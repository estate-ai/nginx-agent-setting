import type { StateCreator } from "zustand"
import type { TradeAreaId } from "@/features/map/types/map"

export type RecommendationSlice = {
  chatTradeAreaIds: TradeAreaId[] | null
  clearChatRecommendations: () => void
  setChatRecommendations: (chatTradeAreaIds: TradeAreaId[]) => void
}

// null은 아직 AI 응답에서 추천 x(설문·온보딩 추천으로 폴백), 빈 배열은 추천 없음(CTA)
export const createRecommendationSlice: StateCreator<RecommendationSlice> = (
  set
) => ({
  chatTradeAreaIds: null,
  clearChatRecommendations: () => set({ chatTradeAreaIds: null }),
  setChatRecommendations: (chatTradeAreaIds) => set({ chatTradeAreaIds }),
})
