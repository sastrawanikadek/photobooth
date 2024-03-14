import { create } from "zustand";
import { persist } from "zustand/middleware";

type ThemeMode = "light" | "dark" | "system";

interface State {
  theme: ThemeMode;
  language: string;
}

interface Action {
  setTheme: (theme: ThemeMode) => void;
  setLanguage: (language: string) => void;
}

const initialState: State = {
  theme: "light",
  language: "en",
};

export const useAppStore = create<State & Action>()(
  persist(
    (set) => ({
      ...initialState,
      setTheme: (theme) => set({ theme }),
      setLanguage: (language) => set({ language }),
    }),
    {
      name: "app-storage",
    },
  ),
);
