import unittest
import time
from unittest.mock import MagicMock

from virtual_machine import VirtualMachine

# We also import the generated modules if we want to craft a ClockMessage
# But for pure unit testing of VirtualMachine logic, we can mock it.
from generated import distributed_system_pb2 as ds_pb2

class TestVirtualMachine(unittest.TestCase):

    def setUp(self):
        """
        Called before each test. We create a VirtualMachine instance 
        with a small dictionary of addresses for local testing.
        """
        all_addresses = {
            0: ("localhost", 50050),
            1: ("localhost", 50051)
        }
        self.vm = VirtualMachine(machine_id=0, all_addresses=all_addresses)
        
        # Prevent the gRPC server from actually starting
        self.vm.server = MagicMock()
        
        # Also mock out stubs so we don't do real network calls
        self.vm.stubs = {
            1: MagicMock()
        }

    def tearDown(self):
        """
        Called after each test. Clean up any resources.
        """
        self.vm.stop_event.set()
        # We won't call vm.stop() here because it might try to close files,
        # but you could if you want to test that logic.

    def test_initial_state(self):
        """
        Test that the VirtualMachine initializes with expected defaults.
        """
        self.assertEqual(self.vm.machine_id, 0)
        self.assertEqual(self.vm.logical_clock, 0)
        self.assertIsNotNone(self.vm.log_file)
        # clock_rate should be between 1 and 6
        self.assertTrue(1 <= self.vm.clock_rate <= 6)

    def test_handle_incoming_message(self):
        """
        Test that an incoming message is placed on the queue.
        """
        msg = ds_pb2.ClockMessage(
            sender_id=1,
            logical_clock=10,
            sender_system_time=time.time(),
            queue_length=0,
            event_type="SEND"
        )
        self.vm.handle_incoming_message(msg)
        self.assertFalse(self.vm.incoming_queue.empty())

    def test_process_incoming_message(self):
        """
        Test that processing a message updates the logical clock correctly.
        """
        msg = ds_pb2.ClockMessage(
            sender_id=1,
            logical_clock=10,
            sender_system_time=time.time(),
            queue_length=0,
            event_type="SEND"
        )
        self.vm.process_incoming_message(msg)
        # local clock = max(local=0, incoming=10) + 1 => 11
        self.assertEqual(self.vm.logical_clock, 11)

    def test_send_message(self):
        """
        Test that sending a message increments local clock and calls the stub.
        """
        old_clock = self.vm.logical_clock
        self.vm.send_message(target_machine_id=1)
        # local clock increments by 1
        self.assertEqual(self.vm.logical_clock, old_clock + 1)
        # check that gRPC stub was called once
        self.vm.stubs[1].SendMessage.assert_called_once()

    def test_internal_event(self):
        """
        We can simulate an 'internal' event by just incrementing the clock.
        """
        old_clock = self.vm.logical_clock
        # Emulate what the event_loop does for internal events
        self.vm.logical_clock += 1
        self.assertEqual(self.vm.logical_clock, old_clock + 1)

    def test_event_loop_with_one_message(self):
        """
        This is a partial test of the event loop. We'll manually enqueue a message,
        run the loop briefly, and ensure it gets processed.
        """
        msg = ds_pb2.ClockMessage(
            sender_id=1,
            logical_clock=5,
            sender_system_time=time.time(),
            queue_length=0,
            event_type="SEND"
        )
        self.vm.incoming_queue.put(msg)

        # We'll run the loop in a thread for a short time
        import threading
        loop_thread = threading.Thread(target=self.vm.event_loop)
        loop_thread.start()

        # Wait a short amount, then signal stop
        time.sleep(0.2)
        self.vm.stop_event.set()
        loop_thread.join()

        # Now logical clock should have updated from processing that message
        # local clock = max(0, 5) + 1 => 6
        self.assertEqual(self.vm.logical_clock, 6)

if __name__ == '__main__':
    unittest.main()
