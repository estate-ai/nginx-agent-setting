import { describe, expect, it } from "vitest"
import { parseMapAreaSearchToolResult } from "@/features/agent/lib/map-area-tool-result"

describe("parseMapAreaSearchToolResult", () => {
  it("지도 검색 도구 결과를 지도 검색 영역으로 변환한다.", () => {
    const result = parseMapAreaSearchToolResult(
      JSON.stringify({
        type: "map_area_search_results",
        success: true,
        keyword: "성수",
        industryCode: "CS100001",
        areas: [
          {
            centerLat: 37.544,
            centerLng: 127.055,
            dongCode: "11200690",
            dongName: "성수2가3동",
            estimatedSalesAmount: 123456,
            industryCode: "CS100001",
            industryName: "한식음식점",
            rank: 1,
            sigunguCode: "11200",
            sigunguName: "성동구",
          },
        ],
      })
    )

    expect(result?.keyword).toBe("성수")
    expect(result?.industryCode).toBe("CS100001")
    expect(result?.areas).toEqual([
      {
        centerLat: 37.544,
        centerLng: 127.055,
        dongCode: "11200690",
        dongName: "성수2가3동",
        estimatedSalesAmount: 123456,
        industryCode: "CS100001",
        industryName: "한식음식점",
        rank: 1,
        sigunguCode: "11200",
        sigunguName: "성동구",
      },
    ])
  })

  it("실패 결과나 잘못된 JSON은 조용히 무시할 수 있게 null로 반환한다.", () => {
    expect(parseMapAreaSearchToolResult("{")).toBeNull()
    expect(
      parseMapAreaSearchToolResult({
        type: "map_area_search_results",
        success: false,
        areas: [],
      })
    ).toBeNull()
  })
})
