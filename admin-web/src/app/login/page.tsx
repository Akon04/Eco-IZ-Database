"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

import { useAuth } from "@/components/auth-provider";
import { isMockMode } from "@/lib/config";
import { loginSchema, type LoginFormValues } from "@/lib/validation";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const mockMode = isMockMode();
  const defaultCredentials = mockMode
    ? {
        email: "akmaral@ecoiz.app",
        password: "admin123",
      }
    : {
        email: "admin@ecoiz.app",
        password: "admin123",
      };
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: defaultCredentials,
  });

  async function onSubmit(values: LoginFormValues) {
    try {
      await login(values);
      router.replace("/");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Login failed. Try again.";
      setError("root", { message });
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <p className="auth-kicker">ECOIZ admin access</p>
        <h1 className="auth-title">Sign in to the moderation workspace</h1>
        <p className="muted">
          {mockMode
            ? "Mock credentials are prefilled for UI development."
            : "Live backend mode is enabled. Use the seeded admin account to sign in."}
        </p>

        <form className="form-shell" onSubmit={handleSubmit(onSubmit)}>
          <label className="field">
            <span>Email</span>
            <input type="email" {...register("email")} />
            {errors.email ? (
              <p className="field-error">{errors.email.message}</p>
            ) : null}
          </label>

          <label className="field">
            <span>Password</span>
            <input type="password" {...register("password")} />
            {errors.password ? (
              <p className="field-error">{errors.password.message}</p>
            ) : null}
          </label>

          {errors.root ? (
            <p className="error-message">{errors.root.message}</p>
          ) : null}

          <p className="form-status muted">
            {isDirty
              ? "You have unsaved login changes."
              : mockMode
                ? "Mock credentials are ready."
                : "Live admin credentials are ready."}
          </p>

          <div className="button-row">
            <button
              type="submit"
              className="primary-button"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
            <button
              type="button"
              className="ghost-button"
              onClick={() => reset(defaultCredentials)}
            >
              Reset
            </button>
          </div>
        </form>

        <div className="auth-hint">
          <strong>{mockMode ? "Mock accounts" : "Live backend account"}</strong>
          {mockMode ? (
            <>
              <p className="muted">`akmaral@ecoiz.app / admin123`</p>
              <p className="muted">`nurdana@ecoiz.app / moderator123`</p>
            </>
          ) : (
            <p className="muted">`admin@ecoiz.app / admin123`</p>
          )}
        </div>
      </div>
    </div>
  );
}
