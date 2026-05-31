-- Hyphen Database Migrations
-- Run these in order via Supabase SQL editor or psql

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT UNIQUE NOT NULL,
  display_name TEXT,
  avatar_url TEXT,
  bio_haiku_id UUID,  -- FK to haikus (set after first haiku)
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Haikus table
CREATE TABLE IF NOT EXISTS public.haikus (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  line1 TEXT NOT NULL,
  line2 TEXT NOT NULL,
  line3 TEXT NOT NULL,
  full_text TEXT GENERATED ALWAYS AS (line1 || E'\n' || line2 || E'\n' || line3) STORED,
  syllable_counts INTEGER[3] NOT NULL,  -- [5,7,5]
  is_identity_haiku BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Emotional profiles (AI-generated)
CREATE TABLE IF NOT EXISTS public.emotional_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  haiku_id UUID UNIQUE NOT NULL REFERENCES public.haikus(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  tone_tags TEXT[] NOT NULL,             -- e.g. ['melancholic','introspective','longing']
  primary_emotion TEXT NOT NULL,         -- dominant tag
  intensity_score FLOAT NOT NULL CHECK (intensity_score >= 0.0 AND intensity_score <= 1.0),
  resonance_embedding FLOAT[] NOT NULL,  -- 128-dim vector
  raw_ai_response JSONB,                 -- full Claude response
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Resonances (user similarity)
CREATE TABLE IF NOT EXISTS public.resonances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_a UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  user_b UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  resonance_score FLOAT NOT NULL CHECK (resonance_score >= -1.0 AND resonance_score <= 1.0),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_a, user_b),
  CHECK (user_a < user_b)  -- prevent duplicates
);

-- 5. Feed haikus
CREATE TABLE IF NOT EXISTS public.feed_haikus (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  haiku_id UUID NOT NULL REFERENCES public.haikus(id) ON DELETE CASCADE,
  emotional_profile_id UUID REFERENCES public.emotional_profiles(id),
  published_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Resonance reactions (one word per user per haiku)
CREATE TABLE IF NOT EXISTS public.resonance_reactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  feed_haiku_id UUID NOT NULL REFERENCES public.feed_haikus(id) ON DELETE CASCADE,
  reactor_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  word TEXT NOT NULL CHECK (char_length(word) <= 24),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(feed_haiku_id, reactor_id)
);

-- 7. Admin users
CREATE TABLE IF NOT EXISTS public.admin_users (
  user_id UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
  granted_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_haikus_user_id ON public.haikus(user_id);
CREATE INDEX IF NOT EXISTS idx_haikus_created_at ON public.haikus(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_emotional_profiles_user_id ON public.emotional_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_emotional_profiles_primary_emotion ON public.emotional_profiles(primary_emotion);
CREATE INDEX IF NOT EXISTS idx_feed_haikus_published_at ON public.feed_haikus(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_feed_haikus_user_id ON public.feed_haikus(user_id);
CREATE INDEX IF NOT EXISTS idx_resonances_user_a ON public.resonances(user_a);
CREATE INDEX IF NOT EXISTS idx_resonances_user_b ON public.resonances(user_b);
CREATE INDEX IF NOT EXISTS idx_resonances_score ON public.resonances(resonance_score DESC);
CREATE INDEX IF NOT EXISTS idx_reactions_feed_haiku ON public.resonance_reactions(feed_haiku_id);
CREATE INDEX IF NOT EXISTS idx_reactions_reactor ON public.resonance_reactions(reactor_id);

-- ===== ROW-LEVEL SECURITY (RLS) =====

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.haikus ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.emotional_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resonances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feed_haikus ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resonance_reactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_users ENABLE ROW LEVEL SECURITY;

-- Profiles: users can read all, write only their own
CREATE POLICY "profiles_read_all" ON public.profiles
  FOR SELECT USING (true);

CREATE POLICY "profiles_write_own" ON public.profiles
  FOR UPDATE USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

CREATE POLICY "profiles_insert_own" ON public.profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- Haikus: users can read all, write only their own, delete own
CREATE POLICY "haikus_read_all" ON public.haikus
  FOR SELECT USING (true);

CREATE POLICY "haikus_write_own" ON public.haikus
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "haikus_delete_own" ON public.haikus
  FOR DELETE USING (auth.uid() = user_id);

-- Emotional profiles: public read, created by system
CREATE POLICY "emotional_profiles_read_all" ON public.emotional_profiles
  FOR SELECT USING (true);

-- Resonances: public read
CREATE POLICY "resonances_read_all" ON public.resonances
  FOR SELECT USING (true);

-- Feed haikus: public read
CREATE POLICY "feed_haikus_read_all" ON public.feed_haikus
  FOR SELECT USING (true);

CREATE POLICY "feed_haikus_insert_own" ON public.feed_haikus
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "feed_haikus_delete_own" ON public.feed_haikus
  FOR DELETE USING (auth.uid() = user_id);

-- Reactions: users can read all, insert/update/delete own
CREATE POLICY "reactions_read_all" ON public.resonance_reactions
  FOR SELECT USING (true);

CREATE POLICY "reactions_write_own" ON public.resonance_reactions
  FOR INSERT WITH CHECK (auth.uid() = reactor_id);

CREATE POLICY "reactions_update_own" ON public.resonance_reactions
  FOR UPDATE USING (auth.uid() = reactor_id)
  WITH CHECK (auth.uid() = reactor_id);

CREATE POLICY "reactions_delete_own" ON public.resonance_reactions
  FOR DELETE USING (auth.uid() = reactor_id);

-- Admin users: public read, admins only
CREATE POLICY "admin_users_read_all" ON public.admin_users
  FOR SELECT USING (true);

-- ===== FUNCTIONS & TRIGGERS =====

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update profiles.updated_at
CREATE TRIGGER update_profiles_updated_at
BEFORE UPDATE ON public.profiles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update resonances.updated_at
CREATE TRIGGER update_resonances_updated_at
BEFORE UPDATE ON public.resonances
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ===== VIEWS =====

-- User activity stats
CREATE OR REPLACE VIEW public.user_stats AS
SELECT
  p.id,
  p.username,
  COUNT(DISTINCT h.id) as haiku_count,
  COUNT(DISTINCT CASE WHEN h.is_identity_haiku THEN 1 END) as identity_haiku_count,
  COUNT(DISTINCT f.id) as feed_post_count,
  COUNT(DISTINCT rr.id) as reaction_count,
  MAX(h.created_at) as last_haiku_at,
  MAX(f.published_at) as last_post_at
FROM public.profiles p
LEFT JOIN public.haikus h ON p.id = h.user_id
LEFT JOIN public.feed_haikus f ON p.id = f.user_id
LEFT JOIN public.resonance_reactions rr ON p.id = rr.reactor_id
GROUP BY p.id, p.username;

-- Platform analytics
CREATE OR REPLACE VIEW public.platform_stats AS
SELECT
  (SELECT COUNT(*) FROM public.profiles) as total_users,
  (SELECT COUNT(*) FROM public.haikus) as total_haikus,
  (SELECT COUNT(*) FROM public.feed_haikus) as total_feed_posts,
  (SELECT AVG(intensity_score) FROM public.emotional_profiles) as avg_intensity_score,
  (SELECT COUNT(DISTINCT user_id) FROM public.haikus) as active_poets;
