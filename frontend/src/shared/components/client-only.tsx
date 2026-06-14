"use client"

import { type ReactNode, useSyncExternalStore } from "react"

type ClientOnlyProps = {
  children: ReactNode
  fallback?: ReactNode
}

const subscribe = () => () => ({})
const getClientSnapshot = () => true
const getServerSnapshot = () => false

const useIsClient = () =>
  useSyncExternalStore(subscribe, getClientSnapshot, getServerSnapshot)

// 클라이언트에서만 렌더링될 컴포넌트를 감싸는 컴포넌트입니다.
// https://tkdodo.eu/blog/avoiding-hydration-mismatches-with-use-sync-external-store
export function ClientOnly({ children, fallback = null }: ClientOnlyProps) {
  const isClient = useIsClient()

  if (!isClient) {
    return <>{fallback}</>
  }

  return <>{children}</>
}
