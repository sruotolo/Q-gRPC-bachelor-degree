# QKD as a Service - Butterfly Protocol Implementation

## About this project
This project provides a simple prototype Python implementation of the **Butterfly Protocol** to deliver Quantum Key Distribution as a Service (QaaS).  
The goal is to allow a Client and a Server to talk (but not like a chat: the Client send a message and the Server answer and the connection ends) using a shared quantum key without needing a direct connection to the QKD hardware.
The system uses two Key Distribution Center (KDC), named **Aija** and **Brencis** (theese names are just a convention), and each one send half of the quantum key and the hash of the other half. Doing this, the full key 
is never transmitted on the communication channel.  
REST APIs are used to interface with ETSI QKD 014 standard and gRPC is used for the communication between the Client and the Server.  

## Role of the Proxies
Thinking about a real scenario, the QKD devices are very strict with security measures and are often protected with private network that are not directly accessible from the outside. The system uses two Flask Proxies
(one for Aija and one for Brencis) with two main purposes:
- they securely tunnel the REST API coming from the external network to the private QKD;
- they control some of the logic of the Butterfly Protocol such as splitting the keys in half and evaluate the hashes, temporarily save the key to be sure that Client and Server can synchronize on the same key and, after this phase,
  delete the used keys after both Client and Server had used them or if are not used for a certain amount of time.

## Dependencies and Installation
The project run with **Python 3.x** and a few external libraries are needed. You can install them using `pip`:   
- Flask
- requests
- grpc
- protobuf
- python-dotenv
- cryptography

## How to run the project
### Step 1: Certificate generation
The system uses a simulated Public Key Infrastructure (PKI) to generate certificates used to create a secure gRPC channel between Client and Server. To generate those certificates, use
```bash
./gen_certs.sh
```
that will automatically create a directory called _certificates_ and put them there (wornking only with unix-like systems).  
On Linux system you have to give to the script permission for execution.  
### Step 2: Virtual Environment Setup
It is recommended to use a virtual environment to isolate the project. Remember to create it and activate it:
```bash
# Create the virtual environment
python3 -m venv venv

# Activate it (Linux/macOS)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```
### Step 3: Install Dependencies
With the virtual environment activated, install the packages:
```bash
pip install Flask requests grpcio grpcio-tools protobuf python-dotenv cryptography
```
### Step 4: Generate gRPC Python Files
Before running the Client and the Server it's needed to compile the Protocol Buffers (`.proto`) in the directory _protos_ to generate Python gRPC classes. The command is (replace _file.proto_ with your proto file):
```bash
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. file.proto
```
You can also use (only in unix-like systems):
```bash
./codegen.sh
```
that will generate the files in a directory called _generated_.
### Step 5: Run the Infrastructure
Multiple terminal windows are needed (make sure to activate the `venv`):
1) start the proxies (only because it's a simulation prototype otherwise they will maybe be always ready)
   ```bash
   python3 src/aija_proxy.py
   python3 src/brencis_proxy.py
   ```
   (the names are just for examples)
2) start the server
   ```bash
   python3 src/server
   ```
3) start the client
   ```bash
   python3 src/client
