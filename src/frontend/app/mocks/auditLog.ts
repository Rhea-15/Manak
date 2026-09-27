export const mockAuditLog = [
  {
    id: 1,
    timestamp: "2026-09-20T10:15:00Z",
    actor: "admin_1",
    action: "APPROVED",
    target: "Standard IS 1239 update",
  },
  {
    id: 2,
    timestamp: "2026-09-21T14:30:00Z",
    actor: "admin_2",
    action: "REJECTED",
    target: "Vendor bid - Steel Rod tender",
  },
  {
    id: 3,
    timestamp: "2026-09-22T09:00:00Z",
    actor: "admin_1",
    action: "APPROVED",
    target: "Standard IS 269 amendment",
  },
];

export const mockReviewQueue = [
  {
    id: 1,
    itemName: "Cement Grade Certification",
    status: "pending_review",
    submittedBy: "vendor_45",
  },
  {
    id: 2,
    itemName: "Steel Rod Compliance Check",
    status: "pending_review",
    submittedBy: "vendor_12",
  },
];