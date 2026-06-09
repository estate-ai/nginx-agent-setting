// src/features/auth/components/sign-in-client.tsx
"use client"

// Google OAuth는 socialProviders.google 설정 + signIn.social({ provider:"google" })로 동작.
// callback URL은 /api/auth/callback/google 형태로 Google Console에 등록해야 함.
// https://better-auth.com/docs/authentication/google :contentReference[oaicite:41]{index=41}
//
// signIn.social의 callbackURL / errorCallbackURL 옵션은 Basic Usage 문서에 명시.
// https://better-auth.com/docs/basic-usage :contentReference[oaicite:42]{index=42}
import { authClient } from "@/features/auth/lib/auth-client"
import { Button } from "@/shared/components/ui/button"

export default function SignInClient({
  callbackURL,
  error,
}: {
  callbackURL: string
  error?: string
}) {
  return (
    <div>
      {error ? <div>Error: {error}</div> : null}

      <Button
        onClick={async () => {
          await authClient.signIn.social({
            provider: "google",
            callbackURL,
            errorCallbackURL: "/sign-in?error=oauth",
          })
        }}
      >
        Continue with Google
      </Button>

      <div>
        callbackURL: <code>{callbackURL}</code>
      </div>
    </div>
  )
}
