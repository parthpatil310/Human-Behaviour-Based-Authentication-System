from flask import Flask, request, jsonify, render_template
import sqlite3, random, smtplib
from email.mime.text import MIMEText
import bcrypt   # 🔥 ADDED

app = Flask(__name__)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT,
        password TEXT,
        secret TEXT,
        answer TEXT,
        typing_speed REAL,
        typing_gap REAL,
        hold_time REAL,
        mouse_speed REAL,
        clicks INT,
        latitude REAL,
        longitude REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- EMAIL ----------------
def send_email_otp(receiver_email, otp):
    try:
        sender_email = "newgensolution1@gmail.com"
        app_password = "ldpirqtivalrpcmb"

        msg = MIMEText(f"Your OTP is {otp}")
        msg["Subject"] = "OTP Verification"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()

        print("OTP sent:", otp)

    except Exception as e:
        print("Email Error:", e)

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register")
def reg():
    return render_template("register.html")

@app.route("/dashboard")
def dash():
    return render_template("dashboard.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        print("REGISTER DATA:", data)

        # 🔐 HASH PASSWORD
        hashed_password = bcrypt.hashpw(
            data.get("password").encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO users (
            email, password, secret, answer,
            typing_speed, typing_gap, hold_time,
            mouse_speed, clicks, latitude, longitude
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            str(data.get("email")),
            hashed_password,   # 🔥 CHANGED
            str(data.get("secret")),
            str(data.get("answer")).lower(),
            float(data.get("typing_speed", 0)),
            float(data.get("typing_gap", 0)),
            float(data.get("hold_time", 0)),
            float(data.get("mouse_speed", 0)),
            int(data.get("clicks", 0)),
            float(data.get("lat", 0)),
            float(data.get("lon", 0))
        ))

        conn.commit()
        conn.close()

        return jsonify({"message": "Registered Successfully"})

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"error": str(e)})

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True)

        email = data["email"]
        password = data["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        user = cur.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if not user:
            return jsonify({"error": "User not found"})

        # 🔐 VERIFY PASSWORD USING BCRYPT
        if not bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            return jsonify({"error": "Wrong password ❌"})

        # -------- STORED --------
        stored_speed = float(user[4])
        stored_gap   = float(user[5])
        stored_hold  = float(user[6])
        stored_mouse = float(user[7])

        # -------- CURRENT --------
        current_speed = float(data.get("typing_speed",0))
        current_gap   = float(data.get("typing_gap",0))
        current_hold  = float(data.get("hold_time",0))
        current_mouse = float(data.get("mouse_speed",0))

        # -------- HARD RULE --------
        if current_speed < stored_speed * 0.4:
            return jsonify({"error": "Access Denied ❌ (Typing abnormal)"})

        # -------- SCORES --------
        typing_score = max(0, 100 - abs(stored_speed - current_speed) * 20)
        gap_score    = max(0, 100 - abs(stored_gap - current_gap) * 0.5)
        hold_score   = max(0, 100 - abs(stored_hold - current_hold) * 0.5)
        mouse_score  = max(0, 100 - abs(stored_mouse - current_mouse) * 50)

        trust = int(
            typing_score * 0.3 +
            gap_score * 0.2 +
            hold_score * 0.2 +
            mouse_score * 0.3
        )

        trust = max(0, min(100, trust))

        print("Trust:", trust)

        # -------- FLOW --------
        if trust >= 75:
            return jsonify({"status": "success", "trust": trust})

        elif 50 <= trust < 75:
            return jsonify({
                "status": "verify",
                "question": user[2],
                "trust": trust
            })

        else:
            return jsonify({"error": "Access Denied ❌ (High Risk)"})

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": "Login failed"}), 500

# ---------------- VERIFY ----------------
@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json(force=True)

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    user = cur.execute("SELECT answer FROM users WHERE email=?", (data["email"],)).fetchone()
    conn.close()

    if user and user[0] == data["answer"].lower():
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "otp"})

# ---------------- OTP ----------------
otp_store = {}

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json(force=True)
    otp = str(random.randint(1000,9999))

    otp_store[data["email"]] = otp
    send_email_otp(data["email"], otp)

    return jsonify({"message": "OTP sent"})

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json(force=True)

    if otp_store.get(data["email"]) == data["otp"]:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failed"})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)