import { useEffect, useState } from "react";
import { Header } from "@/components/layout/header";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, Users } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import api from "@/lib/api";
import type { FamilyMember } from "@/types";
import { RELATIONSHIP_LABELS } from "@/lib/constants";

export function FamilyPage() {
  const { user } = useAuthStore();
  const [members, setMembers] = useState<FamilyMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState({ full_name: "", relationship: "spouse" as string, nationality: "" });
  const [error, setError] = useState("");

  const isFamilyTier = user?.subscription_tier === "family";

  const fetchMembers = async () => {
    if (!isFamilyTier) { setLoading(false); return; }
    setLoading(true);
    try {
      const res = await api.get("/api/v1/family/members");
      setMembers(res.data);
    } catch {
      // may not have access
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMembers();
  }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/api/v1/family/members", form);
      setDialogOpen(false);
      setForm({ full_name: "", relationship: "spouse", nationality: "" });
      fetchMembers();
    } catch (err: unknown) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Failed to add member");
    }
  };

  if (!isFamilyTier) {
    return (
      <div>
        <Header title="Family" />
        <div className="flex flex-col items-center justify-center py-24 px-6">
          <Users className="h-16 w-16 text-muted-foreground/30 mb-4" />
          <h2 className="text-xl font-semibold mb-2">Family Plan Required</h2>
          <p className="text-muted-foreground text-center max-w-md">
            Upgrade to the Family plan (AED 25/mo) to manage documents for up to 5 family members.
          </p>
          <Button className="mt-6 bg-oasis-teal hover:bg-oasis-teal/90 text-white">Upgrade Now</Button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Header title="Family" />
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">{members.length}/5 members</p>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger>
              <Button className="bg-oasis-teal hover:bg-oasis-teal/90 text-white" disabled={members.length >= 5}>
                <Plus className="h-4 w-4 mr-2" />
                Add Member
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Family Member</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleAdd} className="space-y-4">
                {error && (
                  <div className="rounded-lg bg-sunset-red/10 border border-sunset-red/20 px-4 py-3 text-sm text-sunset-red">{error}</div>
                )}
                <div className="space-y-2">
                  <Label>Full Name</Label>
                  <Input value={form.full_name} onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))} required />
                </div>
                <div className="space-y-2">
                  <Label>Relationship</Label>
                  <select
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={form.relationship}
                    onChange={(e) => setForm((f) => ({ ...f, relationship: e.target.value }))}
                  >
                    {Object.entries(RELATIONSHIP_LABELS).map(([k, v]) => (
                      <option key={k} value={k}>{v}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Nationality (optional)</Label>
                  <Input value={form.nationality} onChange={(e) => setForm((f) => ({ ...f, nationality: e.target.value }))} />
                </div>
                <Button type="submit" className="w-full bg-oasis-teal hover:bg-oasis-teal/90 text-white">Add Member</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {loading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : members.length === 0 ? (
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
            <p className="text-muted-foreground">No family members added yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {members.map((m) => (
              <Card key={m.id} className="border-border/50 hover:shadow-md transition-shadow">
                <CardContent className="flex items-center gap-4 pt-6">
                  <Avatar className="h-12 w-12">
                    <AvatarFallback className="bg-desert-gold/20 text-desert-gold font-bold">
                      {m.full_name.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold">{m.full_name}</p>
                    <p className="text-sm text-muted-foreground capitalize">{m.relationship}</p>
                    {m.nationality && <p className="text-xs text-muted-foreground">{m.nationality}</p>}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
