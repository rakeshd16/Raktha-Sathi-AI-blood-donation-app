# send_sms.py
"""Send SMS helper using SMSHorizon API.

This file exposes send_sms() function to send SMS messages via SMSHorizon.
If the requests package is not available, it prints a warning and returns False.
"""

import os
import requests

try:
    import requests
    SMSHORIZON_AVAILABLE = True
except Exception:
    SMSHORIZON_AVAILABLE = False
    print("⚠️ requests package not found — SMS functionality disabled. To enable, run: python -m pip install requests")

# ----------------------------
# SMSHorizon Configuration
# (Move these to environment variables in production)
# ----------------------------
BASE_URL = "https://smshorizon.co.in/api"
USER = os.getenv("SMSHORIZON_USER", "")
API_KEY = os.getenv("SMSHORIZON_API_KEY", "")
SENDER_ID = os.getenv("SMSHORIZON_SENDER_ID", "RaktSathi")
TID = os.getenv("SMSHORIZON_TID")

# ----------------------------
# Email Configuration
# ----------------------------
RS_SENDER_EMAIL = os.getenv("EMAIL_ADDRESS", "")
RS_SENDER_APP_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# ----------------------------
# Helper Functions
# ----------------------------

def format_phone_number(phone):
    """Format phone number for SMSHorizon (remove +, keep 91 prefix)
    
    Examples:
        9876543210 -> 919876543210
        09876543210 -> 919876543210
        +919876543210 -> 919876543210
        +91 9876543210 -> 919876543210
    """
    if not phone:
        return None
    
    # Remove spaces, hyphens, and +
    phone = phone.replace(" ", "").replace("-", "").replace("+", "").strip()
    
    # If starts with 0, remove it (Indian format)
    if phone.startswith("0"):
        phone = phone[1:]
    
    # Ensure it starts with 91 (India country code) if not present
    if not phone.startswith("91"):
        phone = "91" + phone
    
    return phone


def send_sms(mobile, message, senderid=None, sms_type="txt", tid=None):
    """
    Send a single SMS (or comma-separated list of numbers).
    
    Args:
        mobile: Phone number or comma-separated list of numbers
        message: SMS message content
        senderid: Optional sender ID (only required for DLT/transactional)
        sms_type: "txt" for normal or "uni" for unicode
        tid: Optional template ID (only required for DLT/transactional)

    Returns True if the message was sent, False otherwise.
    """
    if not SMSHORIZON_AVAILABLE:
        print(f"⚠️ SMS not sent (requests package missing). Intended recipient: {mobile}. Message: {message}")
        return False

    try:
        # Format phone number if single number provided
        if "," not in str(mobile):
            formatted_mobile = format_phone_number(mobile)
            if not formatted_mobile:
                print(f"❌ SMS failed to {mobile}: Invalid phone number")
                return False
        else:
            # Multiple numbers - format each one
            numbers = [format_phone_number(n.strip()) for n in str(mobile).split(",")]
            formatted_mobile = ",".join([n for n in numbers if n])
            if not formatted_mobile:
                print(f"❌ SMS failed: No valid phone numbers")
                return False
        
        # Prepare parameters for SMSHorizon API
        params = {
            "user": USER,
            "apikey": API_KEY,
            "mobile": formatted_mobile,
            "message": message,
            "type": sms_type,
        }

        # Always include sender ID (required by SMSHorizon)
        if senderid:
            params["senderid"] = senderid
        elif SENDER_ID:
            params["senderid"] = SENDER_ID
            
        if tid:
            params["tid"] = tid

        url = f"{BASE_URL}/sendsms.php"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        msgid = response.text.strip()  # SMSHorizon returns msgid as plain text
        
        if msgid and msgid != "" and "ERROR" not in msgid:
            print(f"✅ SMS sent to {formatted_mobile}, Message ID: {msgid}")
            return True
        else:
            print(f"❌ SMS failed to {mobile}: {msgid if msgid else 'No message ID returned'}")
            return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ SMS failed to {mobile}: Network error - {str(e)}")
        return False
    except Exception as e:
        error_msg = str(e)
        print(f"❌ SMS failed to {mobile}: {error_msg}")
        
        # Log specific errors for debugging
        if "api" in error_msg.lower():
            print(f"   Issue: API key may be invalid")
            print(f"   Fix: Check API_KEY in send_sms.py")
        elif "user" in error_msg.lower():
            print(f"   Issue: Username may be invalid")
            print(f"   Fix: Check USER in send_sms.py")
        elif "unauthorized" in error_msg.lower():
            print(f"   Issue: Unauthorized - invalid credentials")
            print(f"   Fix: Go to https://smshorizon.co.in/ and verify your credentials")
        
        return False


def send_bulk_sms(mobiles, message, senderid=None, sms_type="txt", tid=None):
    """
    Send SMS to multiple numbers.
    
    Args:
        mobiles: List of mobile numbers or a single string with comma-separated numbers
        message: SMS message content
        senderid: Optional sender ID
        sms_type: "txt" for normal or "uni" for unicode
        tid: Optional template ID

    Returns True if the message was sent, False otherwise.
    """
    if isinstance(mobiles, list):
        mobiles = ",".join(mobiles)

    return send_sms(
        mobile=mobiles,
        message=message,
        senderid=senderid,
        sms_type=sms_type,
        tid=tid,
    )


def check_sms_status(msgid):
    """
    Check delivery status using msgid returned from send_sms.
    
    Args:
        msgid: Message ID returned from send_sms function
        
    Returns the status as a string.
    """
    if not SMSHORIZON_AVAILABLE:
        print(f"⚠️ Status check failed (requests package missing)")
        return None

    try:
        params = {
            "user": USER,
            "apikey": API_KEY,
            "msgid": msgid,
        }
        url = f"{BASE_URL}/status.php"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        status = response.text.strip()
        print(f"✅ SMS status for {msgid}: {status}")
        return status
        
    except Exception as e:
        print(f"❌ Status check failed for {msgid}: {str(e)}")
        return None
