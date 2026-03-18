import { apiRequest } from "@/lib/api/client";
import { wait } from "@/lib/api/helpers";
import { isMockMode } from "@/lib/config";
import { mockPosts } from "@/lib/mocks";
import type {
  CommunityPost,
  PostFilters,
  PostMetrics,
  UpdatePostPayload,
} from "@/lib/types";

export async function listPosts(
  filters: PostFilters = {},
): Promise<CommunityPost[]> {
  if (!isMockMode()) {
    const params = new URLSearchParams();
    if (filters.search?.trim()) params.set("search", filters.search.trim());
    if (filters.state && filters.state !== "ALL") {
      params.set("state", filters.state);
    }
    if (filters.visibility && filters.visibility !== "ALL") {
      params.set("visibility", filters.visibility);
    }

    return apiRequest<CommunityPost[]>(
      `/admin/posts${params.size ? `?${params.toString()}` : ""}`,
    );
  }

  await wait(70);

  const query = filters.search?.trim().toLowerCase();
  return mockPosts.filter((post) => {
    const matchesSearch =
      !query ||
      post.author.toLowerCase().includes(query) ||
      post.content.toLowerCase().includes(query);
    const matchesState =
      !filters.state || filters.state === "ALL" || post.state === filters.state;
    const matchesVisibility =
      !filters.visibility ||
      filters.visibility === "ALL" ||
      post.visibility === filters.visibility;

    return matchesSearch && matchesState && matchesVisibility;
  });
}

export async function getPostMetrics(): Promise<PostMetrics> {
  if (!isMockMode()) {
    return apiRequest<PostMetrics>("/admin/posts/metrics");
  }

  await wait(40);

  return {
    totalPosts: mockPosts.length,
    flaggedPosts: mockPosts.filter((post) => post.state === "Flagged").length,
    hiddenPosts: mockPosts.filter((post) => post.state === "Hidden").length,
    totalReports: mockPosts.reduce((sum, post) => sum + post.reportsCount, 0),
  };
}

export async function updatePost(
  postId: string,
  payload: UpdatePostPayload,
): Promise<CommunityPost> {
  if (!isMockMode()) {
    return apiRequest<CommunityPost>(`/admin/posts/${postId}`, {
      method: "PATCH",
      body: payload,
    });
  }

  await wait(120);

  const post = mockPosts.find((item) => item.id === postId);
  if (!post) {
    throw new Error("Post not found");
  }

  return {
    ...post,
    visibility: payload.visibility,
    state: payload.state,
  };
}
