import { AiOutlineSetting } from "react-icons/ai";
import { Link } from "react-router-dom";

import { Button } from "@/components/Button";
import Icon from "@/components/Icon";
import Tooltip from "@/components/Tooltip";

const Sidebar = () => {
  return (
    <aside className="flex flex-col items-center justify-between border-r border-r-slate-700">
      <div className="px-2 py-4">
        <img
          src="/images/logo.png"
          alt="Parisudha Technology Logo"
          width={40}
        />
      </div>
      <div className="border-t border-t-slate-700 px-2 py-4">
        <Tooltip content="Settings" side="right">
          <Button variant="ghost" size="icon" asChild>
            <Link to="/settings">
              <Icon as={AiOutlineSetting} />
            </Link>
          </Button>
        </Tooltip>
      </div>
    </aside>
  );
};

export default Sidebar;
