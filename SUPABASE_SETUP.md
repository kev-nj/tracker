# UK Finance Graduate Tracker - Supabase Setup Guide

## 🚀 Migration to Supabase Complete!

I've created a new version with **Supabase database** and **authentication**. Here's what's changed:

### New Features:
- ✅ **User Authentication** (Sign up, Login, Logout)
- ✅ **User Profiles** with education, skills, experience
- ✅ **Database Storage** (no more CSV files!)
- ✅ **Personalized Cover Letters** using your profile data
- ✅ **Application Tracking** per user

---

## 📋 Setup Instructions

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Wait for it to finish setting up (~2 minutes)

### 2. Run Database Schema

1. In your Supabase project dashboard, go to **SQL Editor**
2. Copy the entire contents of `schema.sql`
3. Paste and click **Run**

This creates:
- `user_profiles` table (stores education, skills, experience)
- `graduate_roles` table (all the tracker data)
- `user_applications` table (track your applications)
- Security policies (Row Level Security)

### 3. Get Your API Keys

In your Supabase project dashboard:
1. Go to **Settings** → **API**
2. Copy these values to your `.env` file:
   - **URL**: `SUPABASE_URL`
   - **anon/public key**: `SUPABASE_KEY`
   - **service_role key**: `SUPABASE_SERVICE_KEY`

### 4. Update .env File

```env
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini

SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

SECRET_KEY=generate-a-random-string-here
```

### 5. Run the New App

```bash
python app_supabase.py
```

Open: **http://localhost:8080**

---

## 🎯 How It Works

### Authentication Flow:
1. **Sign Up**: Create account with email/password
2. **Login**: Get access token for API calls
3. **Profile**: Add your education, skills, experience

### Profile Fields:
- Full Name
- Phone
- University & Degree
- Graduation Year & GPA
- Skills (array)
- Experience
- Achievements
- Career Interests
- LinkedIn URL

### Cover Letter Generation:
When you click "Generate Cover Letter":
1. Fetches YOUR profile data automatically
2. Fetches company and role pages
3. Uses OpenAI to create a **personalized** letter with:
   - Your education
   - Your skills
   - Your experience
   - Company-specific information
   - Role requirements

---

## 🔄 Data Migration

The scraper still works! It:
1. Scrapes the tracker website
2. Saves to CSV temporarily
3. **Automatically imports to Supabase**
4. Runs every hour

---

## 📊 Database Schema

### user_profiles
- Personal info, education, skills, experience

### graduate_roles  
- All roles from the tracker

### user_applications
- Track which roles you've applied to
- Store generated cover letters
- Monitor application status

---

## 🔐 Security

- Row Level Security (RLS) enabled
- Users can only see their own data
- Public roles visible to all
- Service role for admin operations

---

## 🎨 Next Steps (Future Frontend Update)

The frontend needs to be updated with:
- Login/Signup modal
- Profile management page
- JWT token storage
- Protected routes

Let me know if you want me to create the updated frontend now!
