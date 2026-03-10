import { useEffect } from "react";
import { Link } from "react-router-dom";
import { Header } from "@/components/layout/header";
import { useDocumentStore } from "@/stores/document-store";
import { useNotificationStore } from "@/stores/notification-store";
import { useAuthStore } from "@/stores/auth-store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, AlertTriangle, CheckCircle, Clock } from "lucide-react";

export function DashboardPage() {
  const { user } = useAuthStore();
  const { documents, expiringDocs, fetchDocuments, fetchExpiring } = useDocumentStore();
  const { unreadCount, fetchUnreadCount } = useNotificationStore();

  useEffect(() => {
    fetchDocuments();
    fetchExpiring(90);
    fetchUnreadCount();
  }, [fetchDocuments, fetchExpiring, fetchUnreadCount]);

  const activeCount = documents.filter((d) => d.status === "active").length;
  const expiringCount = documents.filter((d) => d.status === "expiring_soon").length;
  const expiredCount = documents.filter((d) => d.status === "expired").length;

  const summaryCards = [
    { label: "Total Documents", value: documents.length, icon: FileText, color: "text-oasis-teal", bg: "bg-oasis-teal/10" },
    { label: "Active", value: activeCount, icon: CheckCircle, color: "text-palm-green", bg: "bg-palm-green/10" },
    { label: "Expiring Soon", value: expiringCount, icon: Clock, color: "text-desert-gold", bg: "bg-desert-gold/10" },
    { label: "Expired", value: expiredCount, icon: AlertTriangle, color: "text-sunset-red", bg: "bg-sunset-red/10" },
  ];

  return (
    <div>
      <Header title={`Welcome, ${user?.full_name?.split(" ")[0] || "User"}`} />
      <div className="p-6 space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {summaryCards.map((card) => (
            <Card key={card.label} className="border-border/50">
              <CardContent className="flex items-center gap-4 pt-6">
                <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${card.bg}`}>
                  <card.icon className={`h-6 w-6 ${card.color}`} />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{card.label}</p>
                  <p className="text-2xl font-bold">{card.value}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Notifications Banner */}
        {unreadCount > 0 && (
          <Card className="border-desert-gold/30 bg-desert-gold/5">
            <CardContent className="flex items-center gap-3 pt-6">
              <AlertTriangle className="h-5 w-5 text-desert-gold" />
              <p className="text-sm">
                You have <strong>{unreadCount}</strong> unread notification{unreadCount > 1 ? "s" : ""}.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Expiring Documents */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-terracotta" />
              Documents Expiring Soon
            </CardTitle>
          </CardHeader>
          <CardContent>
            {expiringDocs.length === 0 ? (
              <p className="text-muted-foreground text-sm">No documents expiring in the next 90 days.</p>
            ) : (
              <div className="space-y-3">
                {expiringDocs.slice(0, 5).map((doc) => {
                  const daysLeft = doc.expiry_date
                    ? Math.ceil((new Date(doc.expiry_date).getTime() - Date.now()) / 86400000)
                    : null;
                  return (
                    <Link
                      key={doc.id}
                      to={`/documents`}
                      className="flex items-center justify-between rounded-lg border border-border/50 px-4 py-3 hover:bg-muted/50 transition-colors"
                    >
                      <div>
                        <p className="font-medium">{doc.title}</p>
                        <p className="text-sm text-muted-foreground">
                          Expires: {doc.expiry_date ? new Date(doc.expiry_date).toLocaleDateString() : "N/A"}
                        </p>
                      </div>
                      <Badge
                        className={
                          daysLeft !== null && daysLeft <= 7
                            ? "bg-sunset-red text-white"
                            : daysLeft !== null && daysLeft <= 30
                            ? "bg-terracotta text-white"
                            : "bg-desert-gold text-white"
                        }
                      >
                        {daysLeft !== null ? `${daysLeft} days` : "Unknown"}
                      </Badge>
                    </Link>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
