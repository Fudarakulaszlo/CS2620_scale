import argparse
import time
import threading

from virtual_machine import VirtualMachine

def main():
    """
    Orchestrate the creation and operation of multiple VirtualMachine instances.
    """

    # 1. Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Run a small asynchronous distributed system simulation with multiple VMs."
    )
    parser.add_argument(
        "--num_machines",
        type=int,
        default=3,
        help="Number of virtual machines to spawn."
    )
    parser.add_argument(
        "--base_port",
        type=int,
        default=50050,
        help="Base port number. Each machine gets base_port + machine_id."
    )
    parser.add_argument(
        "--run_duration",
        type=int,
        default=60,
        help="Number of seconds to let the machines run before stopping."
    )
    args = parser.parse_args()

    num_machines = args.num_machines
    base_port = args.base_port
    run_duration = args.run_duration

    # 2. Build a dictionary of all addresses { machine_id: (host, port), ... }
    #    We'll assume "localhost" for simplicity, but we could change to actual IPs.
    all_addresses = {
        i: ("localhost", base_port + i)
        for i in range(num_machines)
    }

    # 3. Create VirtualMachine instances
    machines = []
    for i in range(num_machines):
        vm = VirtualMachine(machine_id=i, all_addresses=all_addresses)
        machines.append(vm)

    # 4. Start each machine's gRPC server
    for vm in machines:
        vm.start_server()

    # 5. Establish connections (stubs) to other machines
    for vm in machines:
        vm.connect_to_others()

    # 6. Start the event loop for each machine in its own thread
    threads = []
    for vm in machines:
        t = threading.Thread(target=vm.event_loop, daemon=True)
        t.start()
        threads.append(t)

    print(f"All virtual machines are running. Let them run for {run_duration} seconds.")
    time.sleep(run_duration)

    # 7. Stop all machines after the run duration
    print("Stopping all machines...")
    for vm in machines:
        vm.stop()

    # 8. Wait for threads to finish
    for t in threads:
        t.join()

    print("All machines stopped. Exiting.")

if __name__ == "__main__":
    main()
