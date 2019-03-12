"""NApp that solve the L2 Learning Switch algorithm."""

from kytos.core import KytosEvent, KytosNApp, log
from kytos.core.helpers import listen_to
from pyof.foundation.network_types import Ethernet
# OpenFlow structures that differ will be imported versionwise.
from pyof.v0x01.asynchronous.packet_in import PacketInReason
from pyof.v0x01.common.action import ActionOutput as Output10
from pyof.v0x01.common.phy_port import Port as Port10
from pyof.v0x01.controller2switch.flow_mod import FlowMod as FlowMod10
from pyof.v0x01.controller2switch.flow_mod import FlowModCommand
from pyof.v0x01.controller2switch.packet_out import PacketOut as PacketOut10
from pyof.v0x04.common.action import ActionOutput as Output13
from pyof.v0x04.common.flow_instructions import InstructionApplyAction
from pyof.v0x04.common.flow_match import OxmOfbMatchField, OxmTLV
from pyof.v0x04.common.port import PortNo as Port13
from pyof.v0x04.controller2switch.flow_mod import FlowMod as FlowMod13
from pyof.v0x04.controller2switch.packet_out import PacketOut as PacketOut13

from napps.kytos.of_l2ls import settings


class Main(KytosNApp):
    """Main class of a KytosNApp, responsible for OpenFlow operations."""

    def setup(self):
        """App initialization (used instead of ``__init__``).

        The setup method is automatically called by the run method.
        Users shouldn't call this method directly.
        """

    def execute(self):
        """Run once on app 'start' or in a loop.

        The execute method is called by the run method of KytosNApp class.
        Users shouldn't call this method directly.
        """

    @listen_to('kytos/core.switch.new')
    def install_table_miss_flow(self, event):
        """Install the TableMiss Flow in OF1.3 switches.

        This is needed because those drop packets by default.
        """
        if event.content['switch'].ofp_version == '0x04':
            flow_mod = FlowMod13()
            flow_mod.command = FlowModCommand.OFPFC_ADD

            action = Output13(port=Port13.OFPP_CONTROLLER)

            instruction = InstructionApplyAction()
            instruction.actions.append(action)

            flow_mod.instructions.append(instruction)

            destination = event.content['switch'].connection
            event_out = KytosEvent(name=('kytos/of_l2ls.messages.out.'
                                         'ofpt_flow_mod'),
                                   content={'destination': destination,
                                            'message': flow_mod})
            self.controller.buffers.msg_out.put(event_out)

    @staticmethod
    def _create_flow_mod(version, packet, port):
        """Create a FlowMod message with the appropriate version and data."""
        if version == '0x01':
            flow_mod = FlowMod10()
            flow_mod.match.dl_src = packet.source.value
            flow_mod.match.dl_dst = packet.destination.value
            flow_mod.match.dl_type = packet.ether_type
            flow_mod.actions.append(Output10(port=port))

        else:
            flow_mod = FlowMod13()

            match_dl_type = OxmTLV()
            match_dl_type.oxm_field = OxmOfbMatchField.OFPXMT_OFB_ETH_TYPE
            match_dl_type.oxm_value = packet.ether_type.value.to_bytes(2,
                                                                       'big')
            flow_mod.match.oxm_match_fields.append(match_dl_type)

            match_dl_src = OxmTLV()
            match_dl_src.oxm_field = OxmOfbMatchField.OFPXMT_OFB_ETH_SRC
            match_dl_src.oxm_value = packet.source.pack()
            flow_mod.match.oxm_match_fields.append(match_dl_src)

            match_dl_dst = OxmTLV()
            match_dl_dst.oxm_field = OxmOfbMatchField.OFPXMT_OFB_ETH_DST
            match_dl_dst.oxm_value = packet.destination.pack()
            flow_mod.match.oxm_match_fields.append(match_dl_dst)

            action = Output13(port=port)

            instruction = InstructionApplyAction()
            instruction.actions.append(action)

            flow_mod.instructions.append(instruction)

        flow_mod.command = FlowModCommand.OFPFC_ADD
        flow_mod.priority = settings.FLOW_PRIORITY

        return flow_mod

    @staticmethod
    def _create_packet_out(version, packet, ports):
        """Create a PacketOut message with the appropriate version and data."""
        if version == '0x01':
            packet_out = PacketOut10()
            port = ports[0] if ports else Port10.OFPP_FLOOD
            packet_out.actions.append(Output10(port=port))

        else:
            packet_out = PacketOut13()
            port = ports[0] if ports else Port13.OFPP_FLOOD
            packet_out.actions.append(Output13(port=port))

        packet_out.buffer_id = packet.buffer_id
        packet_out.in_port = packet.in_port
        packet_out.data = packet.data

        return packet_out

    @listen_to('kytos/of_core.v0x0[14].messages.in.ofpt_packet_in')
    def handle_packet_in(self, event):
        """Handle PacketIn Event.

        Install flows allowing communication between switch ports.

        Args:
            event (KytosPacketIn): Received Event
        """
        log.debug("PacketIn Received")

        packet_in = event.content['message']

        ethernet = Ethernet()
        ethernet.unpack(packet_in.data.value)

        # Ignore LLDP packets or packets not generated by table-miss flows
        if (ethernet.destination in settings.LLDP_MACS or
                packet_in.reason != PacketInReason.OFPR_NO_MATCH):
            return

        switch = event.source.switch
        version = switch.ofp_version

        # Learn the port where the sender is connected
        if version == '0x01':
            in_port = packet_in.in_port.value
        else:
            in_port = packet_in.in_port

        switch.update_mac_table(ethernet.source, in_port)

        ports = switch.where_is_mac(ethernet.destination)

        # Add a flow to the switch if the destination is known
        if ports:
            flow_mod = self._create_flow_mod(version, ethernet, ports[0])

            event_out = KytosEvent(name=('kytos/of_l2ls.messages.out.'
                                         'ofpt_flow_mod'),
                                   content={'destination': event.source,
                                            'message': flow_mod})
            self.controller.buffers.msg_out.put(event_out)

        # Send the packet to correct destination or flood it
        packet_out = self._create_packet_out(version, packet_in, ports)

        event_out = KytosEvent(name=('kytos/of_l2ls.messages.out.'
                                     'ofpt_packet_out'),
                               content={'destination': event.source,
                                        'message': packet_out})

        self.controller.buffers.msg_out.put(event_out)

    def shutdown(self):
        """Too simple to have a shutdown procedure."""
