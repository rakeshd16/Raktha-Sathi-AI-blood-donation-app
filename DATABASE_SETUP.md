# Database Schema Setup Guide

## ✅ Status: Schema Successfully Initialized

Your Rakt-Sathi application now has full database support!

## Database Initialization Methods

### Method 1: Automatic (Recommended for Mobile)
The app **automatically initializes the database** when you first visit it:
1. Open app at `http://10.0.125.80:5000` on mobile or `http://localhost:5000`
2. The app checks if the database schema exists
3. If not, it automatically creates all tables
4. You'll see console logs: "✅ Database schema initialized successfully!"

### Method 2: Manual Script
Run the initialization script from terminal:
```bash
python init_db.py
```

### Method 3: API Endpoint
Initialize via API call:
```bash
curl -X POST http://localhost:5000/api/init-db
```

## Database Structure

### Tables Created:
1. **Donors** - Blood donor profiles
2. **Requests** - Blood requests
3. **Matches** - Donor-request matches
4. **Notifications** - Notification history
5. **Users** - User authentication
6. **DonationHistory** - Donation records
7. **BloodInventory** - Blood stock tracking

## Database Credentials

**Host:** localhost  
**User:** root  
**Password:** Rakesh@13  
**Database:** rakth_sathi  

⚠️ **Change password in production!**

## API Endpoints for Database Management

### Check Database Status
```
GET /api/check-db
```
Response:
```json
{
  "database": "rakth_sathi",
  "tables": ["Donors", "Requests", "Matches", ...],
  "table_count": 7,
  "schema_initialized": true
}
```

### Initialize Database
```
POST /api/init-db
```
Response:
```json
{
  "success": true,
  "message": "Database schema initialized successfully! (50 statements executed)"
}
```

## Sample Data

The schema includes sample data:
- 10+ Sample Donors
- 5+ Sample Blood Requests
- Sample Matches
- Sample Notifications

## Troubleshooting

### Database Connection Error?
1. Make sure MySQL is running locally
2. Verify credentials in `app.py` (lines 35-41)
3. Check if database user `root` exists

### Tables Already Exist?
The script handles this gracefully - it uses `CREATE TABLE IF NOT EXISTS` so running it multiple times is safe.

### Schema Still Not Initialized?
1. Check browser console (F12) for errors
2. Check Flask server logs for messages
3. Run `python init_db.py` manually
4. Check MySQL directly:
   ```sql
   USE rakth_sathi;
   SHOW TABLES;
   ```

## Next Steps

1. ✅ Database initialized
2. ✅ Tables created with sample data
3. Create user accounts
4. Register donors
5. Create blood requests
6. View donor-request matches

---

**Your mobile app now has full database support!** 🎉
