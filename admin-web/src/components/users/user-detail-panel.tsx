"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { useToast } from "@/components/toast-provider";
import { updateAdminUser } from "@/lib/api/users";
import { queryKeys } from "@/lib/query-keys";
import type { AdminUser, UpdateAdminUserPayload } from "@/lib/types";
import { userFormSchema, type UserFormValues } from "@/lib/validation";

type UserDetailPanelProps = {
  user: AdminUser;
};

export function UserDetailPanel({ user }: UserDetailPanelProps) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors, isDirty },
  } = useForm<UserFormValues>({
    resolver: zodResolver(userFormSchema),
    defaultValues: {
      role: user.role,
      status: user.status,
      adminNote: "Role and status changes will later be sent to backend audit logs.",
    },
  });
  const mutation = useMutation({
    mutationFn: (payload: UpdateAdminUserPayload) => updateAdminUser(user.id, payload),
    onSuccess: async (updated) => {
      showToast({
        tone: "success",
        title: "User updated",
        description: `${updated.username} was updated successfully.`,
      });
      await queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
    },
    onError: () => {
      showToast({
        tone: "error",
        title: "User update failed",
        description: "The user changes could not be saved.",
      });
    },
  });

  useEffect(() => {
    reset({
      role: user.role,
      status: user.status,
      adminNote:
        "Role and status changes will later be sent to backend audit logs.",
    });
  }, [reset, user]);

  function onSubmit(values: UserFormValues) {
    mutation.mutate(values);
  }

  return (
    <article className="card">
      <h2 className="section-title">Selected user</h2>
      <div className="detail-stack">
        <div className="detail-row">
          <span className="muted">Username</span>
          <strong>{user.username}</strong>
        </div>
        <div className="detail-row">
          <span className="muted">Email</span>
          <strong>{user.email}</strong>
        </div>
        <div className="detail-row">
          <span className="muted">Current role</span>
          <strong>{user.role}</strong>
        </div>
        <div className="detail-row">
          <span className="muted">Status</span>
          <strong>{user.status}</strong>
        </div>
        <div className="detail-row">
          <span className="muted">Eco points</span>
          <strong>{user.ecoPoints}</strong>
        </div>
        <div className="detail-row">
          <span className="muted">Streak days</span>
          <strong>{user.streakDays}</strong>
        </div>
      </div>

      <div className="form-shell">
        <label className="field">
          <span>Role</span>
          <select {...register("role")}>
            <option value="USER">USER</option>
            <option value="MODERATOR">MODERATOR</option>
            <option value="ADMIN">ADMIN</option>
          </select>
          {errors.role ? <p className="field-error">{errors.role.message}</p> : null}
        </label>

        <label className="field">
          <span>Status</span>
          <select {...register("status")}>
            <option value="ACTIVE">ACTIVE</option>
            <option value="REVIEW">REVIEW</option>
            <option value="SUSPENDED">SUSPENDED</option>
          </select>
          {errors.status ? (
            <p className="field-error">{errors.status.message}</p>
          ) : null}
        </label>

        <label className="field">
          <span>Admin note</span>
          <textarea rows={4} {...register("adminNote")} />
          {errors.adminNote ? (
            <p className="field-error">{errors.adminNote.message}</p>
          ) : null}
        </label>

        <p className="form-status muted">
          {isDirty ? "You have unsaved user changes." : "No unsaved changes."}
        </p>

        <div className="button-row">
          <button
            type="button"
            className="primary-button"
            onClick={handleSubmit(onSubmit)}
            disabled={mutation.isPending || !isDirty}
          >
            {mutation.isPending ? "Saving..." : "Save changes"}
          </button>
          <button
            type="button"
            className="ghost-button"
            onClick={() =>
              setValue("status", "SUSPENDED", {
                shouldValidate: true,
                shouldDirty: true,
              })
            }
          >
            Suspend user
          </button>
          <button
            type="button"
            className="ghost-button"
            onClick={() =>
              reset({
                role: user.role,
                status: user.status,
                adminNote:
                  "Role and status changes will later be sent to backend audit logs.",
              })
            }
            disabled={!isDirty}
          >
            Reset
          </button>
        </div>
      </div>
    </article>
  );
}
