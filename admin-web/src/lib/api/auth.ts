import { apiRequest } from "@/lib/api/client";
import { wait } from "@/lib/api/helpers";
import { isMockMode } from "@/lib/config";
import type { AuthAdmin, AuthSession, LoginPayload } from "@/lib/types";

const mockAdmins: Array<AuthAdmin & { password: string }> = [
  {
    id: "admin-1",
    email: "akmaral@ecoiz.app",
    username: "akmaral",
    role: "ADMIN",
    password: "admin123",
  },
  {
    id: "admin-2",
    email: "nurdana@ecoiz.app",
    username: "nurdana",
    role: "MODERATOR",
    password: "moderator123",
  },
];

function buildMockSession(admin: AuthAdmin): AuthSession {
  return {
    token: `mock-token-${admin.id}`,
    user: admin,
  };
}

export async function loginAdmin(payload: LoginPayload): Promise<AuthSession> {
  if (!isMockMode()) {
    return apiRequest<AuthSession>("/admin/login", {
      method: "POST",
      body: payload,
    });
  }

  await wait(120);

  const admin = mockAdmins.find(
    (item) =>
      item.email.toLowerCase() === payload.email.toLowerCase() &&
      item.password === payload.password,
  );

  if (!admin) {
    throw new Error("Invalid email or password");
  }

  return buildMockSession({
    id: admin.id,
    email: admin.email,
    username: admin.username,
    role: admin.role,
  });
}

export async function getCurrentAdmin(token: string): Promise<AuthAdmin> {
  if (!isMockMode()) {
    return apiRequest<AuthAdmin>("/admin/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  await wait(60);

  const adminId = token.replace("mock-token-", "");
  const admin = mockAdmins.find((item) => item.id === adminId);
  if (!admin) {
    throw new Error("Session expired");
  }

  return {
    id: admin.id,
    email: admin.email,
    username: admin.username,
    role: admin.role,
  };
}
