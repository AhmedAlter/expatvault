import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Shield } from "lucide-react";

export function RegisterPage() {
  const [form, setForm] = useState({ email: "", password: "", full_name: "", phone: "", nationality: "" });
  const [error, setError] = useState("");
  const { register, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const update = (field: string, value: string) => setForm((f) => ({ ...f, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await register({
        email: form.email,
        password: form.password,
        full_name: form.full_name,
        phone: form.phone || undefined,
        nationality: form.nationality || undefined,
      });
      navigate("/otp-verify", { state: { email: form.email } });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Registration failed";
      setError(msg);
    }
  };

  return (
    <div className="flex min-h-screen">
      <div className="flex flex-1 items-center justify-center px-6">
        <Card className="w-full max-w-md border-border/50">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <Shield className="h-10 w-10 text-desert-gold" />
            </div>
            <CardTitle className="text-2xl">Create your account</CardTitle>
            <CardDescription>Start managing your UAE documents today</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-lg bg-sunset-red/10 border border-sunset-red/20 px-4 py-3 text-sm text-sunset-red">
                  {error}
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="full_name">Full Name</Label>
                <Input id="full_name" placeholder="Ahmed Khan" value={form.full_name} onChange={(e) => update("full_name", e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="you@example.com" value={form.email} onChange={(e) => update("email", e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Phone (optional)</Label>
                <Input id="phone" placeholder="+971 50 123 4567" value={form.phone} onChange={(e) => update("phone", e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="nationality">Nationality (optional)</Label>
                <Input id="nationality" placeholder="e.g. Indian, Pakistani, Filipino" value={form.nationality} onChange={(e) => update("nationality", e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" placeholder="Min 8 characters" value={form.password} onChange={(e) => update("password", e.target.value)} required minLength={8} />
              </div>
              <Button type="submit" className="w-full bg-oasis-teal hover:bg-oasis-teal/90 text-white" disabled={isLoading}>
                {isLoading ? "Creating account..." : "Create Account"}
              </Button>
              <p className="text-center text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link to="/login" className="text-oasis-teal font-medium hover:underline">
                  Sign in
                </Link>
              </p>
            </form>
          </CardContent>
        </Card>
      </div>

      <div className="hidden lg:flex flex-1 items-center justify-center bg-gradient-to-br from-charcoal to-charcoal/90">
        <div className="text-center text-white px-12">
          <Shield className="h-20 w-20 text-desert-gold mx-auto mb-6" />
          <h2 className="text-3xl font-bold mb-4">Join 8.5M+ Expats</h2>
          <p className="text-white/70 text-lg">
            Stop juggling fragmented government apps.<br />
            One vault for all your documents.
          </p>
        </div>
      </div>
    </div>
  );
}
