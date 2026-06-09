// src/app/page.tsx
import Link from "next/link"
import { getServerSession } from "@/features/auth/lib/server-session"
import { Button } from "@/shared/components/ui/button"

export const dynamic = "force-dynamic"

export default async function HomePage() {
  const session = await getServerSession()

  return (
    <main>
      <h1>Home</h1>
      <pre>{JSON.stringify(session ?? null, null, 2)}</pre>

      <ul>
        <li>
          <Button asChild variant="link">
            <Link href="/sign-in">/sign-in</Link>
          </Button>
        </li>
        <li>
          <Button asChild variant="link">
            <Link href="/dashboard">/dashboard</Link>
          </Button>
        </li>
        <li>
          <Button asChild variant="link">
            <Link href="/playground">/playground</Link>
          </Button>
        </li>
        <li>
          <Button asChild variant="link">
            <Link href="/api/session">/api/session</Link>
          </Button>
        </li>
        <li>
          <Button asChild variant="link">
            <Link href="/api/auth/jwks">/api/auth/jwks (JWKS)</Link>
          </Button>
        </li>
        <li>
          <Button asChild variant="link">
            <Link href="/api/auth/token">/api/auth/token (JWT)</Link>
          </Button>
        </li>
      </ul>
    </main>
  )
}
