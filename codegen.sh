#!/bin/bash

# Enable the venv automatically (if it exists).
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "ATTENTION: Can't find the venv, using system Python"
fi

# Create the folder for the files to be generated (if it does not already exist).
# The __init__.py file is used to treat the generated folder as a package.
mkdir -p generated
touch generated/__init__.py

echo "Generating python files..."

# Generate Python files from proto files (the * is used to use all proto files).
python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./generated \
    --grpc_python_out=./generated \
    --mypy_out=./generated \
    --mypy_grpc_out=./generated \
    ./protos/*.proto

echo "Done."