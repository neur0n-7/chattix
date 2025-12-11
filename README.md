# Chattix

![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Socket.io](https://img.shields.io/badge/Socket.io-black?style=for-the-badge&logo=socket.io&badgeColor=010101)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

- Lightweight text-based group chat app made with **Flask** and **Socket.IO**
- Encrypted:
  - Messages are encrypted client-side with AES
  - Server never sees plaintext
  - Rooms are temporary and secure

## Features

- Create or join chat rooms with a room code
- End-to-end encrypted messages (AES + RSA key exchange)

## Setup

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
