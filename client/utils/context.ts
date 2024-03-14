import { useContext as reactUseContext } from "react";

export const useContext = <T>(context: React.Context<T | null>) => {
  const value = reactUseContext(context);

  if (value === null) {
    throw new Error("useContext must be inside a Provider with a value");
  }

  return value;
};
