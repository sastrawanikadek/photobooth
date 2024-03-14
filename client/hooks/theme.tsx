import { useEffect } from "react";

import { useAppStore } from "@/stores/app";

export const useThemeMode = () => {
  const theme = useAppStore((state) => state.theme);

  useEffect(() => {
    if (
      theme === "dark" ||
      (theme === "system" &&
        window.matchMedia("(prefers-color-scheme: dark)").matches)
    ) {
      document.documentElement.classList.add("dark");
      return;
    }

    document.documentElement.classList.remove("dark");
  }, [theme]);
};
