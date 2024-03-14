import { RouterProvider } from "react-router-dom";

import { TooltipProvider } from "./components/Tooltip";
import { useThemeMode } from "./hooks/theme";
import TitleBar from "./layouts/TitleBar";
import router from "./routes";

const App = () => {
  useThemeMode();

  return (
    <TooltipProvider delayDuration={200}>
      <TitleBar />
      <RouterProvider router={router} />
    </TooltipProvider>
  );
};

export default App;
