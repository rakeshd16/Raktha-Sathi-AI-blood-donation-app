import math
import os
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import mysql.connector
import numpy as np
import pandas as pd
from joblib import load

# -----------------------
# Get the directory where app.py is located
# -----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'template')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# -----------------------
# Email & SMS setup
# -----------------------
from send_email import send_email as send_email_alert
from send_sms import send_sms as send_sms_alert

# -----------------------
# Chatbot setup
# -----------------------
try:
    from chatbot_helper import get_bot_reply
    CHATBOT_AVAILABLE = True
except Exception:
    CHATBOT_AVAILABLE = False

# -----------------------
# Database Config
# -----------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": "rakth_sathi",
    "auth_plugin": "mysql_native_password"
}

# -----------------------
# Optional ML models (for smart matching)
# -----------------------
TREE_FILE = os.path.join("models", "tree_matcher.joblib")
LOGREG_FILE = os.path.join("models", "logreg_matcher.joblib")

tree, logreg = None, None
try:
    if os.path.exists(TREE_FILE):
        tree = load(TREE_FILE)
    if os.path.exists(LOGREG_FILE):
        logreg = load(LOGREG_FILE)
except Exception as e:
    print(f"⚠️ Could not load models: {e}")

# -----------------------
# Coordinates of cities
# -----------------------
CITY_COORDS = {
    "Vijayawada": (16.5062, 80.6480),
    "Guntur": (16.3067, 80.4365),
    "Visakhapatnam": (17.6868, 83.2185),
    "Nellore": (14.4426, 79.9865),
    "Tirupati": (13.6288, 79.4192),
    "Hyderabad": (17.3850, 78.4867),
    "Warangal": (17.9689, 79.5941),
    "Nizamabad": (18.6727, 78.0941),
    "Khammam": (17.2473, 80.1514),
    "Karimnagar": (18.4386, 79.1281),
    "Anantapur": (14.6816, 77.6000),
    "Kurnool": (15.8281, 78.0373),
}

# -----------------------
# Helper Functions
# -----------------------
def safe_connect():
    """Safely connect to MySQL."""
    return mysql.connector.connect(**DB_CONFIG)

def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lon in KM."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * (math.sin(dlambda / 2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def blood_compatible(donor_bg, req_bg):
    """Check if donor blood group can donate to required blood group."""
    compat = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+']
    }
    return 1 if req_bg in compat.get(donor_bg, []) else 0

def urgency_score(urg):
    """Assign score for urgency."""
    return {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}.get(urg, 2)

# -----------------------
# Flask App with proper template folder
# -----------------------
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Enhanced CORS configuration for mobile access
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Add headers to support mobile and PWA
@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Cache-Control'] = 'public, max-age=3600'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

@app.route("/")
def api_root():
    try:
        return render_template("index.html")
    except Exception as e:
        print(f"❌ Template error: {e}")
        print(f"Template dir: {TEMPLATE_DIR}")
        print(f"Files in template: {os.listdir(TEMPLATE_DIR) if os.path.exists(TEMPLATE_DIR) else 'Not found'}")
        return jsonify({"error": f"Template error: {e}"}), 500

@app.route("/home")
def serve_home():
    return render_template("index.html")

# -----------------------
# Database Initialization
# -----------------------
@app.route("/api/init-db", methods=["POST", "GET"])
def init_database():
    """Initialize database schema from SQL file."""
    try:
        schema_path = os.path.join(BASE_DIR, 'database_schema.sql')
        
        if not os.path.exists(schema_path):
            return jsonify({"error": "Schema file not found"}), 404
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = safe_connect()
        cursor = conn.cursor()
        
        # Execute each statement
        executed_count = 0
        for statement in schema_sql.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    executed_count += 1
                except Exception as e:
                    print(f"⚠️ Statement error: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Database schema initialized successfully! ({executed_count} statements executed)"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/check-db", methods=["GET"])
def check_database():
    """Check if database and tables exist."""
    try:
        conn = safe_connect()
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        
        # Get list of tables
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "database": db_name,
            "tables": tables,
            "table_count": len(tables),
            "schema_initialized": len(tables) > 0
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "schema_initialized": False
        }), 500

# -----------------------
# PWA Static Files
# -----------------------
@app.route("/manifest.json")
def serve_manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@app.route("/service-worker.js")
def serve_sw():
    return send_from_directory('static', 'service-worker.js', mimetype='application/javascript')

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory('static', filename)

