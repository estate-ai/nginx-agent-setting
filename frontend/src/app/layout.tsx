// src/app/layout.tsx
import UserNav from "@/features/auth/components/user-nav"
import { Providers } from "./providers"
import "./globals.css"

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ko">
      <body>
        <Providers>
          <div>
            <UserNav />
          </div>
          <div>{children}</div>
        </Providers>
      </body>
    </html>
  )
}
