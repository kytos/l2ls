"""Test Main methods."""
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from kytos.lib.helpers import (get_controller_mock, get_kytos_event_mock,
                               get_switch_mock)


# pylint: disable=protected-access
class TestMain(TestCase):
    """Tests for the Main class."""

    def setUp(self):
        """Execute steps before each tests."""
        patch('kytos.core.helpers.run_on_thread', lambda x: x).start()
        from napps.kytos.of_l2ls.main import Main
        self.addCleanup(patch.stopall)

        self.napp = Main(get_controller_mock())

    @patch('kytos.core.buffers.KytosEventBuffer.put')
    @patch('napps.kytos.of_l2ls.main.KytosEvent')
    @patch('napps.kytos.of_l2ls.main.InstructionApplyAction')
    @patch('napps.kytos.of_l2ls.main.Output13')
    @patch('napps.kytos.of_l2ls.main.FlowMod13')
    def test_install_table_miss_flow(self, *args):
        """Test install_table_miss_flow method."""
        (mock_flow_mod, mock_action, mock_instruction, mock_kytos_event,
         mock_buffer_put) = args

        kytos_event = MagicMock()

        mock_flow_mod.return_value = MagicMock()
        mock_action.return_value = MagicMock()
        mock_instruction.return_value = MagicMock()
        mock_kytos_event.return_value = kytos_event

        switch = get_switch_mock("00:00:00:00:00:00:00:01", 0x04)
        event = get_kytos_event_mock(name='kytos/core.switch.new',
                                     content={'switch': switch})
        self.napp.install_table_miss_flow(event)

        mock_flow_mod.assert_called()
        mock_action.assert_called()
        mock_instruction.assert_called()
        mock_kytos_event.assert_called()
        mock_buffer_put.assert_called_with(kytos_event)

    @patch('napps.kytos.of_l2ls.main.Output10')
    @patch('napps.kytos.of_l2ls.main.FlowMod10')
    def test_create_flow_mod_10(self, *args):
        """Test _create_flow_mod method for flow_mod 1.0 packet."""
        (mock_flow_mod, mock_action) = args

        flow_mod = MagicMock()
        flow_mod.actions = []
        action = MagicMock()

        mock_flow_mod.return_value = flow_mod
        mock_action.return_value = action

        packet = MagicMock()
        packet.source.value = '00:00:00:00:00:00:00:01'
        packet.destination.value = '00:00:00:00:00:00:00:02'
        packet.ether_type = 0x800
        flow_mod_out = self.napp._create_flow_mod('0x01', packet, 1)

        mock_flow_mod.assert_called()
        mock_action.assert_called()
        self.assertEqual(flow_mod_out.actions[0], action)
        self.assertEqual(flow_mod_out.match.dl_src, packet.source.value)
        self.assertEqual(flow_mod_out.match.dl_dst, packet.destination.value)
        self.assertEqual(flow_mod_out.match.dl_type, packet.ether_type)
        self.assertEqual(flow_mod_out.command, 0)
        self.assertEqual(flow_mod_out.priority, 10)

    @patch('napps.kytos.of_l2ls.main.InstructionApplyAction')
    @patch('napps.kytos.of_l2ls.main.Output13')
    @patch('napps.kytos.of_l2ls.main.OxmTLV')
    @patch('napps.kytos.of_l2ls.main.FlowMod13')
    def test_create_flow_mod_13(self, *args):
        """Test _create_flow_mod method for flow_mod 1.3 packet."""
        (mock_flow_mod, mock_oxm_tlv, mock_action, mock_instruction) = args

        flow_mod = MagicMock()
        flow_mod.match.oxm_match_fields = []
        flow_mod.instructions = []
        instruction = MagicMock()

        match_dl_type = MagicMock()
        match_dl_type.oxm_field = 5
        match_dl_type.oxm_value = 'ether_type'

        match_dl_src = MagicMock()
        match_dl_src.oxm_field = 4
        match_dl_src.oxm_value = 'source'

        match_dl_dst = MagicMock()
        match_dl_dst.oxm_field = 3
        match_dl_dst.oxm_value = 'destination'

        oxm_tlvs = [match_dl_type, match_dl_src, match_dl_dst]

        mock_flow_mod.return_value = flow_mod
        mock_action.return_value = MagicMock()
        mock_instruction.return_value = instruction
        mock_oxm_tlv.side_effect = oxm_tlvs

        flow_mod_out = self.napp._create_flow_mod('0x04', MagicMock(), 2)

        mock_flow_mod.assert_called()
        mock_oxm_tlv.assert_called()
        mock_action.assert_called()
        mock_instruction.assert_called()
        self.assertEqual(flow_mod.match.oxm_match_fields, oxm_tlvs)
        self.assertEqual(flow_mod.instructions[0], instruction)
        self.assertEqual(flow_mod_out.command, 0)
        self.assertEqual(flow_mod_out.priority, 10)

    @patch('napps.kytos.of_l2ls.main.Output10')
    @patch('napps.kytos.of_l2ls.main.PacketOut10')
    def test_create_packet_out_10(self, *args):
        """Test _create_packet_out method for packet_out 1.0 packet."""
        (mock_packet_out, mock_action) = args

        packet_out = MagicMock()
        packet_out.actions = []
        action = MagicMock()

        mock_packet_out.return_value = packet_out
        mock_action.return_value = action

        packet = MagicMock()
        packet.buffer_id = 1
        packet.in_port = 1
        packet.data = '1'
        packet_out = self.napp._create_packet_out('0x01', packet, [])

        mock_packet_out.assert_called()
        mock_action.assert_called()
        self.assertEqual(packet_out.actions[0], action)
        self.assertEqual(packet_out.buffer_id, packet.buffer_id)
        self.assertEqual(packet_out.in_port, packet.in_port)
        self.assertEqual(packet_out.data, packet.data)

    @patch('napps.kytos.of_l2ls.main.Output13')
    @patch('napps.kytos.of_l2ls.main.PacketOut13')
    def test_create_packet_out_13(self, *args):
        """Test _get_lldp_interfaces method for packet_out 1.3 packet."""
        (mock_packet_out, mock_action) = args

        packet_out = MagicMock()
        packet_out.actions = []
        action = MagicMock()

        mock_packet_out.return_value = packet_out
        mock_action.return_value = action

        packet = MagicMock()
        packet.buffer_id = 2
        packet.in_port = 2
        packet.data = '2'
        packet_out = self.napp._create_packet_out('0x04', packet, [])

        mock_packet_out.assert_called()
        mock_action.assert_called()
        self.assertEqual(packet_out.actions[0], action)
        self.assertEqual(packet_out.buffer_id, packet.buffer_id)
        self.assertEqual(packet_out.in_port, packet.in_port)
        self.assertEqual(packet_out.data, packet.data)

    @patch('kytos.core.buffers.KytosEventBuffer.put')
    @patch('napps.kytos.of_l2ls.main.Main._create_packet_out')
    @patch('napps.kytos.of_l2ls.main.Main._create_flow_mod')
    @patch('napps.kytos.of_l2ls.main.KytosEvent')
    @patch('napps.kytos.of_l2ls.main.Ethernet')
    def test_handle_packet_in(self, *args):
        """Test handle_packet_in method."""
        (mock_ethernet, mock_kytos_event, mock_create_flow_mod,
         mock_create_packet_out, mock_buffer_put) = args

        switch = get_switch_mock("00:00:00:00:00:00:00:01", 0x04)
        ports = [1, 2]

        ethernet = MagicMock()
        ethernet.source = 'sw'
        kevent_01 = MagicMock()
        kevent_02 = MagicMock()

        switch.where_is_mac.return_value = ports
        mock_ethernet.return_value = ethernet
        mock_create_flow_mod.return_value = MagicMock()
        mock_create_packet_out.return_value = MagicMock()
        mock_kytos_event.side_effect = [kevent_01, kevent_02]

        event_name = 'kytos/of_core.v0x0[14].messages.in.ofpt_packet_in'
        message = MagicMock()
        message.reason = 0
        message.in_port = 1
        event = get_kytos_event_mock(name=event_name,
                                     content={'source': switch.connection,
                                              'message': message})

        self.napp.handle_packet_in(event)

        mock_ethernet.assert_called()
        switch.update_mac_table.assert_called_with(ethernet.source,
                                                   message.in_port)
        mock_create_flow_mod.assert_called_with(switch.ofp_version,
                                                ethernet, ports[0])
        mock_create_packet_out.assert_called_with(switch.ofp_version,
                                                  message, ports)
        mock_buffer_put.assert_has_calls([call(kevent_01), call(kevent_02)])
