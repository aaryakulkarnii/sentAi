import Sidebar from "@/components/layout/Sidebar";
import Topbar from "@/components/layout/Topbar";
import AuthGuard from "@/components/layout/AuthGuard";
import AlertStreamProvider from "@/components/layout/AlertStreamProvider";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <AlertStreamProvider>
        <div className="flex h-screen overflow-hidden">
          <Sidebar />
          <div className="flex flex-1 flex-col overflow-hidden">
            <Topbar />
            <div className="flex-1 overflow-y-auto">{children}</div>
          </div>
        </div>
      </AlertStreamProvider>
    </AuthGuard>
  );
}
