import type { StateCreator } from "zustand"
import type { DongCode, MapTab } from "@/features/map/types/map"

export type SelectionSlice = {
  activeResultTab: MapTab
  selectedDongCode: DongCode | null
  selectDong: (selectedDongCode: DongCode | null) => void
  setActiveResultTab: (activeResultTab: MapTab) => void
}

// 선택된 동과 결과 패널 탭을 보관
// selectedDongCode가 선택의 단일 원천
// 지도 클릭·추천 목록·AI 채팅 모두 이 값을 갱신
export const createSelectionSlice: StateCreator<SelectionSlice> = (set) => ({
  activeResultTab: "traffic",
  selectedDongCode: null,
  selectDong: (selectedDongCode) => set({ selectedDongCode }),
  setActiveResultTab: (activeResultTab) => set({ activeResultTab }),
})
