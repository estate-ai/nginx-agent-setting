"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { signOut } from "@/features/auth/lib/auth-client"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/shared/components/ui/alert-dialog"
import { Button } from "@/shared/components/ui/button"

type HeaderAuthLogoutButtonProps = {
  userName?: string | null
}

export function HeaderAuthLogoutButton({
  userName,
}: HeaderAuthLogoutButtonProps) {
  const router = useRouter()
  const [isSigningOut, setIsSigningOut] = useState(false)

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button
          variant="outline"
          size="lg"
          disabled={isSigningOut}
          className="min-w-20 px-3.5"
          title={userName ?? undefined}
        >
          로그아웃
        </Button>
      </AlertDialogTrigger>

      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>로그아웃 하시겠습니까?</AlertDialogTitle>
          <AlertDialogDescription>
            현재 세션이 종료되며 홈 화면으로 이동합니다.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>취소</AlertDialogCancel>
          <AlertDialogAction
            variant="destructive"
            onClick={async () => {
              if (isSigningOut) return

              setIsSigningOut(true)

              try {
                await signOut({
                  fetchOptions: {
                    onSuccess: () => {
                      router.push("/")
                    },
                  },
                })
              } finally {
                setIsSigningOut(false)
              }
            }}
          >
            로그아웃
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
