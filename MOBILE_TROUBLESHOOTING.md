# 🔧 Mobile App - Troubleshooting Guide

## Problem: Blank Page on Mobile

### ✅ Solution Applied
I've fixed the following issues:

1. **API URL Auto-Detection** ✅
   - Old: Hardcoded to `http://127.0.0.1:5000`
   - New: Auto-detects based on current device IP
   - Works on: Desktop, Mobile (same WiFi), Any device

2. **Enhanced CORS Headers** ✅
   - Allows requests from any origin
   - Supports all HTTP methods (GET, POST, PUT, DELETE)
   - Proper security headers added

3. **Better Error Logging** ✅
   - Console logs API URL for debugging
   - Easy to identify connection issues

---

## 📱 How to Access on Different Devices

### **Desktop / Laptop**
```
http://localhost:5000
or
http://127.0.0.1:5000
```

### **Mobile on Same WiFi**
```
http://192.168.43.131:5000
```
(Replace 192.168.43.131 with your computer's actual IP)

### **Different Network?**
Use your public IP (requires port forwarding or hosting service)

---

## 🐛 If Still Showing Blank Page

### Step 1: Check Console Logs
1. Open mobile Chrome
2. Press `Ctrl+Shift+I` (or Menu → More tools → Developer tools)
3. Go to **Console** tab
4. Look for error messages
5. Screenshot and share with me

### Step 2: Test Connection
Open this URL on your mobile:
```
http://192.168.43.131:5000/admin/summary
```
If you see JSON data (not blank), the connection is working ✅

### Step 3: Clear Cache
On mobile Chrome:
1. Menu → Settings
2. Privacy → Clear browsing data
3. Check "Cookies and site data"
4. Click "Clear data"
5. Reload the page

### Step 4: Check Network
Make sure:
- ✅ Phone and laptop are on **same WiFi**
- ✅ WiFi is enabled (not airplane mode)
- ✅ Flask server is running (check terminal)
- ✅ You're using the correct IP address

---

## 🔍 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **Blank white page** | API not loading | Check IP address in URL |
| **ERR_CONNECTION_REFUSED** | Flask server not running | Start `python app.py` |
| **ERR_NAME_NOT_RESOLVED** | Wrong IP address | Use `ipconfig` to find correct IP |
| **Page loads but no content** | CORS blocked | Check browser console for errors |
| **Can't find server** | Different network | Use public IP or hosting service |

---

## 📊 Debugging Steps

### Find Your Computer IP
**Windows PowerShell:**
```powershell
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.x.x)

### Test Flask Server
```powershell
# In your project folder
python app.py
# Should show: Running on http://127.0.0.1:5000
```

### Test Mobile Connection
On mobile browser, try:
1. `http://192.168.43.131:5000` - Full app
2. `http://192.168.43.131:5000/admin/summary` - API test

---

## 📋 What Changed

### index.html
```javascript
// OLD ❌
const API_BASE_URL = "http://127.0.0.1:5000";

// NEW ✅
const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:5000`;
```

### app.py
```python
# OLD ❌
CORS(app)

# NEW ✅
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
    }
})

@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    # ... other security headers
    return response
```

---

## 🚀 Quick Test Checklist

- [ ] Flask server is running (`python app.py`)
- [ ] Mobile is on same WiFi as computer
- [ ] Using correct IP address (e.g., `192.168.43.131:5000`)
- [ ] Port 5000 is not blocked by firewall
- [ ] Browser cache is cleared
- [ ] No VPN/Proxy enabled
- [ ] JavaScript is enabled in browser

---

## 💡 Still Not Working?

1. **Open browser DevTools** (F12)
2. Go to **Console** tab
3. Look for red error messages
4. Share the error message with me
5. I'll provide specific fix

---

## ✅ When It Works

You should see:
- ✅ "Welcome to Rakt-Sathi" page
- ✅ Login/Signup buttons
- ✅ Can click through app features
- ✅ API calls work without errors
- ✅ Can install as PWA

---

## 🎯 Next Steps After Fix

1. **Test all features:**
   - Register as donor
   - Create blood request
   - Find matches
   - Chat with AI

2. **Install as PWA:**
   - Chrome: Menu → "Install app"
   - Safari: Share → "Add to Home Screen"

3. **Share with others:**
   - Give them your computer IP + port
   - They open in their mobile browser

---

## 📞 Need Help?

If still blank, provide:
1. Screenshot of blank page
2. Browser console errors (F12 → Console)
3. Your computer IP (from `ipconfig`)
4. Mobile device type (Android/iOS)
5. Browser type (Chrome/Safari)
