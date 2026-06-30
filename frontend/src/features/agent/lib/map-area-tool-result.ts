import type { MarketSearchArea } from "@/features/map/types/map"

export type MapAreaSearchToolResult = {
  type: "map_area_search_results"
  success: true
  keyword?: string
  industryCode?: string
  industryName?: string
  areas: MarketSearchArea[]
}

const parseJson = (value: string) => {
  try {
    return JSON.parse(value) as unknown
  } catch {
    return null
  }
}

const toStringOrUndefined = (value: unknown) =>
  typeof value === "string" && value.trim() ? value.trim() : undefined

const toNumberOrUndefined = (value: unknown) =>
  typeof value === "number" && Number.isFinite(value) ? value : undefined

const toArea = (value: unknown): MarketSearchArea | null => {
  if (typeof value !== "object" || value === null) {
    return null
  }

  const candidate = value as Record<string, unknown>
  const dongCode = toStringOrUndefined(candidate.dongCode)
  const centerLat = toNumberOrUndefined(candidate.centerLat)
  const centerLng = toNumberOrUndefined(candidate.centerLng)

  if (!dongCode || centerLat === undefined || centerLng === undefined) {
    return null
  }

  return {
    centerLat,
    centerLng,
    dongCode,
    dongName: toStringOrUndefined(candidate.dongName) ?? dongCode,
    estimatedSalesAmount: toNumberOrUndefined(candidate.estimatedSalesAmount),
    industryCode: toStringOrUndefined(candidate.industryCode),
    industryName: toStringOrUndefined(candidate.industryName),
    rank: toNumberOrUndefined(candidate.rank),
    sigunguCode: toStringOrUndefined(candidate.sigunguCode) ?? "",
    sigunguName: toStringOrUndefined(candidate.sigunguName) ?? "",
  }
}

export const parseMapAreaSearchToolResult = (
  value: unknown
): MapAreaSearchToolResult | null => {
  const parsed = typeof value === "string" ? parseJson(value) : value
  if (typeof parsed !== "object" || parsed === null) {
    return null
  }

  const candidate = parsed as Record<string, unknown>
  if (
    candidate.type !== "map_area_search_results" ||
    candidate.success !== true ||
    !Array.isArray(candidate.areas)
  ) {
    return null
  }

  return {
    type: "map_area_search_results",
    success: true,
    keyword: toStringOrUndefined(candidate.keyword),
    industryCode: toStringOrUndefined(candidate.industryCode),
    industryName: toStringOrUndefined(candidate.industryName),
    areas: candidate.areas
      .map(toArea)
      .filter((area): area is MarketSearchArea => area !== null),
  }
}
