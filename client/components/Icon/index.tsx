import { createElement } from "react";

import { cn } from "@/utils/tailwind";

interface IconProps extends Omit<React.SVGAttributes<SVGElement>, "children"> {
  as: React.ElementType;
}

const Icon = ({ as, className, ...props }: IconProps) => {
  return createElement(as, {
    ...props,
    className: cn("h-6 w-6 dark:text-white", className),
  });
};

export default Icon;
