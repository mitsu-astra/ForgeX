import { create } from 'zustand'
import { UserProfile } from './api'

interface UploadedData {
  images: Array<{ id: string; name: string; preview: string }>;
  productionCsv: { id: string; name: string; modelType: string; rows: number } | null;
  economicCsv: { id: string; name: string; rows: number } | null;
  hasAnalyzedData?: boolean;
}

const DEFAULT_DEMO_USER: UserProfile = {
  id: 1,
  email: 'admin@forgex.ai',
  full_name: 'Alex Vance',
  role: 'Lead Systems Architect',
  avatar_initials: 'AV',
}

interface AppState {
  currentBatchId: string | null;
  uploadedData: UploadedData;
  currentUser: UserProfile | null;
  authToken: string | null;
  isAuthReady: boolean;
  initializeAuth: () => void;
  setCurrentBatchId: (id: string | null) => void;
  setUploadedData: (data: Partial<UploadedData>) => void;
  setCurrentUser: (user: UserProfile | null, token?: string | null) => void;
  logout: () => void;
  resetData: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  currentBatchId: null,
  uploadedData: {
    images: [],
    productionCsv: null,
    economicCsv: null,
    hasAnalyzedData: false,
  },
  currentUser: null,
  authToken: null,
  isAuthReady: false,

  initializeAuth: () => {
    if (typeof window === 'undefined') return;
    try {
      const storedUser = localStorage.getItem('auth_user');
      const storedToken = localStorage.getItem('auth_token');
      if (storedUser && storedToken) {
        const user = JSON.parse(storedUser);
        document.cookie = `auth_token=${storedToken}; path=/; max-age=86400; SameSite=Lax`;
        set({ currentUser: user, authToken: storedToken, isAuthReady: true });
        return;
      }
    } catch {
      // ignore JSON parse error
    }
    set({ currentUser: null, authToken: null, isAuthReady: true });
  },

  setCurrentBatchId: (id) => set({ currentBatchId: id }),
  setUploadedData: (data) => set((state) => ({
    uploadedData: { ...state.uploadedData, ...data }
  })),

  setCurrentUser: (user, token = null) => {
    if (typeof window !== 'undefined') {
      if (user && token) {
        try {
          localStorage.setItem('auth_user', JSON.stringify(user));
          localStorage.setItem('auth_token', token);
          document.cookie = `auth_token=${token}; path=/; max-age=86400; SameSite=Lax`;
        } catch {}
      } else {
        try {
          localStorage.removeItem('auth_user');
          localStorage.removeItem('auth_token');
          document.cookie = 'auth_token=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        } catch {}
      }
    }
    set({
      currentUser: user,
      authToken: token,
      isAuthReady: true,
      uploadedData: { images: [], productionCsv: null, economicCsv: null, hasAnalyzedData: false },
    });
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      try {
        localStorage.removeItem('auth_user');
        localStorage.removeItem('auth_token');
        document.cookie = 'auth_token=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      } catch {}
    }
    set({
      currentUser: null,
      authToken: null,
      isAuthReady: true,
      uploadedData: { images: [], productionCsv: null, economicCsv: null, hasAnalyzedData: false },
    });
  },

  resetData: () => set({
    currentBatchId: null,
    uploadedData: { images: [], productionCsv: null, economicCsv: null, hasAnalyzedData: false }
  }),
}))
