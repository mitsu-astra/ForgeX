import { create } from 'zustand'

interface UploadedData {
  images: Array<{ id: string; name: string; preview: string }>;
  productionCsv: { id: string; name: string; modelType: string; rows: number } | null;
  economicCsv: { id: string; name: string; rows: number } | null;
}

interface AppState {
  currentBatchId: string | null;
  uploadedData: UploadedData;
  setCurrentBatchId: (id: string | null) => void;
  setUploadedData: (data: Partial<UploadedData>) => void;
  resetData: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  currentBatchId: null,
  uploadedData: {
    images: [],
    productionCsv: null,
    economicCsv: null,
  },
  setCurrentBatchId: (id) => set({ currentBatchId: id }),
  setUploadedData: (data) => set((state) => ({
    uploadedData: { ...state.uploadedData, ...data }
  })),
  resetData: () => set({
    currentBatchId: null,
    uploadedData: { images: [], productionCsv: null, economicCsv: null }
  }),
}))
