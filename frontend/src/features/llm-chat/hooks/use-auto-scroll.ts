// frontend/src/features/llm-chat/hooks/use-auto-scroll.ts
import { useCallback, useRef } from "react"
import type { UIEvent } from "react"

export function useAutoScroll() {
  const scrollViewportRef = useRef<HTMLDivElement | null>(null)
  const isAutoScrollEnabled = useRef(true)

  const viewportRef = useCallback((root: HTMLDivElement | null) => {
    if (!root) {
      scrollViewportRef.current = null
      return
    }

    scrollViewportRef.current =
      root.querySelector<HTMLDivElement>(
        '[data-slot="scroll-area-viewport"]'
      ) ?? root
  }, [])

  const onScroll = useCallback((e: UIEvent<HTMLDivElement>) => {
    const target =
      scrollViewportRef.current ?? (e.currentTarget as HTMLDivElement)

    const { scrollTop, scrollHeight, clientHeight } = target

    // 사용자가 스크롤 맨 밑부분 근처에 있는지 확인
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 300
    isAutoScrollEnabled.current = isAtBottom
  }, [])

  const scrollToBottom = useCallback((force = false) => {
    const viewport = scrollViewportRef.current

    if ((force || isAutoScrollEnabled.current) && viewport) {
      viewport.scrollTo({
        top: viewport.scrollHeight,
        behavior: "auto",
      })
    }
  }, [])

  return { viewportRef, onScroll, scrollToBottom }
}
