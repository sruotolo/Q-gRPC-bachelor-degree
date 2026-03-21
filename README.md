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
- they control some of the logic of the Butterfly Protocol such as splitting the keys in half and evaluate the hashes, temporarily save the key to be sure that Client and Server can synchronize on the same key and, after this phase, delete the used keys after both Client and Server had used them or if are not used for a certain amount of time.
The proxies run in the machines hosting the QKD nodes.

## Dependencies and Installation
The project run with **Python 3.x** and a few external libraries are needed. You can install them using `pip`:   
- Flask
- requests
- grpcio
- grpcio-tools
- protobuf
- python-dotenv
- cryptography
- pandas
- matplotlib

## How to run the project
### Step 1: Certificate generation
The system uses a simulated Public Key Infrastructure (PKI) to generate certificates used to create a secure gRPC channel between Client and Server. To generate those certificates:   
**For Linux / macOS:**  
Give the script execution permission and run it:
```bash
chmod +x gen_certs.sh
./gen_certs.sh
```
**For Windows**  
Since the script relies on Bash and OpenSSL, CMD and PowerShell will not work. To run the script use **Git Bash** or **WSL**.  
Note: it will automatically create a directory called _certificates_ and put them there.  
### Step 2: Virtual Environment Setup
It is recommended to use a virtual environment to isolate the project. Remember to create it and activate it:
```bash
# Create the virtual environment
python3 -m venv .venv

# Activate it (Linux/macOS)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate
```
### Step 3: Install Dependencies
With the virtual environment activated, install the packages:
```bash
pip install Flask requests grpcio grpcio-tools protobuf python-dotenv cryptography pandas matplotlib
```
### Step 4: Environment Variable Configuration
The project is designed to run on separate physical hardware so the configuration is divided into two parts.  
1. **Client/Server configuration (in the root directoy)**
   To understand the purpose of every variable read the following table:
   |VARIABLE|DESCRIPTION|
   |--------|-----------|
   |`GLOBAL_SSH_KEY`|Path to ssh key to do the proxy jump|
   |`CA_CERT_PATH`|Path to the simulated local CA certificate|
   |`CLIENT_CERT_PATH`|Path to local client certificate|
   |`CLIENT_KEY_PATH`|Path to local client key|
   |`SERVER_CERT_PATH`|Path to local server certificate|
   |`SERVER_KEY_PATH`|Path to local server key|
   |`SERVER_PORT`|Local port on which the gRPC server listens|
   |`SERVER_ADDRESS`|Local IP or hostname of the gRPC server (ex: 127.0.0.1:50051)|
   |--------|-----------|
   |`[...]_SAE_ID`|ID of the SAE on AIJA/BRENCIS side|
   |`[...]_NEED_TUNNEL`|True if the node needs an SSH tunnel|
   |`[...]_BASTION_IP`|Server bastion ID to access the private network of the QKD|
   |`[...]_BASTION_USER`|SSH username for bastion server|
   |`[...]_REMOTE_IP`|QKD device private ID on the private network|
   |`[...]_LOCAL_PORT`|Local port for the SSH tunnel|
   |`[...]_REMOTE_PORT`|Remote port for the SSH tunnel|
   |`[...]_BASE_URL`|Base url used by the proxy to forward ETSI call (ex: http://127.0.0.1)|
   |`[...]_REMOTE_USER`|SSH username for the remote machine hosting the node|

   Note: replace [...] with teh name of the two nodes (ex: AIJA and BRENCIS).
   
   There is a `.env-example` to copy in the root directory.
   
3. **Proxy Configuration**
   Used for the machine that physically host the QKD nodes.
   |VARIABLE|DESCRIPTION|
   |--------|-----------|
   |`[...]_REAL_IP`|Real IP of the device in private network|
   |`[...]_REAL_PORT`|Port for the ETSI QKD 014 API|
   |`[...]_CERT_PATH`|Path to the device certificate|
   |`[...]_KEY_PATH`|Path to the device key|
   |`[...]_CA_PATH`|Path to the CA certificate|  

   Note: replace [...] with teh name of the two nodes (ex: AIJA and BRENCIS).
   
   There is a `.env-example` to copy in `src/proxy`
### Step 5: Generate gRPC Python Files
Before running the Client and the Server it's needed to compile the Protocol Buffers (`.proto`) in the directory _protos_ to generate Python gRPC classes.  
- **Project structure note**: the directory called _protos_ only contains the source `.proto` file. The compiled python file are generated in a directory called _generated_.
To automatically compile the files and fix the known Python gRPC absolute import bug, give the script execution permission and run it:
```bash
# Only on Linux/macOS
chmod +x codegen.sh
./codegen.sh
```
On Windows, use **Git Bash** or **WSL** to run the script because CMD and PowerShell do not support sed command used in the script to correct gRPC import paths..
### Step 6: Run the Infrastructure
Multiple terminal windows are needed (make sure to activate the `venv`):
1) start the proxies (only because it's a simulation prototype otherwise they will maybe be always ready)
   ```bash
   python3 -m src/aija_proxy
   python3 -m src/brencis_proxy
   ```
   Note: remember that theese proxies are meant to run in the machines hosting the QKD nodes.
2) start the server
   ```bash
   python3 -m src.server.main_server
   ```
3) start the client
   ```bash
   python3 -m src.client.main_client

4) if you want to run the test to get the time results of the execution and to create the stacked bar graphic, instead of using the client main, you have to run the test script
   ```bash
   python3 -m src.custom_test.main_test
   ```
   Note: this script assumes that the directory "benchmark_result" and the CSV file "time_benchmark.csv" are already created in the root directory so make sure you create them before running the script.
