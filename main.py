import os
import random
import string
import base64
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# room data lives here while server runs
# {
#   "ROOMCODE": {
#       "members": { socket_ids... },
#       "aes_key": b"...",  # raw 32 byte key
#       "messages": [ "<json payloads>" ]
#   }
# }
rooms = {}


def generate_room_code(length=6):
    # makes random uppercase+digit code that isn’t taken
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if code not in rooms:
            return code


@app.route("/", methods=["GET", "POST"])
def home():
    # home page, join/create form
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username:
            return "username required", 400

        session["username"] = username
        action = request.form.get("action")

        if action == "create":
            room_code = generate_room_code()
            rooms[room_code] = {
                "members": set(),
                "aes_key": os.urandom(32),
                "messages": []
            }
            return redirect(url_for("chat", room_code=room_code))

        elif action == "join":
            room_code = request.form.get("room_code", "").upper().strip()
            if room_code in rooms:
                return redirect(url_for("chat", room_code=room_code))
            return render_template("index.html", error="room not found")

    return render_template("index.html")


@app.route("/chat/<room_code>")
def chat(room_code):
    # main chat page
    if "username" not in session:
        return redirect(url_for("home"))

    if room_code not in rooms:
        return redirect(url_for("home"))

    return render_template("chat.html",
                           room_code=room_code,
                           username=session["username"])


##################################################################
# Socket stuff
##################################################################

@socketio.on("join")
def handle_join(data):
    room = data.get("room")
    if not room or room not in rooms:
        return

    join_room(room)
    rooms[room]["members"].add(request.sid)

    # send all past encrypted msgs to user who just joined room
    for msg in rooms[room]["messages"]:
        emit("message", msg, to=request.sid)

    emit("status",
         f"{session.get('username', 'anon')} joined the room.",
         room=room)


@socketio.on("register_key")
def handle_register_key(data):
    # client sends rsa pubkey, server returns aes key encrypted wit it
    room = data.get("room")
    pub_b64 = data.get("public_key")

    if not room or room not in rooms or not pub_b64:
        return

    try:
        pub_der = base64.b64decode(pub_b64)
        pubkey = serialization.load_der_public_key(pub_der)
        aes_key = rooms[room]["aes_key"]

        enc = pubkey.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        enc_b64 = base64.b64encode(enc).decode()
        emit("encrypted_key", {"enc_key": enc_b64}, to=request.sid)

    except Exception as e:
        print(f"[err] register_key failed: {e}")


@socketio.on("message")
def handle_message(data):
    # gets ciphertext payload, stores & sends to room
    room = data.get("room")
    payload = data.get("payload")

    if not room or room not in rooms or not payload:
        return

    rooms[room]["messages"].append(payload)
    emit("message", payload, room=room)


@socketio.on("leave")
def handle_leave(data):
    room = data.get("room")
    if not room or room not in rooms:
        return

    leave_room(room)
    rooms[room]["members"].discard(request.sid)

    emit("status",
         f"{session.get('username', 'anon')} left the room.",
         room=room)

    # drop empty rooms
    if not rooms[room]["members"]:
        del rooms[room]


@socketio.on("disconnect")
def handle_disconnect():
    # remove disconnected users
    for code, info in list(rooms.items()):
        if request.sid in info["members"]:
            info["members"].discard(request.sid)
            emit("status", "a user disconnected.", room=code)

            if not info["members"]:
                del rooms[code]


if __name__ == "__main__":
    print("[INFO] Starting Chattix...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
