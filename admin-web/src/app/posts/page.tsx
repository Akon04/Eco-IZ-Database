import { PageHeader } from "@/components/page-header";
import { PostsWorkspace } from "@/components/posts/posts-workspace";
import { getPostMetrics, listPosts } from "@/lib/api/posts";

export default async function PostsPage() {
  const [posts, metrics] = await Promise.all([listPosts(), getPostMetrics()]);

  return (
    <>
      <PageHeader
        title="Posts"
        description="Moderate community content and review visibility issues."
      />
      <PostsWorkspace initialPosts={posts} metrics={metrics} />
    </>
  );
}
