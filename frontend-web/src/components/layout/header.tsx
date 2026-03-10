import { Bell } from "lucide-react";
import { useNotificationStore } from "@/stores/notification-store";
import { Button } from "@/components/ui/button";

export function Header({ title }: { title: string }) {
  const { unreadCount } = useNotificationStore();

  return (
    <header className="flex items-center justify-between border-b border-border bg-card px-6 py-4">
      <h1 className="text-2xl font-bold text-foreground">{title}</h1>
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-sunset-red text-[10px] font-bold text-white px-1">
              {unreadCount}
            </span>
          )}
        </Button>
      </div>
    </header>
  );
}
