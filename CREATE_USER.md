# How to Create User Accounts in Supabase

Since signup is disabled, you need to manually create user accounts in Supabase.

## Method 1: Supabase Dashboard (Easiest)

1. Go to your Supabase project dashboard
2. Click **Authentication** in the left sidebar
3. Click **Users** tab
4. Click **Add User** button
5. Fill in:
   - Email address
   - Password (or use "Auto generate password")
   - Optional: Disable "Send email confirmation"
6. Click **Create User**

The user profile will be automatically created when they first login.

## Method 2: SQL Query

Run this in the Supabase SQL Editor:

```sql
-- Create a new user
INSERT INTO auth.users (
    id,
    email,
    encrypted_password,
    email_confirmed_at,
    created_at,
    updated_at
)
VALUES (
    gen_random_uuid(),
    'user@example.com',
    crypt('your_password', gen_salt('bf')),
    NOW(),
    NOW(),
    NOW()
);

-- Create their profile (use the ID from above)
INSERT INTO user_profiles (id, email, full_name)
VALUES (
    (SELECT id FROM auth.users WHERE email = 'user@example.com'),
    'user@example.com',
    'User Full Name'
);
```

## What Happens After:

1. User logs in with the credentials you created
2. They click "Profile" to add their:
   - Education (university, degree, GPA, grad year)
   - Skills
   - Experience
   - Achievements
   - Career interests
3. When they generate cover letters, all this info is automatically used!

## Test Credentials (Example)

Create a test account to try it out:
- Email: test@example.com
- Password: TestPass123

The user can add their full profile after logging in.