# -----------------------
# Chatbot
# -----------------------
@app.route("/chatbot", methods=["POST"])
def chatbot_route():
    if not CHATBOT_AVAILABLE:
        return jsonify({"error": "Chatbot not available"}), 500

    data = request.get_json()
    message = data.get("message", "")
    try:
        reply = get_bot_reply(message)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": f"Chatbot error: {e}"}), 500

# -----------------------
# Donor Registration
# -----------------------
@app.route("/api/donor/register", methods=["POST"])
def register_donor():
    try:
        data = request.get_json()
        print("📩 Donor data received:", data)

        conn = safe_connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO donors 
            (name, email, contact_number, city, state, blood_group, availability,
             months_since_first_donation, number_of_donation, pints_donated, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
        """, (
            data["name"],
            data["email"],
            data["phone"],
            data["city"],
            data["state"],
            data["blood_group"],
            "Yes" if data.get("availability", "Yes") in ["Yes", "Ready"] else "No",
            0, 0, data.get("pints_donated", 1)
        ))

        conn.commit()
        donor_id = cursor.lastrowid
        cursor.close()
        conn.close()

        print(f"✅ Donor registered successfully! ID: {donor_id}")
        return jsonify({"message": "Donor registered successfully!", "donor_id": donor_id}), 200

    except Exception as e:
        print("❌ Error in register_donor:", e)
        return jsonify({"error": str(e)}), 500

# -----------------------
# Create Blood Request
# -----------------------
@app.route("/api/request/create", methods=["POST"])
def create_request():
    try:
        data = request.get_json()
        print("📩 New blood request:", data)

        conn = safe_connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO requests (blood_group_needed, urgency, city, state, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["blood_group"],
            data["urgency"],
            data["city"],
            "Andhra Pradesh / Telangana",
            "Open"
        ))

        conn.commit()
        request_id = cursor.lastrowid
        cursor.close()
        conn.close()

        print(f"✅ Request created with ID: {request_id}")
        return jsonify({"message": "Request created successfully!", "request_id": request_id}), 200

    except Exception as e:
        print("❌ Error in create_request:", e)
        return jsonify({"error": str(e)}), 500

# -----------------------
# Match Donors for Request
# -----------------------
@app.route("/api/request/matches/<int:request_id>", methods=["GET"])
def match_donors(request_id):
    """Find compatible donors for a given request."""
    try:
        conn = safe_connect()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM requests WHERE request_id = %s", (request_id,))
        req = cursor.fetchone()
        if not req:
            return jsonify({"error": "Request not found"}), 404

        print(f"🔍 Matching for Request ID {request_id}: {req}")

        # Fetch donors
        cursor.execute("""
            SELECT donor_id, name, email, contact_number AS phone, city, state, blood_group, availability
            FROM donors
            WHERE availability = 'Yes'
        """)
        donors = cursor.fetchall()
        if not donors:
            return jsonify({"error": "No donors found"}), 404

        req_coords = CITY_COORDS.get(req["city"], (0, 0))
        results = []

        for donor in donors:
            donor_coords = CITY_COORDS.get(donor["city"], (0, 0))
            distance = haversine_km(donor_coords[0], donor_coords[1], req_coords[0], req_coords[1])
            blood_match = blood_compatible(donor["blood_group"], req["blood_group_needed"])
            if blood_match:
                results.append({
                    "name": donor["name"],
                    "city": donor["city"],
                    "blood_group": donor["blood_group"],
                    "email": donor["email"],
                    "phone": donor["phone"],
                    "distance_km": round(distance, 2)
                })

        cursor.close()
        conn.close()

        return jsonify({
            "request_id": request_id,
            "blood_group_needed": req["blood_group_needed"],
            "city": req["city"],
            "total_matches": len(results),
            "available_donors": sorted(results, key=lambda x: x["distance_km"])
        }), 200

    except Exception as e:
        print("❌ Error in match_donors:", e)
        return jsonify({"error": str(e)}), 500

# -----------------------
# Admin Summary
# -----------------------
@app.route("/admin/summary", methods=["GET"])
def summary():
    try:
        conn = safe_connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM donors")
        total_donors = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM requests")
        total_requests = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM matches")
        total_matches = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return jsonify({
            "total_donors": total_donors,
            "total_requests": total_requests,
            "total_matches": total_matches
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------
# Emergency Alert (SOS)
# -----------------------
@app.route("/api/emergency-alert", methods=["POST"])
def emergency_alert():
    """Send emergency email and SMS alerts to available donors in a city."""
    try:
        data = request.get_json()
        city = data.get("city", "").strip()
        blood_group = data.get("blood_group", "").strip()
        patient_name = data.get("patient_name", "Unknown Patient").strip()
        patient_phone = data.get("patient_phone", "Not provided").strip()
        hospital_name = data.get("hospital_name", "Unknown Hospital").strip()
        units_required = data.get("units_required", "1").strip()
        message = data.get("message", "🚨 EMERGENCY: Blood donation needed urgently!")
        via_sms = data.get("via_sms", False)
        
        if not city or not blood_group:
            return jsonify({"error": "City and blood_group are required"}), 400
        
        print(f"🚨 Emergency Alert triggered: City={city}, Blood={blood_group}, SMS={via_sms}, Patient={patient_name}")
        
        conn = safe_connect()
        cursor = conn.cursor(dictionary=True)
        
        # Find all available donors in the city
        cursor.execute("""
            SELECT donor_id, name, email, contact_number AS phone, blood_group, city
            FROM donors
            WHERE city = %s AND availability = 'Yes'
        """, (city,))
        
        donors = cursor.fetchall()
        print(f"Found {len(donors)} available donors in {city}")
        
        if not donors:
            cursor.close()
            conn.close()
            return jsonify({
                "notified_count": 0,
                "details": [],
                "message": f"No available donors found in {city}"
            }), 200
        
        # Filter by blood group compatibility
        notified_donors = []
        for donor in donors:
            if blood_compatible(donor["blood_group"], blood_group):
                notified_donors.append(donor)
        
        print(f"After blood compatibility filter: {len(notified_donors)} donors")
        
        if not notified_donors:
            cursor.close()
            conn.close()
            return jsonify({
                "notified_count": 0,
                "details": [],
                "message": f"No donors with compatible blood type {blood_group} found in {city}"
            }), 200
        
        # Send alerts
        details = []
        successful_email = 0
        successful_sms = 0
        
        for donor in notified_donors:
            email_sent = False
            sms_sent = False
            
            # Send email
            if donor.get("email"):
                try:
                    email_subject = f"🚨 EMERGENCY ALERT: Blood Needed - {blood_group}"
                    email_body = f"""
Dear {donor.get('name', 'Donor')},

{message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 EMERGENCY PATIENT DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Patient Name:         {patient_name}
Patient Phone:        {patient_phone}
Hospital Name:        {hospital_name}
Location/City:        {city}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🩸 BLOOD REQUIREMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Blood Group Needed:    {blood_group}
Units Required:       {units_required} units

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  Your urgent assistance is requested. 

Please contact the hospital immediately if you can help save this patient's life.

📞 Hospital Contact: {patient_phone}
📍 Location: {city}

Every drop counts. Your donation can save a life!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Thank you for being a life saver!

Rakt-Sathi Team
"""
                    email_sent = send_email_alert(donor.get("email"), email_subject, email_body)
                    if email_sent:
                        successful_email += 1
                except Exception as e:
                    print(f"❌ Email error for {donor.get('email')}: {e}")
                    email_sent = False
            
            # Send SMS
            sms_sent = False
            if via_sms and donor.get("phone"):
                try:
                    sms_message = f"""🚨 EMERGENCY ALERT: Blood Needed - {blood_group}

Dear {donor.get('name', 'Donor')},

{message}

📋 EMERGENCY DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Patient Name: {patient_name}
Patient Phone: {patient_phone}
Hospital Name: {hospital_name}
Blood Group Needed: {blood_group}
Units Required: {units_required}
Location: {city}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your urgent assistance is requested. Please contact the hospital immediately if you can help.

Every drop counts. Your donation can save a life!

Thank you for being a life saver!

Rakt-Sathi Team"""
                    sms_sent = send_sms_alert(donor.get("phone"), sms_message)
                    if sms_sent:
                        successful_sms += 1
                except Exception as e:
                    print(f"❌ SMS error for {donor.get('phone')}: {e}")
                    sms_sent = False
            
            details.append({
                "donor_id": donor.get("donor_id"),
                "name": donor.get("name"),
                "email": donor.get("email"),
                "phone": donor.get("phone"),
                "email_sent": email_sent,
                "sms": sms_sent
            })
        
        # Store notifications in database for donors
        try:
            conn2 = safe_connect()
            cursor2 = conn2.cursor()
            
            for donor in notified_donors:
                cursor2.execute("""
                    INSERT INTO notifications 
                    (donor_id, donor_email, patient_name, patient_phone, hospital_name, 
                     blood_group, units_required, city, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', NOW())
                """, (
                    donor.get("donor_id"),
                    donor.get("email"),
                    patient_name,
                    patient_phone,
                    hospital_name,
                    blood_group,
                    units_required,
                    city
                ))
            
            conn2.commit()
            cursor2.close()
            conn2.close()
            print(f"✅ Notifications stored in database")
        except Exception as e:
            print(f"⚠️ Could not store notifications: {e}")
        
        cursor.close()
        conn.close()
        
        print(f"✅ Alerts sent: {successful_email} emails, {successful_sms} SMS")
        
        return jsonify({
            "notified_count": len(notified_donors),
            "successful_emails": successful_email,
            "successful_sms": successful_sms,
            "details": details
        }), 200
        
    except Exception as e:
        print(f"❌ Error in emergency_alert: {e}")
        return jsonify({"error": str(e)}), 500


# Get Donor Profile by Email
# -----------------------
@app.route("/api/donor-by-email/<email>", methods=["GET"])
def get_donor_by_email(email):
    """Fetch donor profile information by email."""
    try:
        conn = safe_connect()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT donor_id, name, email, contact_number, blood_group, 
                   city, age, gender, availability, last_donation_date
            FROM donors
            WHERE email = %s
        """, (email,))
        
        donor = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if donor:
            return jsonify(donor), 200
        else:
            return jsonify({"error": "Donor not found"}), 404
            
    except Exception as e:
        print(f"❌ Error fetching donor: {e}")
        return jsonify({"error": str(e)}), 500


# Get Notifications for a Donor
# -----------------------
@app.route("/api/notifications/<email>", methods=["GET"])
def get_notifications(email):
    """Fetch all notifications for a donor."""
    try:
        conn = safe_connect()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT notification_id, donor_email, patient_name, patient_phone, 
                   hospital_name, blood_group, units_required, city, status, created_at
            FROM notifications
            WHERE donor_email = %s
            ORDER BY created_at DESC
        """, (email,))
        
        notifications = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"notifications": notifications}), 200
            
    except Exception as e:
        print(f"❌ Error fetching notifications: {e}")
        return jsonify({"error": str(e)}), 500


# Update Notification Status (Accept/Ignore)
# -----------------------
@app.route("/api/notifications/<int:notification_id>", methods=["PUT"])
def update_notification(notification_id):
    """Update notification status (accept or ignore)."""
    try:
        data = request.get_json()
        status = data.get("status", "ignored")  # "accepted" or "ignored"
        
        conn = safe_connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE notifications
            SET status = %s
            WHERE notification_id = %s
        """, (status, notification_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": f"Notification {status} successfully"}), 200
            
    except Exception as e:
        print(f"❌ Error updating notification: {e}")
        return jsonify({"error": str(e)}), 500


# Get SOS Responses (Alerts sent by a requester)
# -----------------------
@app.route("/api/sos-responses/<email>", methods=["GET"])
def get_sos_responses(email):
    """Get all SOS alerts sent and their responses (from donors)."""
    try:
        conn = safe_connect()
        cursor = conn.cursor(dictionary=True)
        
        # Get all notifications where current user is the patient/requester
        # We'll track this by getting alerts sent to donors about this patient
        cursor.execute("""
            SELECT notification_id, donor_email, patient_name, donor_name, 
                   blood_group, units_required, city, status, created_at
            FROM notifications
            WHERE patient_name IN (
                SELECT CONCAT(name, ' - ', email) FROM donors WHERE email = %s
            )
            ORDER BY created_at DESC
        """, (email,))
        
        notifications = cursor.fetchall()
        
        # Alternative simpler approach: store who sent the alert
        # For now, we'll get all responses and filter
        cursor.execute("""
            SELECT notification_id, donor_email, patient_name, patient_phone,
                   hospital_name, blood_group, units_required, city, status, 
                   created_at
            FROM notifications
            ORDER BY created_at DESC
            LIMIT 100
        """)
        
        all_responses = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"responses": all_responses}), 200
            
    except Exception as e:
        print(f"❌ Error fetching SOS responses: {e}")
        return jsonify({"error": str(e)}), 500

# -----------------------
# Run the App
# -----------------------
if __name__ == "__main__":
    print("🚀 Starting Rakt-Sathi Flask server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
