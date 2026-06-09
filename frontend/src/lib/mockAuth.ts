import type { User } from "@/types";

// Dev-only auth bypass. Toggle with NEXT_PUBLIC_MOCK_AUTH in .env.local.
// When enabled, the login page accepts any credentials and AuthGuard
// skips the backend /auth/me call so the UI is usable without the API.
export const MOCK_AUTH = process.env.NEXT_PUBLIC_MOCK_AUTH === "true";

export const MOCK_TOKEN = "mock-dev-token";

export const MOCK_USER: User = {
  id: "00000000-0000-0000-0000-000000000001",
  email: "analyst@sentinelai.dev",
  role: "tier2",
};
