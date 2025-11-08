# Chattix

- Lightweight text-based group chat app made with **Flask** and **Socket.IO**
- Encrypted:
  - Messages are encrypted client-side with AES
  - Server never sees plaintext
  - Rooms are temporary and secure

## Features

- Create or join chat rooms with a room code
- End-to-end encrypted messages (AES + RSA key exchange)

## Setup

### Requirements

- Python 3.8+
- Flask
- Flask-SocketIO
- cryptography

### Install

```bash
# Clone repository
git clone https://github.com/your-username/chattix.git
cd chattix
# Install requirements
pip install -r requirements.txt
```

Then, to run:

```bash
python main.py
```
