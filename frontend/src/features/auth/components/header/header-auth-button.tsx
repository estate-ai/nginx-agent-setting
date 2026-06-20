import { HeaderAuthLoginButton } from "@/features/auth/components/header/header-auth-login-button"
import { HeaderAuthLogoutButton } from "@/features/auth/components/header/header-auth-logout-button"
import { getServerSession } from "@/features/auth/lib/server-session"

export async function HeaderAuthButton() {
  const session = await getServerSession()

  if (!session) {
    return <HeaderAuthLoginButton />
  }

  return <HeaderAuthLogoutButton userName={session.user.name} />
}
