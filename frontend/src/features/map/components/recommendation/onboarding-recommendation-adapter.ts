import type { MarketRecommendedArea } from "@/features/map/types/map"
import type { OnboardingRecommendation } from "@/features/onboarding/types/onboarding"

const DONG_CODE_ALIAS: Record<string, string> = {
  "11110515": "11110720",
  "11680740": "11680511",
  "11740760": "11740520",
  "11740770": "11740520",
}

const getDongCodeFromItemId = (itemId: string) => {
  const rawDongCode = itemId.split(":")[0]?.trim()

  if (!rawDongCode) {
    return null
  }

  return DONG_CODE_ALIAS[rawDongCode] ?? rawDongCode
}

export const toMarketRecommendedAreasFromOnboarding = (
  recommendations: OnboardingRecommendation[]
): MarketRecommendedArea[] => {
  const areaByDongCode = new Map<string, MarketRecommendedArea>()

  recommendations.forEach((recommendation) => {
    const dongCode = getDongCodeFromItemId(recommendation.item_id)

    if (!dongCode) {
      return
    }

    const score = Math.round(recommendation.score * 100)
    const previous = areaByDongCode.get(dongCode)

    if (!previous || previous.score < score) {
      areaByDongCode.set(dongCode, {
        dongCode,
        dongName: recommendation.area_name,
        score,
      })
    }
  })

  return Array.from(areaByDongCode.values())
}
