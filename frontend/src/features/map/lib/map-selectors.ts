import type {
  BudgetRange,
  DongCode,
  TargetDemographic,
  TradeAreaId,
} from "@/features/map/types/map"
import { districtsData, personaResults } from "@/features/startup/lib/data"

type FilteredTradeAreaInput = {
  activePersona: string | null
  budgetRange: BudgetRange
  recommendationsOnly: boolean
  selectedCategory: string
  targetDemographic: TargetDemographic
}

type ResolveRecommendedTradeAreaIdsInput = {
  chatTradeAreaIds: TradeAreaId[] | null
  isChatPanelActive: boolean
  onboardingTradeAreaIds: TradeAreaId[] | null
  surveyTradeAreaIds: TradeAreaId[] | null
}

// 선택자 유틸은 필터링 규칙이 위젯과 스토어 조각에 흩어지지 않게 한다.
// 상권 데이터는 행정동 코드를 id로 쓰므로 선택된 동 코드로 바로 조회한다.
export const getSelectedTradeArea = (selectedDongCode: DongCode | null) =>
  districtsData.find((district) => district.id === selectedDongCode) ?? null

export const getFilteredTradeAreas = ({
  activePersona,
  budgetRange,
  recommendationsOnly,
  selectedCategory,
  targetDemographic,
}: FilteredTradeAreaInput) =>
  districtsData.filter((district) => {
    if (selectedCategory !== "all") {
      const hasSector = district.topSectors.some((sector) =>
        sector.sector.includes(selectedCategory)
      )

      if (!hasSector) {
        return false
      }
    }

    if (budgetRange !== "all") {
      if (budgetRange === "low" && district.avgSales > 3000) {
        return false
      }

      if (budgetRange === "high" && district.avgSales < 3500) {
        return false
      }
    }

    if (targetDemographic !== "all") {
      const dominantAge = district.footTrafficAge.reduce((current, next) =>
        next.percentage > current.percentage ? next : current
      )

      if (targetDemographic === "20" && dominantAge.ageGroup !== "20대") {
        return false
      }

      if (targetDemographic === "30" && dominantAge.ageGroup !== "30대") {
        return false
      }

      if (
        targetDemographic === "50" &&
        dominantAge.ageGroup !== "40대" &&
        dominantAge.ageGroup !== "50대 이상"
      ) {
        return false
      }
    }

    if (recommendationsOnly && activePersona) {
      const personaInfo = personaResults[activePersona]

      if (
        personaInfo &&
        !personaInfo.recommendedDistricts.includes(district.id)
      ) {
        return false
      }
    }

    return true
  })

export const getFilteredTradeAreaIds = (input: FilteredTradeAreaInput) =>
  new Set(getFilteredTradeAreas(input).map((district) => district.id))

export const getRecommendedTradeAreaIds = (activePersona: string | null) =>
  activePersona
    ? (personaResults[activePersona]?.recommendedDistricts ?? [])
    : []

export const resolveRecommendedTradeAreaIds = ({
  chatTradeAreaIds,
  isChatPanelActive,
  onboardingTradeAreaIds,
  surveyTradeAreaIds,
}: ResolveRecommendedTradeAreaIdsInput) => {
  const baseTradeAreaIds = surveyTradeAreaIds ?? onboardingTradeAreaIds ?? []

  return isChatPanelActive
    ? (chatTradeAreaIds ?? baseTradeAreaIds)
    : baseTradeAreaIds
}
