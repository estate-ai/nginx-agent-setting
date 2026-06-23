import type {
  CrawlPreview,
  CreateCrawlSummaryPostInput,
} from "@/features/post/types/post"

const crawlPreviewApiUrl = `${process.env.NEXT_PUBLIC_API_ORIGIN ?? "http://localhost:8088"}/api/post/api/posts/crawl-preview`

export async function previewCrawlPost(
  input: Pick<CreateCrawlSummaryPostInput, "url" | "keyword">
): Promise<CrawlPreview> {
  const response = await fetch(crawlPreviewApiUrl, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ ...input, rawContent: null, visibility: "PUBLIC" }),
  })
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as {
      detail?: string
      message?: string
    } | null
    throw new Error(
      body?.detail ?? body?.message ?? "크롤링 미리보기에 실패했습니다."
    )
  }
  return response.json() as Promise<CrawlPreview>
}
