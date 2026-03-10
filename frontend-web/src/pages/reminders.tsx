import { useEffect, useState } from "react";
import { Header } from "@/components/layout/header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Bell, Check, Clock } from "lucide-react";
import api from "@/lib/api";
import type { Reminder } from "@/types";

export function RemindersPage() {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const fetchReminders = async () => {
    const res = await api.get("/api/v1/reminders/");
    setReminders(res.data);
  };

  useEffect(() => {
    fetchReminders();
  }, []);

  const acknowledge = async (id: string) => {
    await api.post(`/api/v1/reminders/${id}/acknowledge`);
    fetchReminders();
  };

  const snooze = async (id: string) => {
    await api.post(`/api/v1/reminders/${id}/snooze`, { days: 3 });
    fetchReminders();
  };

  const pending = reminders.filter((r) => r.status === "pending");
  const sent = reminders.filter((r) => r.status === "sent");
  const done = reminders.filter((r) => r.status === "acknowledged" || r.status === "snoozed");

  const ReminderCard = ({ reminder }: { reminder: Reminder }) => (
    <div className="flex items-center justify-between rounded-lg border border-border/50 px-4 py-3">
      <div className="flex items-center gap-3">
        <Bell className={`h-5 w-5 ${reminder.status === "sent" ? "text-terracotta" : reminder.status === "pending" ? "text-desert-gold" : "text-palm-green"}`} />
        <div>
          <p className="text-sm font-medium">
            {reminder.days_before ? `${reminder.days_before} days before expiry` : "Custom reminder"}
          </p>
          <p className="text-xs text-muted-foreground">
            {new Date(reminder.remind_at).toLocaleDateString()} via {reminder.channel}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Badge variant="outline" className="text-xs">
          {reminder.status}
        </Badge>
        {(reminder.status === "pending" || reminder.status === "sent") && (
          <>
            <Button size="sm" variant="ghost" onClick={() => acknowledge(reminder.id)}>
              <Check className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="ghost" onClick={() => snooze(reminder.id)}>
              <Clock className="h-4 w-4" />
            </Button>
          </>
        )}
      </div>
    </div>
  );

  return (
    <div>
      <Header title="Reminders" />
      <div className="p-6">
        <Tabs defaultValue="pending">
          <TabsList>
            <TabsTrigger value="pending">Pending ({pending.length})</TabsTrigger>
            <TabsTrigger value="sent">Sent ({sent.length})</TabsTrigger>
            <TabsTrigger value="done">Completed ({done.length})</TabsTrigger>
          </TabsList>
          <TabsContent value="pending" className="space-y-3 mt-4">
            {pending.length === 0 ? (
              <p className="text-muted-foreground text-sm py-8 text-center">No pending reminders</p>
            ) : (
              pending.map((r) => <ReminderCard key={r.id} reminder={r} />)
            )}
          </TabsContent>
          <TabsContent value="sent" className="space-y-3 mt-4">
            {sent.length === 0 ? (
              <p className="text-muted-foreground text-sm py-8 text-center">No sent reminders</p>
            ) : (
              sent.map((r) => <ReminderCard key={r.id} reminder={r} />)
            )}
          </TabsContent>
          <TabsContent value="done" className="space-y-3 mt-4">
            {done.length === 0 ? (
              <p className="text-muted-foreground text-sm py-8 text-center">No completed reminders</p>
            ) : (
              done.map((r) => <ReminderCard key={r.id} reminder={r} />)
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
