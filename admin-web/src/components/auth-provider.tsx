"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getCurrentAdmin, loginAdmin } from "@/lib/api/auth";
import {
  clearStoredSession,
  loadStoredSession,
  storeSession,
} from "@/lib/auth-storage";
import { queryKeys } from "@/lib/query-keys";
import type { AuthAdmin, AuthSession, LoginPayload } from "@/lib/types";

type AuthContextValue = {
  user: AuthAdmin | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [token, setToken] = useState<string | null>(null);
  const [hasHydrated, setHasHydrated] = useState(false);

  useEffect(() => {
    const storedSession = loadStoredSession();
    if (storedSession) {
      setToken(storedSession.token);
      queryClient.setQueryData(queryKeys.auth.me, storedSession.user);
    }

    setHasHydrated(true);
  }, [queryClient]);

  const authQuery = useQuery({
    queryKey: queryKeys.auth.me,
    queryFn: async () => {
      if (!token) {
        return null;
      }

      try {
        return await getCurrentAdmin(token);
      } catch (error) {
        clearStoredSession();
        setToken(null);
        throw error;
      }
    },
    enabled: Boolean(token),
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: loginAdmin,
    onSuccess: (session: AuthSession) => {
      storeSession(session);
      setToken(session.token);
      queryClient.setQueryData(queryKeys.auth.me, session.user);
    },
  });

  async function login(payload: LoginPayload) {
    await loginMutation.mutateAsync(payload);
  }

  function logout() {
    clearStoredSession();
    setToken(null);
    queryClient.setQueryData(queryKeys.auth.me, null);
    queryClient.removeQueries({ queryKey: queryKeys.users.all });
    queryClient.removeQueries({ queryKey: queryKeys.categories.all });
    queryClient.removeQueries({ queryKey: queryKeys.habits.all });
    queryClient.removeQueries({ queryKey: queryKeys.achievements.all });
    queryClient.removeQueries({ queryKey: queryKeys.posts.all });
  }

  const user = authQuery.data ?? null;
  const isLoading = authQuery.isLoading || loginMutation.isPending;

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isLoading: !hasHydrated || isLoading,
      isAuthenticated: Boolean(user && token),
      login,
      logout,
    }),
    [hasHydrated, isLoading, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
