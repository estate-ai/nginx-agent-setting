"use client"

import { useRouter } from "next/navigation"
import { type FallbackProps } from "react-error-boundary"

export function MainErrorFallback({ resetErrorBoundary }: FallbackProps) {
  const router = useRouter()

  return (
    <div role="alert">
      <h2>예기치 않은 오류가 발생했습니다.</h2>
      <div>
        <button
          onClick={() => {
            resetErrorBoundary()
            router.refresh()
          }}
        >
          재시도
        </button>
        <button
          onClick={() => {
            window.location.assign("/")
          }}
        >
          홈으로
        </button>
      </div>
    </div>
  )
}
