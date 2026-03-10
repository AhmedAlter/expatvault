import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Shield, FileText, Bell, Users, Brain, Globe } from "lucide-react";

const features = [
  { icon: FileText, title: "Document Vault", desc: "Store all UAE documents in one secure place with OCR scanning." },
  { icon: Bell, title: "Smart Reminders", desc: "Never miss a renewal. Dependency-aware alerts via app, email & SMS." },
  { icon: Users, title: "Family Dashboard", desc: "Manage documents for up to 5 family members in one account." },
  { icon: Brain, title: "AI-Powered", desc: "Auto-classify documents, extract dates, and get renewal guidance." },
  { icon: Globe, title: "Cross-Emirate", desc: "Works across all 7 emirates. One tool for all government services." },
  { icon: Shield, title: "Bank-Grade Security", desc: "Encrypted storage, JWT auth, and secure document handling." },
];

const pricing = [
  { name: "Free", price: "0", features: ["10 documents", "Email reminders", "OCR scanning", "Basic dashboard"], cta: "Get Started" },
  { name: "Pro", price: "15", features: ["Unlimited documents", "SMS + Email reminders", "AI assistant", "Priority support"], cta: "Start Pro", popular: true },
  { name: "Family", price: "25", features: ["Everything in Pro", "Up to 5 family members", "Family dashboard", "Shared reminders"], cta: "Start Family" },
];

export function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <div className="relative overflow-hidden bg-gradient-to-br from-sand via-desert-gold/20 to-oasis-teal/10">
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23264653' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")" }} />
        <nav className="relative z-10 flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
          <div className="flex items-center gap-2">
            <Shield className="h-8 w-8 text-desert-gold" />
            <span className="text-xl font-bold text-charcoal">ExpatVault</span>
          </div>
          <div className="flex gap-3">
            <Link to="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link to="/register">
              <Button className="bg-oasis-teal hover:bg-oasis-teal/90 text-white">Get Started</Button>
            </Link>
          </div>
        </nav>

        <div className="relative z-10 max-w-4xl mx-auto text-center px-6 py-24">
          <h1 className="text-5xl font-bold text-charcoal mb-6 leading-tight">
            Never Miss a Document<br />Renewal Again
          </h1>
          <p className="text-xl text-charcoal/70 mb-8 max-w-2xl mx-auto">
            The smart document vault for UAE expats. Track visas, Emirates ID, insurance & more with
            AI-powered OCR and dependency-aware reminders.
          </p>
          <div className="flex justify-center gap-4">
            <Link to="/register">
              <Button size="lg" className="bg-oasis-teal hover:bg-oasis-teal/90 text-white px-8 text-lg">
                Start Free
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="border-charcoal/20 text-charcoal px-8 text-lg">
              Watch Demo
            </Button>
          </div>
          <p className="mt-4 text-sm text-charcoal/50">
            Avoid AED 50/day visa fines & AED 20/day Emirates ID penalties
          </p>
        </div>
      </div>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <h2 className="text-3xl font-bold text-center text-charcoal mb-12">Everything You Need</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((f) => (
            <Card key={f.title} className="border-border/50 hover:shadow-lg transition-shadow hover:-translate-y-1 duration-200">
              <CardContent className="pt-6">
                <f.icon className="h-10 w-10 text-oasis-teal mb-4" />
                <h3 className="text-lg font-semibold text-charcoal mb-2">{f.title}</h3>
                <p className="text-muted-foreground">{f.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section className="bg-sand/50 px-6 py-20">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-charcoal mb-12">Simple Pricing</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {pricing.map((p) => (
              <Card key={p.name} className={`relative ${p.popular ? "border-oasis-teal border-2 shadow-lg" : "border-border/50"}`}>
                {p.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-oasis-teal text-white text-xs font-bold px-3 py-1 rounded-full">
                    Most Popular
                  </div>
                )}
                <CardContent className="pt-8 text-center">
                  <h3 className="text-lg font-semibold text-charcoal">{p.name}</h3>
                  <div className="my-4">
                    <span className="text-4xl font-bold text-charcoal">AED {p.price}</span>
                    <span className="text-muted-foreground">/mo</span>
                  </div>
                  <ul className="space-y-2 text-sm text-muted-foreground mb-6">
                    {p.features.map((f) => (
                      <li key={f}>{f}</li>
                    ))}
                  </ul>
                  <Link to="/register">
                    <Button className={`w-full ${p.popular ? "bg-oasis-teal hover:bg-oasis-teal/90 text-white" : ""}`} variant={p.popular ? "default" : "outline"}>
                      {p.cta}
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-charcoal text-white/70 px-6 py-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-desert-gold" />
            <span className="font-semibold text-white">ExpatVault</span>
          </div>
          <p className="text-sm">&copy; 2026 ExpatVault. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
