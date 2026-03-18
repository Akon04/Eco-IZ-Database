"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { useToast } from "@/components/toast-provider";
import { updateCategory } from "@/lib/api/categories";
import { queryKeys } from "@/lib/query-keys";
import type { EcoCategory, UpdateCategoryPayload } from "@/lib/types";
import {
  categoryFormSchema,
  type CategoryFormValues,
} from "@/lib/validation";

type CategoryDetailPanelProps = {
  category: EcoCategory;
};

export function CategoryDetailPanel({ category }: CategoryDetailPanelProps) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const { register, handleSubmit, reset, setValue, formState: { errors, isDirty } } =
    useForm<CategoryFormValues>({
      resolver: zodResolver(categoryFormSchema),
      defaultValues: {
        name: category.name,
        description: category.description,
        color: category.color,
        icon: category.icon,
      },
    });
  const mutation = useMutation({
    mutationFn: (payload: UpdateCategoryPayload) => updateCategory(category.id, payload),
    onSuccess: async (updated) => {
      showToast({
        tone: "success",
        title: "Category updated",
        description: `${updated.name} was updated successfully.`,
      });
      await queryClient.invalidateQueries({ queryKey: queryKeys.categories.all });
    },
    onError: () => {
      showToast({
        tone: "error",
        title: "Category update failed",
        description: "The category changes could not be saved.",
      });
    },
  });

  useEffect(() => {
    reset({
      name: category.name,
      description: category.description,
      color: category.color,
      icon: category.icon,
    });
  }, [category, reset]);

  function onSubmit(values: CategoryFormValues) {
    mutation.mutate(values);
  }

  return (
    <article className="card">
      <h2 className="section-title">Selected category</h2>
      <div className="detail-stack">
        <div className="detail-row">
          <span className="muted">Name</span>
          <strong>{category.name}</strong>
        </div>
        <div className="detail-row">
          <span className="muted">Color</span>
          <strong>{category.color}</strong>
        </div>
        <div className="detail-row">
          <span className="muted">Icon</span>
          <strong>{category.icon}</strong>
        </div>
      </div>

      <div className="form-shell">
        <label className="field">
          <span>Name</span>
          <input {...register("name")} />
          {errors.name ? <p className="field-error">{errors.name.message}</p> : null}
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
            <span>Color</span>
            <input {...register("color")} />
            {errors.color ? (
              <p className="field-error">{errors.color.message}</p>
            ) : null}
          </label>

          <label className="field">
            <span>Icon</span>
            <input {...register("icon")} />
            {errors.icon ? <p className="field-error">{errors.icon.message}</p> : null}
          </label>
        </div>

        <p className="form-status muted">
          {isDirty ? "You have unsaved category changes." : "No unsaved changes."}
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
              setValue("color", category.color.toLowerCase(), {
                shouldValidate: true,
                shouldDirty: true,
              })
            }
          >
            Normalize color
          </button>
          <button
            type="button"
            className="ghost-button"
            onClick={() =>
              reset({
                name: category.name,
                description: category.description,
                color: category.color,
                icon: category.icon,
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
