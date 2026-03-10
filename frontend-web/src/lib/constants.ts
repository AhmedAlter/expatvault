export const STATUS_COLORS = {
  active: "bg-palm-green text-white",
  expiring_soon: "bg-desert-gold text-white",
  expired: "bg-sunset-red text-white",
  renewed: "bg-oasis-teal text-white",
} as const;

export const STATUS_LABELS = {
  active: "Active",
  expiring_soon: "Expiring Soon",
  expired: "Expired",
  renewed: "Renewed",
} as const;

export const RELATIONSHIP_LABELS = {
  spouse: "Spouse",
  child: "Child",
  parent: "Parent",
  sibling: "Sibling",
  other: "Other",
} as const;

export const SUBSCRIPTION_FEATURES = {
  free: { maxDocs: 10, familyMembers: 0, channels: ["in_app", "email"] },
  individual_pro: { maxDocs: Infinity, familyMembers: 0, channels: ["in_app", "email", "sms"] },
  family: { maxDocs: Infinity, familyMembers: 5, channels: ["in_app", "email", "sms"] },
} as const;
