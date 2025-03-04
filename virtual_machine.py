import time
import random
import queue
import threading
from concurrent import futures

import grpc

# Import the generated gRPC code (adjust paths if needed)
from generated import distributed_system_pb2 as ds_pb2
from generated import distributed_system_pb2_grpc as ds_pb2_grpc


class DistributedSystemServicer(ds_pb2_grpc.DistributedSystemServicer):
    """
    This class implements the service defined in distributed_system.proto.
    Each VirtualMachine will have an instance of this servicer to handle incoming RPCs.
    """

    def __init__(self, virtual_machine):
        # Keep a reference to the parent VirtualMachine so we can update its state
        self.virtual_machine = virtual_machine

    def SendMessage(self, request, context):
        """
        Handler for the SendMessage RPC call.
        request: ClockMessage (as defined in distributed_system.proto)
        returns: Ack
        """
        # Put the message in the VM's queue (or handle it immediately)
        self.virtual_machine.handle_incoming_message(request)

        # Return an acknowledgment. You can customize the status string as needed.
        return ds_pb2.Ack(status="OK")


class VirtualMachine:
    """
    A class modeling a single 'virtual machine' in the distributed system.
    Each instance:
      - Runs its own gRPC server
      - Maintains a logical clock
      - Processes a queue of incoming messages
      - Sends messages to other machines at a rate determined by its random clock speed
      - Logs events to a dedicated logfile
    """

    def __init__(self, machine_id, all_addresses):
        """
        :param machine_id: (int) Unique identifier for this virtual machine
        :param all_addresses: (dict) {vm_id: (host, port), ...} for all machines
        """
        self.machine_id = machine_id
        self.all_addresses = all_addresses  # Info needed to connect to other VMs

        # Local logical clock
        self.logical_clock = 0

        # A queue to store incoming messages (as ClockMessage objects)
        self.incoming_queue = queue.Queue()

        # Random clock rate in [1,6] ticks per second
        self.clock_rate = random.randint(1, 6)

        # Flag to stop the main loop
        self.stop_event = threading.Event()

        # Create a gRPC server
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))

        # Create and register our servicer
        self.servicer = DistributedSystemServicer(self)
        ds_pb2_grpc.add_DistributedSystemServicer_to_server(
            self.servicer,
            self.server
        )

        # Create stubs (for calling SendMessage on other VMs). We'll fill this after we start servers.
        self.stubs = {}

        # Open a log file. E.g., "machine_0.log", "machine_1.log", etc.
        self.log_file = open(f"machine_{machine_id}.log", "w")

    def start_server(self):
        """
        Start the gRPC server on the designated (host, port) for this machine.
        """
        host, port = self.all_addresses[self.machine_id]
        self.server.add_insecure_port(f"{host}:{port}")
        self.server.start()
        print(f"[Machine {self.machine_id}] gRPC server started on {host}:{port}")

    def connect_to_others(self):
        """
        Create gRPC channels and stubs for calling the 'SendMessage' RPC on other VMs.
        """
        for mid, (host, port) in self.all_addresses.items():
            if mid != self.machine_id:
                channel = grpc.insecure_channel(f"{host}:{port}")
                stub = ds_pb2_grpc.DistributedSystemStub(channel)
                self.stubs[mid] = stub
        print(f"[Machine {self.machine_id}] Connected to other machines' stubs.")

    def stop(self):
        """
        Signal the event loop to stop and shutdown the gRPC server.
        """
        self.stop_event.set()
        self.server.stop(0)  # Immediately stop the server
        self.log_file.close()
        print(f"[Machine {self.machine_id}] Stopped.")

    def handle_incoming_message(self, request):
        """
        Handles an incoming ClockMessage from another VM.
        For now, we push it into an internal queue to be processed in the event loop.
        """
        self.incoming_queue.put(request)

    def process_incoming_message(self, clock_msg):
        """
        Process a message taken from the queue, update local clock, and log.
        """
        # 1. Update local logical clock: clock = max(local, incoming) + 1
        incoming_ts = clock_msg.logical_clock
        self.logical_clock = max(self.logical_clock, incoming_ts) + 1

        # 2. Log the RECEIVED event
        system_time = time.time()
        self.log_event(
            event_type="RECEIVE",
            system_time=system_time,
            queue_length=self.incoming_queue.qsize()
        )

    def send_message(self, target_machine_id, event_type="SEND"):
        """
        Send a ClockMessage to the given target machine using the corresponding stub.
        Also increments the local clock first (per send event rules).
        """
        # Increment local clock
        self.logical_clock += 1

        # Log the SEND event
        system_time = time.time()
        self.log_event(
            event_type=event_type,
            system_time=system_time,
            queue_length=self.incoming_queue.qsize()
        )

        # Construct the ClockMessage
        clock_msg = ds_pb2.ClockMessage(
            sender_id=self.machine_id,
            logical_clock=self.logical_clock,
            sender_system_time=system_time,
            queue_length=self.incoming_queue.qsize(),
            event_type=event_type  # "SEND", "INTERNAL", etc.
        )

        # Make the gRPC call
        self.stubs[target_machine_id].SendMessage(clock_msg)

    def log_event(self, event_type, system_time, queue_length):
        """
        Write a line to our local log file. This can be extended with more data.
        """
        log_line = (f"{event_type}, system_time={system_time:.6f}, "
                    f"queue_length={queue_length}, "
                    f"logical_clock={self.logical_clock}\n")
        self.log_file.write(log_line)
        self.log_file.flush()

    def event_loop(self):
        """
        Main loop, driven by the clock_rate. Each iteration:
          - Sleeps for 1 / clock_rate seconds
          - Checks for incoming messages (and processes one if available)
          - Otherwise, picks a random 1–10 for the event type (SEND, INTERNAL, etc.)
        """
        print(f"[Machine {self.machine_id}] Starting event loop with clock_rate={self.clock_rate}.")
        while not self.stop_event.is_set():
            time.sleep(1 / self.clock_rate)

            # If there's a message in the incoming queue, process it
            if not self.incoming_queue.empty():
                msg = self.incoming_queue.get()
                self.process_incoming_message(msg)
            else:
                # No message to process => decide next action
                val = random.randint(1, 10)
                if val == 1:
                    # Send to ONE other machine
                    target = self.pick_random_other()
                    if target is not None:
                        self.send_message(target, event_type="SEND")
                elif val == 2:
                    # Send to ONE other machine (like above, or pick different logic)
                    target = self.pick_random_other()
                    if target is not None:
                        self.send_message(target, event_type="SEND")
                elif val == 3:
                    # Send to ALL others
                    for t_id in self.stubs.keys():
                        self.send_message(t_id, event_type="SEND")
                else:
                    # Internal event: just increment local clock, log, no send
                    self.logical_clock += 1
                    system_time = time.time()
                    self.log_event(
                        event_type="INTERNAL",
                        system_time=system_time,
                        queue_length=self.incoming_queue.qsize()
                    )

    def pick_random_other(self):
        """
        Return a random machine ID (stub) from the list of other machines, or None if empty.
        """
        other_ids = list(self.stubs.keys())  # All except self
        return random.choice(other_ids) if other_ids else None
