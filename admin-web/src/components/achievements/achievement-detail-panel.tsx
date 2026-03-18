"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { useToast } from "@/components/toast-provider";
import { updateAchievement } from "@/lib/api/achievements";
import { queryKeys } from "@/lib/query-keys";
import type { Achievement, UpdateAchievementPayload } from "@/lib/types";
import {
  achievementFormSchema,
  type AchievementFormValues,
} from "@/lib/validation";

type AchievementDetailPanelProps = {
  achievement: Achievement;
};

export function AchievementDetailPanel({
  achievement,
}: AchievementDetailPanelProps) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors, isDirty },
  } = useForm<AchievementFormValues>({
    resolver: zodResolver(achievementFormSchema),
    defaultValues: {
      title: achievement.title,
      description: achievement.description,
      icon: achievement.icon,
      targetValue: achievement.targetValue,
      rewardPoints: achievement.rewardPoints,
    },
  });
  const mutation = useMutation({
    mutationFn: (payload: UpdateAchievementPayload) =>
      updateAchievement(achievement.id, payload),
    onSuccess: async (updated) => {
      showToast({
        tone: "success",
        title: "Achievement updated",
        description: `${updated.title} was updated successfully.`,
      });
      await queryClient.invalidateQueries({
        queryKey: queryKeys.achievements.all,
      });
    },
    onError: () => {
      showToast({
        tone: "error",
        title: "Achievement update failed",
        description: "The achievement changes could not be saved.",
      });
    },
  });

  useEffect(() => {
    reset({
      title: achievement.title,
      description: achievement.description,
      icon: achievement.icon,
      targetValue: achievement.targetValue,
      rewardPoints: achievement.rewardPoints,
    });
  }, [achievement, reset]);

  function onSubmit(values: AchievementFormValues) {
    mutation.mutate(values);
  }

  return (
    <article className="card">
      <h2 className="section-title">Selected achievement</h2>
      <div className="detail-stack">
        <div className="detail-row">
          <span className="muted">Title</span>
          <strong>{achievement.title}</strong>
        </div>
        <div className="detail-row">
          <span className="muted">Icon</span>
          <strong>{achievement.icon}</strong>
        </div>
        <div className="detail-row">
          <span className="muted">Target</span>
          <strong>{achievement.targetValue}</strong>
        </div>
      </div>

      <div className="form-shell">
        <label className="field">
          <span>Title</span>
          <input {...register("title")} />
          {errors.title ? (
            <p className="field-error">{errors.title.message}</p>
          ) : null}
        </label>

        <label className="field">
          <span>Description</span>
          <textarea rows={4} {...register("description")} />
          {errors.description ? (
            <p className="field-error">{errors.description.message}</p>
          ) : null}
        </label>

        <div className="form-grid-two">
          <label className="field">
            <span>Icon</span>
            <input {...register("icon")} />
            {errors.icon ? <p className="field-error">{errors.icon.message}</p> : null}
          </label>

          <label className="field">
            <span>Target value</span>
            <input
              type="number"
              {...register("targetValue", { valueAsNumber: true })}
            />
            {errors.targetValue ? (
              <p className="field-error">{errors.targetValue.message}</p>
            ) : null}
          </label>

          <label className="field">
            <span>Reward points</span>
            <input
              type="number"
              {...register("rewardPoints", { valueAsNumber: true })}
            />
            {errors.rewardPoints ? (
              <p className="field-error">{errors.rewardPoints.message}</p>
            ) : null}
          </label>
        </div>

        <p className="form-status muted">
          {isDirty ? "You have unsaved achievement changes." : "No unsaved changes."}
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
              setValue("rewardPoints", achievement.rewardPoints + 10, {
                shouldValidate: true,
                shouldDirty: true,
              })
            }
          >
            Add 10 reward points
          </button>
          <button
            type="button"
            className="ghost-button"
            onClick={() =>
              reset({
                title: achievement.title,
                description: achievement.description,
                icon: achievement.icon,
                targetValue: achievement.targetValue,
                rewardPoints: achievement.rewardPoints,
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
