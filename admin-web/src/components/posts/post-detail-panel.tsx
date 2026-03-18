"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { useToast } from "@/components/toast-provider";
import { updatePost } from "@/lib/api/posts";
import { queryKeys } from "@/lib/query-keys";
import type { CommunityPost, UpdatePostPayload } from "@/lib/types";
import { postFormSchema, type PostFormValues } from "@/lib/validation";

type PostDetailPanelProps = {
  post: CommunityPost;
};

export function PostDetailPanel({ post }: PostDetailPanelProps) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors, isDirty },
  } = useForm<PostFormValues>({
    resolver: zodResolver(postFormSchema),
    defaultValues: {
      visibility: post.visibility,
      state: post.state,
      moderatorNote: "Moderation action will later be sent to backend audit logs.",
    },
  });
  const mutation = useMutation({
    mutationFn: (payload: UpdatePostPayload) => updatePost(post.id, payload),
    onSuccess: async (updated) => {
      showToast({
        tone: "success",
        title: "Post moderation saved",
        description: `Moderation changes for ${updated.author} were saved.`,
      });
      await queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
    },
    onError: () => {
      showToast({
        tone: "error",
        title: "Post moderation failed",
        description: "The moderation changes could not be saved.",
      });
    },
  });

  useEffect(() => {
    reset({
      visibility: post.visibility,
      state: post.state,
      moderatorNote:
        "Moderation action will later be sent to backend audit logs.",
    });
  }, [post, reset]);

  function onSubmit(values: PostFormValues) {
    mutation.mutate(values);
  }

  return (
    <article className="card">
      <h2 className="section-title">Selected post</h2>
      <div className="detail-stack">
        <div className="detail-row">
          <span className="muted">Author</span>
          <strong>{post.author}</strong>
        </div>
        <div className="detail-row">
          <span className="muted">Reports</span>
          <strong>{post.reportsCount}</strong>
        </div>
        <div className="detail-row">
          <span className="muted">Created</span>
          <strong>{post.createdAt}</strong>
        </div>
      </div>

      <div className="card inset-card">
        <p className="muted">Post content</p>
        <p>{post.content}</p>
      </div>

      <div className="form-shell" style={{ marginTop: 16 }}>
        <label className="field">
          <span>Visibility</span>
          <select {...register("visibility")}>
            <option value="PUBLIC">PUBLIC</option>
            <option value="FOLLOWERS">FOLLOWERS</option>
            <option value="PRIVATE">PRIVATE</option>
          </select>
          {errors.visibility ? (
            <p className="field-error">{errors.visibility.message}</p>
          ) : null}
        </label>

        <label className="field">
          <span>Moderation state</span>
          <select {...register("state")}>
            <option value="Published">Published</option>
            <option value="Flagged">Flagged</option>
            <option value="Needs review">Needs review</option>
            <option value="Hidden">Hidden</option>
          </select>
          {errors.state ? (
            <p className="field-error">{errors.state.message}</p>
          ) : null}
        </label>

        <label className="field">
          <span>Moderator note</span>
          <textarea rows={4} {...register("moderatorNote")} />
          {errors.moderatorNote ? (
            <p className="field-error">{errors.moderatorNote.message}</p>
          ) : null}
        </label>

        <p className="form-status muted">
          {isDirty ? "You have unsaved moderation changes." : "No unsaved changes."}
        </p>

        <div className="button-row">
          <button
            type="button"
            className="primary-button"
            onClick={handleSubmit(onSubmit)}
            disabled={mutation.isPending || !isDirty}
          >
            {mutation.isPending ? "Saving..." : "Save moderation"}
          </button>
          <button
            type="button"
            className="ghost-button"
            onClick={() =>
              setValue("state", "Hidden", {
                shouldValidate: true,
                shouldDirty: true,
              })
            }
          >
            Hide post
          </button>
          <button
            type="button"
            className="ghost-button"
            onClick={() =>
              reset({
                visibility: post.visibility,
                state: post.state,
                moderatorNote:
                  "Moderation action will later be sent to backend audit logs.",
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
