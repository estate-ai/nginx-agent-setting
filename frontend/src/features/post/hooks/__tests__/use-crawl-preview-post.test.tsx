import { beforeEach, describe, expect, it, vi } from "vitest"
import { act, renderHook, waitFor } from "@testing-library/react"
import { previewCrawlPost } from "@/features/post/api/preview-crawl-post"
import { useCrawlPreviewPost } from "@/features/post/hooks/use-crawl-preview-post"

vi.mock("@/features/post/api/preview-crawl-post", () => ({
  previewCrawlPost: vi.fn(),
}))

describe("useCrawlPreviewPost", () => {
  beforeEach(() => {
    vi.mocked(previewCrawlPost).mockReset()
  })

  it("preview 성공 상태를 저장한다", async () => {
    const preview = {
      inputUrl: "https://news.example.com/search",
      inputUrlType: "SEARCH_RESULT" as const,
      discoveredArticleUrls: [],
      crawledArticleCount: 2,
      skippedArticleCount: 0,
      usedSelector: "article",
      totalParagraphCount: 10,
      matchedParagraphCount: 3,
      matchedKeywords: ["프랜차이즈"],
      excludedKeywords: [],
      relevanceScore: 0.5,
      extractedTextLength: 300,
      extractedTextPreview: "미리보기 본문",
    }
    vi.mocked(previewCrawlPost).mockResolvedValue(preview)
    const { result } = renderHook(() => useCrawlPreviewPost())

    await act(() =>
      result.current.preview(
        " https://news.example.com/search ",
        " 프랜차이즈 "
      )
    )

    expect(result.current.data).toEqual(preview)
    expect(result.current.error).toBeNull()
    expect(result.current.isLoading).toBe(false)
    expect(previewCrawlPost).toHaveBeenCalledWith({
      url: "https://news.example.com/search",
      keyword: "프랜차이즈",
    })
  })

  it("preview 실패 메시지를 저장한다", async () => {
    vi.mocked(previewCrawlPost).mockRejectedValue(new Error("미리보기 실패"))
    const { result } = renderHook(() => useCrawlPreviewPost())

    await act(async () => {
      await result.current
        .preview("https://news.example.com/search", "")
        .catch(() => undefined)
    })

    await waitFor(() => expect(result.current.error).toBe("미리보기 실패"))
    expect(result.current.data).toBeNull()
    expect(result.current.isLoading).toBe(false)
  })
})
