import { usePathname } from "next/navigation"
import { useSession } from "@/features/auth/lib/auth-client"
import { OnboardingRecommendationLoader } from "@/features/map/components/recommendation/onboarding-recommendation-loader"
import { RecommendationEmpty } from "@/features/map/components/recommendation/recommendation-empty"

type RecommendationEmptyContainerProps = {
  hasRecommendations: boolean
  onResetFilters: () => void
}

export function RecommendationEmptyContainer({
  hasRecommendations,
  onResetFilters,
}: RecommendationEmptyContainerProps) {
  const pathname = usePathname()
  const { data: session, isPending: isSessionPending } = useSession()
  const loginHref = `/login?${new URLSearchParams({
    callbackURL: pathname ?? "/map",
  }).toString()}`

  return (
    <RecommendationEmpty
      hasRecommendations={hasRecommendations}
      isSessionPending={isSessionPending}
      loginHref={loginHref}
      onboardingContent={session ? <OnboardingRecommendationLoader /> : null}
      onResetFilters={onResetFilters}
      shouldShowLoginCta={!session}
    />
  )
}
