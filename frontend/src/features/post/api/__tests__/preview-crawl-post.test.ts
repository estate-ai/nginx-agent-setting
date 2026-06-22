import { beforeEach, describe, expect, it, vi } from "vitest"
import { previewCrawlPost } from "@/features/post/api/preview-crawl-post"

describe("previewCrawlPost", () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })

  it("crawl-preview API에 URL과 keyword를 전달하고 결과를 반환한다", async () => {
    const preview = {
      inputUrl: "https://news.example.com/search?query=프랜차이즈",
      inputUrlType: "SEARCH_RESULT",
      discoveredArticleUrls: ["https://news.example.com/article/1"],
      crawledArticleCount: 1,
      skippedArticleCount: 0,
      usedSelector: "article",
      totalParagraphCount: 10,
      matchedParagraphCount: 3,
      matchedKeywords: ["프랜차이즈", "가맹점"],
      excludedKeywords: [],
      relevanceScore: 0.6,
      extractedTextLength: 500,
      extractedTextPreview: "[기사 1]\n본문",
    }
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(preview), {
        status: 200,
        headers: { "content-type": "application/json" },
      })
    )
    vi.stubGlobal("fetch", fetchMock)

    await expect(
      previewCrawlPost({
        url: "https://news.example.com/search?query=프랜차이즈",
        keyword: "프랜차이즈 창업",
      })
    ).resolves.toEqual(preview)

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/post/api/posts/crawl-preview"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          url: "https://news.example.com/search?query=프랜차이즈",
          keyword: "프랜차이즈 창업",
          rawContent: null,
          visibility: "PUBLIC",
        }),
      })
    )
  })

  it("실패 응답의 detail을 오류 메시지로 반환한다", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "관련 기사가 없습니다." }), {
          status: 422,
          headers: { "content-type": "application/json" },
        })
      )
    )

    await expect(
      previewCrawlPost({
        url: "https://news.example.com/search",
        keyword: null,
      })
    ).rejects.toThrow("관련 기사가 없습니다.")
  })
})
