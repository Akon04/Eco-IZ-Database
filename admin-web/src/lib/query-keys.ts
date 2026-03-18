export const queryKeys = {
  auth: {
    me: ["auth", "me"] as const,
  },
  users: {
    all: ["users"] as const,
    list: (filters: string) => ["users", "list", filters] as const,
    metrics: ["users", "metrics"] as const,
  },
  categories: {
    all: ["categories"] as const,
    list: (filters: string) => ["categories", "list", filters] as const,
    metrics: ["categories", "metrics"] as const,
  },
  habits: {
    all: ["habits"] as const,
    list: (filters: string) => ["habits", "list", filters] as const,
    metrics: ["habits", "metrics"] as const,
  },
  achievements: {
    all: ["achievements"] as const,
    list: (filters: string) => ["achievements", "list", filters] as const,
    metrics: ["achievements", "metrics"] as const,
  },
  posts: {
    all: ["posts"] as const,
    list: (filters: string) => ["posts", "list", filters] as const,
    metrics: ["posts", "metrics"] as const,
  },
};
