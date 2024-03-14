import Sidebar from "./components/Sidebar";

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout = ({ children }: MainLayoutProps) => {
  return (
    <main className="flex min-h-screen pt-8 dark:bg-slate-900">
      <Sidebar />
      {children}
    </main>
  );
};

export default MainLayout;
