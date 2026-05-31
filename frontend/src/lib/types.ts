export interface Profile {
  id: string;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  bio_haiku_id: string | null;
  created_at: string;
}

export interface Haiku {
  id: string;
  user_id: string;
  line1: string;
  line2: string;
  line3: string;
  full_text: string;
  syllable_counts: [number, number, number];
  is_identity_haiku: boolean;
  created_at: string;
}

export interface EmotionalProfile {
  id: string;
  haiku_id: string;
  user_id: string;
  tone_tags: string[];
  primary_emotion: string;
  intensity_score: number;
  created_at: string;
}

export interface FeedHaiku {
  id: string;
  user_id: string;
  haiku_id: string;
  published_at: string;
  haikus: {
    line1: string;
    line2: string;
    line3: string;
    full_text: string;
  };
  profiles: {
    username: string;
    display_name: string | null;
  };
  emotional_profiles: {
    primary_emotion: string;
    intensity_score: number;
  };
  reaction_count: number;
  resonance_score?: number;
}

export interface UserMatch {
  id: string;
  username: string;
  display_name: string | null;
  identity_haiku: string | null;
  resonance_score: number;
}
