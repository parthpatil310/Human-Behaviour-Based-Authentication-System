FEATURES:
🔑 Password Authentication
🧠 Behavioral Biometrics
Typing speed & rhythm
Keystroke hold time
Mouse movement tracking
📊 Dynamic Trust Score Calculation
⚠️ Risk-Based Authentication
Low risk → Direct login
Medium risk → Security question
High risk → OTP verification
📧 Email OTP Verification
📍 Location Tracking (Latitude & Longitude)
📊 User Dashboard with Trust Score Visualization

Tech Stack:
Frontend: HTML, CSS, JavaScript
Backend: Flask (Python)
Database: SQLite
Email Service: SMTP (Gmail)

How It Works:
The system captures user behavior during login (typing patterns, mouse activity, etc.) and compares it with previously stored data. Based on this comparison, a trust score is calculated.
Trust Score → Determines Authentication Level
✅ High Trust → Access Granted
⚠️ Medium Trust → Security Question
❌ Low Trust → Access Denied / OTP Required
