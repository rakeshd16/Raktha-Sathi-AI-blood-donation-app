"""
test_sms.py - Test SMS with patient details (like emergency alert system)
"""

from send_sms import send_sms

# Patient Details
patient_name = "Rakesh"
patient_phone = "9063234423"  # or use: "+91 9063234423"
blood_group = "O+"
hospital_name = "ramesh"
units_required = 2
city = "vijayaawada"

# Format SMS message with patient details
sms_message = f"""
🚨 BLOOD DONATION EMERGENCY ALERT 🚨

Patient: {patient_name}
Blood Group: {blood_group}
Hospital: {hospital_name}
Units Needed: {units_required}
Location: {city}
Contact: {patient_phone}

Please respond if you can donate.
Reply STOP to opt out.
"""

# Test SMS sending
print("=" * 60)
print("Testing SMS with patient details...")
print("=" * 60)
sms_result = send_sms(patient_phone, sms_message)
print(f"SMS Result: {'✅ SUCCESS' if sms_result else '❌ FAILED'}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
