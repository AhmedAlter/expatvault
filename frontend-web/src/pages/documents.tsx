import { useEffect, useState } from "react";
import { Header } from "@/components/layout/header";
import { useDocumentStore } from "@/stores/document-store";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, Search, FileText, Upload } from "lucide-react";
import { STATUS_COLORS, STATUS_LABELS } from "@/lib/constants";
import type { Document } from "@/types";

export function DocumentsPage() {
  const { documents, documentTypes, total, isLoading, fetchDocuments, fetchDocumentTypes, uploadDocument } = useDocumentStore();
  const [search, setSearch] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [uploadForm, setUploadForm] = useState({ title: "", document_type_id: "", file: null as File | null });

  useEffect(() => {
    fetchDocuments();
    fetchDocumentTypes();
  }, [fetchDocuments, fetchDocumentTypes]);

  const handleSearch = () => {
    fetchDocuments({ search });
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadForm.title || !uploadForm.document_type_id) return;
    const formData = new FormData();
    formData.append("title", uploadForm.title);
    formData.append("document_type_id", uploadForm.document_type_id);
    if (uploadForm.file) {
      formData.append("file", uploadForm.file);
    }
    try {
      await uploadDocument(formData);
      setDialogOpen(false);
      setUploadForm({ title: "", document_type_id: "", file: null });
      fetchDocuments();
    } catch {
      // error handled by store
    }
  };

  const statusColor = (status: Document["status"]) => STATUS_COLORS[status] || "bg-muted text-foreground";

  return (
    <div>
      <Header title="Documents" />
      <div className="p-6 space-y-6">
        {/* Toolbar */}
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search documents..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-oasis-teal hover:bg-oasis-teal/90 text-white">
                <Plus className="h-4 w-4 mr-2" />
                Upload Document
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Upload Document</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleUpload} className="space-y-4">
                <div className="space-y-2">
                  <Label>Title</Label>
                  <Input
                    placeholder="e.g. My UAE Visa 2026"
                    value={uploadForm.title}
                    onChange={(e) => setUploadForm((f) => ({ ...f, title: e.target.value }))}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Document Type</Label>
                  <select
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={uploadForm.document_type_id}
                    onChange={(e) => setUploadForm((f) => ({ ...f, document_type_id: e.target.value }))}
                    required
                  >
                    <option value="">Select type...</option>
                    {documentTypes.map((dt) => (
                      <option key={dt.id} value={dt.id}>{dt.display_name}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>File (PDF, Image)</Label>
                  <div className="flex items-center gap-3">
                    <label className="flex-1 flex items-center justify-center gap-2 rounded-lg border-2 border-dashed border-border py-8 cursor-pointer hover:bg-muted/50 transition-colors">
                      <Upload className="h-5 w-5 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        {uploadForm.file ? uploadForm.file.name : "Click to upload"}
                      </span>
                      <input
                        type="file"
                        className="hidden"
                        accept=".pdf,.jpg,.jpeg,.png"
                        onChange={(e) => setUploadForm((f) => ({ ...f, file: e.target.files?.[0] || null }))}
                      />
                    </label>
                  </div>
                </div>
                <Button type="submit" className="w-full bg-oasis-teal hover:bg-oasis-teal/90 text-white">
                  Upload
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Document Grid */}
        {isLoading ? (
          <div className="text-center text-muted-foreground py-12">Loading...</div>
        ) : documents.length === 0 ? (
          <div className="text-center py-16">
            <FileText className="h-16 w-16 text-muted-foreground/30 mx-auto mb-4" />
            <p className="text-lg font-medium text-muted-foreground">No documents yet</p>
            <p className="text-sm text-muted-foreground">Upload your first document to get started.</p>
          </div>
        ) : (
          <>
            <p className="text-sm text-muted-foreground">{total} document{total !== 1 ? "s" : ""}</p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {documents.map((doc) => (
                <Card key={doc.id} className="border-border/50 hover:shadow-md hover:-translate-y-0.5 transition-all cursor-pointer">
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-oasis-teal/10">
                        <FileText className="h-5 w-5 text-oasis-teal" />
                      </div>
                      <Badge className={statusColor(doc.status)}>{STATUS_LABELS[doc.status]}</Badge>
                    </div>
                    <h3 className="font-semibold mb-1 truncate">{doc.title}</h3>
                    <p className="text-sm text-muted-foreground mb-2">
                      {doc.ai_classification || "Unclassified"}
                    </p>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>
                        {doc.expiry_date ? `Expires: ${new Date(doc.expiry_date).toLocaleDateString()}` : "No expiry"}
                      </span>
                      <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
