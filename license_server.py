from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# Contoh database sementara (bisa diganti ke database permanen)
users = {
    "demo": {
        "password": "1234",
        "devices": {},
        "max_devices": 1,
        "expires": "2025-12-31"
    }
}

@app.route("/")
def home():
    return "✅ Indotex License Server aktif"

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    device_id = data.get("device_id")

    if not username or not password or not device_id:
        return jsonify({"status": "error", "message": "Data tidak lengkap"}), 400

    user = users.get(username)
    if not user or user["password"] != password:
        return jsonify({"status": "error", "message": "User atau password salah"}), 401

    # Cek masa aktif
    if datetime.now() > datetime.strptime(user["expires"], "%Y-%m-%d"):
        return jsonify({"status": "error", "message": "Lisensi sudah kedaluwarsa"}), 403

    # Cek device ID
    devices = user["devices"]
    if device_id in devices:
        return jsonify({"status": "ok", "message": "Login sukses", "license": user})
    elif len(devices) < user["max_devices"]:
        devices[device_id] = {"activated": str(datetime.now())}
        return jsonify({"status": "ok", "message": "Perangkat baru terdaftar", "license": user})
    else:
        return jsonify({"status": "error", "message": "Batas perangkat tercapai"}), 403

@app.route("/admin/users", methods=["GET"])
def list_users():
    return jsonify(users)

@app.route("/admin/create", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    expires = data.get("expires", "2025-12-31")
    max_devices = int(data.get("max_devices", 1))
    if username in users:
        return jsonify({"status": "error", "message": "User sudah ada"}), 400
    users[username] = {"password": password, "devices": {}, "max_devices": max_devices, "expires": expires}
    return jsonify({"status": "ok", "message": f"User {username} dibuat"})

@app.route("/admin/delete/<username>", methods=["DELETE"])
def delete_user(username):
    if username in users:
        del users[username]
        return jsonify({"status": "ok", "message": f"User {username} dihapus"})
    return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
