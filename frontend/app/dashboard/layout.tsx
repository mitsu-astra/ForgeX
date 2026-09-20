import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { AuthGuard } from "@/components/AuthGuard";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-[#F8F6F3] text-[#181818] p-4 md:p-5 flex gap-5">
        <Sidebar />
        <div className="flex-1 min-w-0 flex flex-col">
          <Header />
          <main className="flex-1 overflow-y-auto pt-2">
            <div className="animate-fade-in">
              {children}
            </div>
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
