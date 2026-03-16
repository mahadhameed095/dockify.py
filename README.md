# Dockify

Package any Python script into a portable Docker image (.tar) with a single command which can then be deployed.

## The Problem
Deploying Python scripts to Linux VMs from a Windows machine is painful.
PyInstaller executables are platform-dependent. Editing Dockerfiles manually for every script gets old fast.

## What it does
1. Auto-generates a Dockerfile for your script
2. Builds a Linux executable using PyInstaller inside Docker
3. Saves the image as a `.tar` file — ready to ship
```bash
scp image.tar user@vm
docker load -i image.tar
docker run ...
```

## Usage
```bash
python dockify.py script.py
```

## Requirements
- Docker
- Python 3.8+
