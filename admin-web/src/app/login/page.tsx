"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

import { useAuth } from "@/components/auth-provider";
import { loginSchema, type LoginFormValues } from "@/lib/validation";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "akmaral@ecoiz.app",
      password: "admin123",
    },
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
          Mock credentials are prefilled. Replace this flow with backend auth
          when the real admin API is ready.
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
            {isDirty ? "You have unsaved login changes." : "Mock credentials are ready."}
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
              onClick={() =>
                reset({
                  email: "akmaral@ecoiz.app",
                  password: "admin123",
                })
              }
            >
              Reset
            </button>
          </div>
        </form>

        <div className="auth-hint">
          <strong>Mock accounts</strong>
          <p className="muted">`akmaral@ecoiz.app / admin123`</p>
          <p className="muted">`nurdana@ecoiz.app / moderator123`</p>
        </div>
      </div>
    </div>
  );
}
