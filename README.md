# CS2620 Scale Models and Logical Clocks HW

## Overview

This project is a **small, asynchronous distributed system** simulation that uses **gRPC** for communication. Each “virtual machine”:

- Maintains a **logical clock**.  
- Sends and receives messages to/from other VMs.  
- Logs events (SEND, RECEIVE, INTERNAL) to a local log file.  
- Operates at a **random clock rate** chosen at initialization.  
- Uses [Lamport Logical Clock](https://en.wikipedia.org/wiki/Lamport_timestamps) rules to update its clock.

All VMs run on a **single physical machine** but simulate distributed behavior through concurrent gRPC servers and clients.

---

## File Structure
```
CS2620_scale/
├── main.py
├── virtual_machine.py
├── distributed_system.proto
├── notebook.txt
├── requirements.txt
└── generated/
    ├── distributed_system_pb2.py
    └── distributed_system_pb2_grpc.py
```

1. **distributed_system.proto**  
   - Defines the gRPC service (`DistributedSystem`) and the messages (`ClockMessage`, `Ack`).
   - You run `protoc` (via `grpc_tools`) to generate the Python gRPC modules.

2. **generated/**  
   - Contains the auto-generated Python files from `distributed_system.proto`:
     - `distributed_system_pb2.py`
     - `distributed_system_pb2_grpc.py`
   - These are **imported** by `virtual_machine.py` to implement the RPC service and create stubs for sending messages.

3. **virtual_machine.py**  
   - Defines the `VirtualMachine` class:
     - **Starts a gRPC server** (so this VM can receive `SendMessage` calls).  
     - Maintains a **logical clock**, a **message queue**, and a **random clock rate**.  
     - Implements the main **event loop** that periodically checks for incoming messages or decides to send a message or do an internal event.  
     - Logs all events to a file named `machine_<id>.log`.

4. **main.py**  
   - The **orchestrator** script:
     - Creates multiple `VirtualMachine` instances.  
     - Starts each machine’s gRPC server.  
     - Connects the machines to each other (via gRPC stubs).  
     - Spawns threads for each VM’s event loop.  
     - Lets them run for a specified duration.  
     - Shuts everything down gracefully.

5. **notebook.txt**  
   - Engineering notebook

6. **README.md**  
   - This documentation file, explaining the overall setup and usage.

7. **requirements.txt**  
   - Lists Python packages required to run this system.

---

## Installation & Setup

1. **Clone** this repository (or copy the files into your working directory).

2. **Install** required libraries:
   ```bash
   pip install -r requirements.txt

3. **Generate** the gRPC Python files if you haven't already
    ```bash
    python -m grpc_tools.protoc \
        --proto_path=. \
        --python_out=generated \
        --grpc_python_out=generated \
        distributed_system.proto

## How to Run

1. **Confirm** the gRPC stubs (`distributed_system_pb2.py`, `distributed_system_pb2_grpc.py`) are present in the `generated/` folder.

2. **Launch** the system:

   ```bash
   python main.py --num_machines 3 --base_port 50050 --run_duration 60


## Command-line Arguments

- `--num_machines`: Number of VMs to spawn (default: `3`).
- `--base_port`: Base port; each machine gets `base_port + machine_id` (default: `50050`).
- `--run_duration`: How long (in seconds) to run before stopping (default: `60`).

## Observing Logs

- Each machine writes logs to `machine_<id>.log`.
- Look for lines indicating:
  - `RECEIVE`, `SEND`, and `INTERNAL` events.
  - Associated timestamps and logical clock values.
