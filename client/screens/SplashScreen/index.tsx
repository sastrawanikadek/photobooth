import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Progress } from "@/components/Progress";

const SplashScreen = () => {
  const navigate = useNavigate();
  const progress = useMockProgress();

  useEffect(() => {
    if (progress >= 100) {
      navigate("/settings", { replace: true });
    }
  }, [progress]);

  return (
    <main className="flex h-screen items-center justify-center dark:bg-slate-900">
      <div className="flex w-full max-w-md flex-col items-center gap-4 py-4">
        <img
          src="/images/logo.png"
          alt="Parisudha Technology Logo"
          width={125}
        />
        <Progress value={progress} />
      </div>
    </main>
  );
};

const useMockProgress = () => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      if (progress >= 100) {
        clearInterval(interval);
        return;
      }

      const increment = Math.random() * 20;
      setProgress((prev) => (prev + increment > 100 ? 100 : prev + increment));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return progress;
};

export default SplashScreen;
