# 🚀 UK Finance Graduate Tracker - Startup Guide

Welcome! This guide will help you get the UK Finance Graduate Tracker up and running.

---

## 📋 Prerequisites

- **Python 3.10+** installed
- **Chrome browser** (for Selenium scraper)
- **Supabase account** (free tier works)
- **OpenAI API key** (for cover letter generation)

---

## ⚙️ Initial Setup

### 1. Clone/Download Project

Ensure you have the project files in a directory (e.g., `/Users/kevinj/Desktop/tracker`)

### 2. Create Virtual Environment

```bash
cd /Users/kevinj/Desktop/tracker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Configure Environment Variables

### 1. Create `.env` file

Copy the template below and save as `.env` in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_public_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Flask Secret Key
SECRET_KEY=your_random_secret_key_here
```

### 2. Get OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Navigate to API Keys
3. Create new key
4. Copy and paste into `.env`

### 3. Get Supabase Keys

1. Go to [supabase.com](https://supabase.com)
2. Create new project (wait ~2 minutes for setup)
3. Go to **Settings** → **API**
4. Copy:
   - **URL**: `SUPABASE_URL`
   - **anon/public key**: `SUPABASE_KEY` 
   - **service_role key**: `SUPABASE_SERVICE_KEY` (⚠️ Keep this secret!)

### 4. Generate Flask Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output to `SECRET_KEY` in `.env`

---

## 🗄️ Set Up Supabase Database

### 1. Run Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy entire contents of `schema.sql`
4. Paste and click **Run**

This creates:
- `user_profiles` table (stores user education, skills, experience)
- `graduate_roles` table (all tracker data)
- `user_applications` table (tracks application status)
- Row Level Security policies
- Indexes and triggers

### 2. Verify Tables Created

Go to **Table Editor** and confirm you see:
- ✅ user_profiles
- ✅ graduate_roles  
- ✅ user_applications

---

## 👤 Create Your User Account

### 1. Create Auth User

1. In Supabase dashboard, go to **Authentication** → **Users**
2. Click **Add User** → **Create new user**
3. Enter your email and password
4. Click **Create User**
5. Copy the **User UID** (you'll need this next)

### 2. Create User Profile

1. Go to **SQL Editor** → **New Query**
2. Run this SQL (replace `YOUR_USER_ID` and email):

```sql
INSERT INTO user_profiles (id, email) 
VALUES ('YOUR_USER_ID', 'your@email.com');
```

Or automatically create profiles for all auth users:

```sql
INSERT INTO user_profiles (id, email)
SELECT id, email FROM auth.users
WHERE id NOT IN (SELECT id FROM user_profiles);
```

---

## 🎯 Run the Application

### 1. Activate Virtual Environment

```bash
cd /Users/kevinj/Desktop/tracker
source venv/bin/activate
```

### 2. Start the Flask App

```bash
python app_supabase.py
```

You should see:

```
============================================================
UK Finance Tracker App Started
============================================================
🌐 Open in browser: http://localhost:8080
⏰ Scheduler: Running scraper every hour
🤖 OpenAI Model: gpt-4o-mini
🗄️  Database: Supabase
============================================================
```

### 3. Open in Browser

Navigate to: **http://localhost:8080**

---

## 🔄 First-Time Usage

### 1. Initial Data Load

On first run, the app will:
- Automatically scrape tracker website
- Import 600+ graduate roles to Supabase
- Takes ~30 seconds

### 2. Login

1. Click **Login** button (top right)
2. Enter your email and password
3. Click **Sign In**

### 3. Complete Profile

1. Click **Profile** button (after login)
2. Fill in your information:
   - Full Name
   - Phone
   - University & Degree
   - Graduation Year & GPA
   - Skills (comma-separated)
   - Experience
   - Achievements
   - Career Interests
   - LinkedIn URL
3. Click **Save Profile**
4. Click **Close** button

### 4. Generate Cover Letter

1. Browse graduate roles
2. Use filters and search to find roles
3. Click **Generate Cover Letter** on any role
4. Your personalized cover letter will be generated using:
   - Your profile data
   - Company information
   - Role requirements
5. Click **Copy to Clipboard** to use

---

## 🛠️ Maintenance

### Data Refresh

The scraper runs automatically every hour. To manually refresh:
1. Click **Refresh Data** button in the app
2. Or run: `python scraper.py`

### Adding New Users

1. Create user in Supabase Authentication
2. Run SQL to create their profile:

```sql
INSERT INTO user_profiles (id, email) 
VALUES ('USER_UUID', 'user@email.com');
```

---

## 🐛 Troubleshooting

### Port 8080 Already in Use

```bash
# Find process using port
lsof -ti:8080 | xargs kill -9

# Or change port in app_supabase.py (line with app.run)
```

### "No module named 'selenium'"

```bash
pip install -r requirements.txt
```

### Scraper Fails

- Ensure Chrome browser is installed
- Check internet connection
- Verify tracker website is accessible

### Login Fails

- Verify user exists in Supabase Authentication
- Check `.env` has correct Supabase keys
- Ensure password is correct

### Profile Won't Load

- Verify profile row exists in `user_profiles` table
- Run SQL to create profile (see "Create User Account" section)

### Cover Letter Generation Fails

- Check OpenAI API key is valid and has credits
- Verify profile is completed
- Check app terminal for detailed error messages

### Database Connection Issues

- Verify Supabase URL and keys in `.env`
- Check service_role key is complete (should be ~200+ characters)
- Restart the app after changing `.env`

---

## 📁 Project Structure

```
tracker/
├── app_supabase.py          # Main Flask application
├── scraper.py               # Web scraper for tracker data
├── schema.sql               # Database schema
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (DO NOT COMMIT)
├── templates/
│   └── index.html          # Frontend UI
└── venv/                   # Virtual environment
```

---

## 🔒 Security Notes

- **Never commit `.env`** to version control
- **Keep `SUPABASE_SERVICE_KEY` secret** - it has full database access
- **Rotate keys periodically** for security
- User passwords are managed by Supabase (encrypted)

---

## 📊 Features

✅ **Automated Scraping** - Hourly updates from tracker website  
✅ **Search & Filter** - Find roles by company, category, status  
✅ **User Authentication** - Secure login with Supabase Auth  
✅ **Profile Management** - Store education, skills, experience  
✅ **AI Cover Letters** - Personalized using your profile + role data  
✅ **Application Tracking** - Track which roles you've applied to  
✅ **Open Roles Only** - Filter to show only currently open positions  

---

## 🤝 Support

For issues or questions:
1. Check terminal output for detailed error messages
2. Review Supabase logs (Database → Logs)
3. Verify all environment variables are set correctly
4. Ensure database schema is properly created

---

## 🎉 You're Ready!

Your UK Finance Graduate Tracker is now fully set up. Happy job hunting! 🚀

Login → Complete Profile → Generate Cover Letters → Apply! 💼
