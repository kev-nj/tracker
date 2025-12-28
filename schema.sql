-- Supabase Database Schema for UK Finance Tracker

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User profiles table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    phone TEXT,
    university TEXT,
    degree TEXT,
    graduation_year INTEGER,
    gpa TEXT,
    skills TEXT[], -- Array of skills
    experience TEXT, -- Previous experience description
    achievements TEXT, -- Key achievements
    interests TEXT, -- Career interests
    linkedin_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Graduate roles table
CREATE TABLE IF NOT EXISTS graduate_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category TEXT NOT NULL,
    company_name TEXT NOT NULL,
    company_link TEXT,
    role_title TEXT NOT NULL,
    role_link TEXT,
    application_opens DATE,
    application_closes DATE,
    last_year_opened DATE,
    interview_stages TEXT,
    assessment_platform TEXT,
    online_application TEXT,
    cv_required TEXT,
    cover_letter TEXT,
    test_required TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User applications tracking
CREATE TABLE IF NOT EXISTS user_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES graduate_roles(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'Not Applied', -- Not Applied, Applied, Interview, Offer, Rejected
    applied_date DATE,
    cover_letter_generated TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_graduate_roles_company ON graduate_roles(company);
CREATE INDEX IF NOT EXISTS idx_graduate_roles_category ON graduate_roles(category);
CREATE INDEX IF NOT EXISTS idx_graduate_roles_dates ON graduate_roles(application_opens, application_closes);
CREATE INDEX IF NOT EXISTS idx_user_applications_user_id ON user_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_applications_status ON user_applications(status);

-- Row Level Security (RLS) Policies

-- Enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE graduate_roles ENABLE ROW LEVEL SECURITY;

-- User profiles: Users can only see and edit their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Graduate roles: Everyone can view (public data)
CREATE POLICY "Anyone can view graduate roles" ON graduate_roles
    FOR SELECT USING (true);

-- Only service role can insert/update/delete roles (via backend)
CREATE POLICY "Service role can manage roles" ON graduate_roles
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- User applications: Users can only see their own applications
CREATE POLICY "Users can view own applications" ON user_applications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own applications" ON user_applications
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own applications" ON user_applications
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own applications" ON user_applications
    FOR DELETE USING (auth.uid() = user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to auto-update updated_at
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_graduate_roles_updated_at BEFORE UPDATE ON graduate_roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_applications_updated_at BEFORE UPDATE ON user_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
