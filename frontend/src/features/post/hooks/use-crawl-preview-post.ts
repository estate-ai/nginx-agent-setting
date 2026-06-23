"use client"

import { useState } from "react"
import { previewCrawlPost } from "@/features/post/api/preview-crawl-post"
import type { CrawlPreview } from "@/features/post/types/post"

export function useCrawlPreviewPost() {
  const [data, setData] = useState<CrawlPreview | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const preview = async (url: string, keyword: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await previewCrawlPost({
        url: url.trim(),
        keyword: keyword.trim() || null,
      })
      setData(result)
      return result
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "크롤링 미리보기에 실패했습니다."
      )
      throw cause
    } finally {
      setIsLoading(false)
    }
  }

  const reset = () => {
    setData(null)
    setError(null)
  }

  return { preview, reset, data, error, isLoading }
}
