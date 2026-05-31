const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  private getHeaders(): HeadersInit {
    return {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` })
    };
  }

  async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const url = `${API_BASE_URL}${path}`;
    const options: RequestInit = {
      method,
      headers: this.getHeaders()
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Haiku
  async submitHaiku(line1: string, line2: string, line3: string) {
    return this.request('/api/haiku', 'POST', { line1, line2, line3 });
  }

  async checkSyllables(line: string) {
    return this.request(`/api/haiku/syllable-check?line=${encodeURIComponent(line)}`, 'POST');
  }

  async getHaiku(haiku_id: string) {
    return this.request(`/api/haiku/${haiku_id}`, 'GET');
  }

  async getHaikuProfile(haiku_id: string) {
    return this.request(`/api/haiku/${haiku_id}/profile`, 'GET');
  }

  // Profile
  async getProfile(username: string) {
    return this.request(`/api/profile/${username}`, 'GET');
  }

  async getMyProfile() {
    return this.request('/api/profile/me', 'GET');
  }

  async updateProfile(display_name?: string, avatar_url?: string) {
    return this.request('/api/profile/me', 'PUT', { display_name, avatar_url });
  }

  async setIdentityHaiku(haiku_id: string) {
    return this.request(`/api/profile/me/identity-haiku/${haiku_id}`, 'POST');
  }

  // Feed
  async getFeed(tab: 'for-you' | 'new' = 'for-you', limit: number = 20, offset: number = 0) {
    return this.request(`/api/feed?tab=${tab}&limit=${limit}&offset=${offset}`, 'GET');
  }

  async getDiscovery(limit: number = 20, offset: number = 0) {
    return this.request(`/api/feed/discover?limit=${limit}&offset=${offset}`, 'GET');
  }

  async reactToHaiku(feed_haiku_id: string, word: string) {
    return this.request(`/api/feed/${feed_haiku_id}/react`, 'POST', { word });
  }

  async postToFeed(haiku_id: string) {
    return this.request('/api/feed', 'POST', { haiku_id });
  }

  // Resonance
  async getMyMatches(limit: number = 20) {
    return this.request(`/api/resonance/my-matches?limit=${limit}`, 'GET');
  }

  async getResonanceScore(user_id: string) {
    return this.request(`/api/resonance/score/${user_id}`, 'GET');
  }

  // Auth
  async getCurrentUser() {
    return this.request('/api/auth/me', 'GET');
  }

  async logout() {
    return this.request('/api/auth/logout', 'POST');
  }
}

export const apiClient = new ApiClient();
