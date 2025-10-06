from flask import Flask, request, jsonify
import os, json, hashlib, uuid, time

app = Flask(__name__)

# Simulasi database sederhana (nanti bisa diganti file JSON di storage online)
users = {
    "demo_user": {
        "password": "demo_pass",
        "device_id": None,
        "expires": time.time() + 86400,  # 1 hari aktif
    }
}

def hash_device(device_info):
    return hashlib.sha256(device_info.encode()).hexdigest()

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("user")
    password = data.get("password")
    device_id = hash_device(data.get("device", ""))

    if username not in users:
        return jsonify({"status": "error", "msg": "User tidak ditemukan"})
    user = users[username]

    if user["password"] != password:
        return jsonify({"status": "error", "msg": "Password salah"})
    if user["expires"] < time.time():
        return jsonify({"status": "error", "msg": "Lisensi sudah kadaluarsa"})
    if user["device_id"] and user["device_id"] != device_id:
        return jsonify({"status": "error", "msg": "Lisensi ini hanya untuk 1 device"})
    if not user["device_id"]:
        user["device_id"] = device_id  # lock ke 1 device

    return jsonify({"status": "ok", "msg": "Login berhasil", "user": username})

@app.route("/")
def index():
    return "Indotex License Server aktif ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
