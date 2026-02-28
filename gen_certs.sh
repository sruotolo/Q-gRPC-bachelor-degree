#!/bin/bash
mkdir -p certificates
cd certificates || exit

echo "--- 1. Certification Authority Generation ---"
openssl req -new -x509 -days 365 -nodes -out ca.crt -keyout ca.key -subj "/CN=Q-gRPC-Authority"

echo "--- 2. Certificate generation: SERVER with SAN ---"
# Server key.
openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.csr -subj "/CN=Q-gRPC-Server"

# We use a temporary configuration file to add the SAN, making the certificates valid for 'localhost' and '127.0.0.1'.
cat > server.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
EOF

# Sign the certificate using the configuration file.
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
-out server.crt -days 365 \
-extfile server.ext

echo "--- 3. Certificate Generation: CLIENT ---"
openssl req -new -newkey rsa:2048 -nodes -keyout client.key -out client.csr -subj "/CN=Q-gRPC-Client"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365

# Delete temporary files.
rm server.csr client.csr server.ext

echo "--- DONE ---"
echo "Certificates generated in /certificates with SAN support"



