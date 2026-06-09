import Sidebar from "@/components/layout/Sidebar";
import AuthGuard from "@/components/layout/AuthGuard";
import AlertStreamProvider from "@/components/layout/AlertStreamProvider";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <AlertStreamProvider>
        <div className="flex h-screen overflow-hidden">
          <Sidebar />
          <div className="flex-1 overflow-y-auto">{children}</div>
        </div>
      </AlertStreamProvider>
    </AuthGuard>
  );
}
