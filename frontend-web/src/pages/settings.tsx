import { useState } from "react";
import { Header } from "@/components/layout/header";
import { useAuthStore } from "@/stores/auth-store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import api from "@/lib/api";

export function SettingsPage() {
  const { user, fetchUser } = useAuthStore();
  const [form, setForm] = useState({
    full_name: user?.full_name || "",
    phone: user?.phone || "",
    nationality: user?.nationality || "",
    emirates_id_number: user?.emirates_id_number || "",
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      await api.patch("/api/v1/users/me", form);
      await fetchUser();
      setMessage("Profile updated successfully");
    } catch {
      setMessage("Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  const tierLabels = { free: "Free", individual_pro: "Pro", family: "Family" };

  return (
    <div>
      <Header title="Settings" />
      <div className="p-6">
        <Tabs defaultValue="profile">
          <TabsList>
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="subscription">Subscription</TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="mt-4">
            <Card className="max-w-lg border-border/50">
              <CardHeader>
                <CardTitle>Profile Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSave} className="space-y-4">
                  {message && (
                    <div className="rounded-lg bg-oasis-teal/10 border border-oasis-teal/20 px-4 py-3 text-sm text-oasis-teal">
                      {message}
                    </div>
                  )}
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input value={user?.email || ""} disabled className="bg-muted" />
                  </div>
                  <div className="space-y-2">
                    <Label>Full Name</Label>
                    <Input value={form.full_name} onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))} />
                  </div>
                  <div className="space-y-2">
                    <Label>Phone</Label>
                    <Input value={form.phone} onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))} placeholder="+971..." />
                  </div>
                  <div className="space-y-2">
                    <Label>Nationality</Label>
                    <Input value={form.nationality} onChange={(e) => setForm((f) => ({ ...f, nationality: e.target.value }))} />
                  </div>
                  <div className="space-y-2">
                    <Label>Emirates ID Number</Label>
                    <Input value={form.emirates_id_number} onChange={(e) => setForm((f) => ({ ...f, emirates_id_number: e.target.value }))} placeholder="784-XXXX-XXXXXXX-X" />
                  </div>
                  <Button type="submit" className="bg-oasis-teal hover:bg-oasis-teal/90 text-white" disabled={saving}>
                    {saving ? "Saving..." : "Save Changes"}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="subscription" className="mt-4">
            <Card className="max-w-lg border-border/50">
              <CardHeader>
                <CardTitle>Subscription</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground">Current Plan:</span>
                  <Badge className="bg-oasis-teal text-white">
                    {tierLabels[user?.subscription_tier as keyof typeof tierLabels] || "Free"}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  {user?.subscription_tier === "free"
                    ? "You're on the Free plan. Upgrade for unlimited documents and SMS reminders."
                    : "Thank you for being a premium subscriber!"}
                </p>
                {user?.subscription_tier === "free" && (
                  <div className="flex gap-3">
                    <Button className="bg-desert-gold hover:bg-desert-gold/90 text-white">
                      Upgrade to Pro — AED 15/mo
                    </Button>
                    <Button variant="outline">
                      Family — AED 25/mo
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
