import { createHashRouter } from "react-router-dom";

import SettingsScreen from "./screens/SettingsScreen";
import SplashScreen from "./screens/SplashScreen";

const router = createHashRouter([
  {
    path: "/",
    element: <SplashScreen />,
  },
  {
    path: "/settings",
    element: <SettingsScreen />,
  },
]);

export default router;
