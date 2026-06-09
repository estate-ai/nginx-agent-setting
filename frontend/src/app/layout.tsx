// src/app/layout.tsx
import type { ReactNode } from "react"
import UserNav from "@/features/auth/components/user-nav"
import "./globals.css"

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <div>
          <UserNav />
        </div>
        <div>{children}</div>
      </body>
    </html>
  )
}
