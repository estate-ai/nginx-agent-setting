"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { ArrowRight, Sparkles } from "lucide-react"
import { useQueryClient } from "@tanstack/react-query"
import { toMarketRecommendedAreasFromOnboarding } from "@/features/map/components/recommendation/onboarding-recommendation-adapter"
import { mapQueryKeys } from "@/features/map/lib/map-query-options"
import { DEFAULT_ONBOARDING_TOP_K } from "@/features/onboarding/lib/onboarding-defaults"
import type {
  OnboardingCategoryRecommendation,
  OnboardingSavedResultSummary,
} from "@/features/onboarding/types/onboarding"
import {
  getGetAreaRecommendationsSurveysResultsResultCodeAreaRecommendationsGetQueryOptions,
  useGetResultByCodeSurveysResultsResultCodeGet,
  useGetSavedSurveyResultsSurveysMeSavedResultsGet,
} from "@/shared/api/generated/onboarding/endpoints/survey/survey"
import { Badge } from "@/shared/components/ui/badge"
import { Button } from "@/shared/components/ui/button"
import { Spinner } from "@/shared/components/ui/spinner"

const getLatestSavedResultCode = (results: OnboardingSavedResultSummary[]) => {
  return [...results].sort(
    (a, b) => new Date(b.saved_at).getTime() - new Date(a.saved_at).getTime()
  )[0]?.result_code
}

const getErrorMessage = (error: unknown) => {
  if (error instanceof Error) {
    return error.message
  }

  return "추천 상권을 불러오지 못했습니다."
}

export function OnboardingRecommendationLoader() {
  const queryClient = useQueryClient()
  const [loadingCategoryCode, setLoadingCategoryCode] = useState<string | null>(
    null
  )
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const {
    data: savedResults,
    isError: isSavedResultsError,
    isLoading: isSavedResultsLoading,
  } = useGetSavedSurveyResultsSurveysMeSavedResultsGet({
    query: {
      staleTime: 1000 * 60,
    },
  })
  const resultCode = useMemo(
    () =>
      savedResults?.default_result_code ??
      getLatestSavedResultCode(savedResults?.results ?? []) ??
      "",
    [savedResults]
  )
  const {
    data: surveyResult,
    isError: isSurveyResultError,
    isLoading: isSurveyResultLoading,
  } = useGetResultByCodeSurveysResultsResultCodeGet(resultCode, {
    query: {
      enabled: resultCode.length > 0,
      staleTime: 1000 * 60,
    },
  })
  const categories = surveyResult?.category_recommendations ?? []
  const isLoading = isSavedResultsLoading || isSurveyResultLoading
  const isError = isSavedResultsError || isSurveyResultError

  const handleSelectCategory = async (
    category: OnboardingCategoryRecommendation
  ) => {
    if (!resultCode) {
      return
    }

    setLoadingCategoryCode(category.service_category_code)
    setErrorMessage(null)

    try {
      const result = await queryClient.fetchQuery(
        getGetAreaRecommendationsSurveysResultsResultCodeAreaRecommendationsGetQueryOptions(
          resultCode,
          {
            category_code: category.service_category_code,
            top_k: DEFAULT_ONBOARDING_TOP_K,
          }
        )
      )
      const recommendations = toMarketRecommendedAreasFromOnboarding(
        result.prediction.recommendations
      )

      await queryClient.invalidateQueries({ queryKey: mapQueryKeys.adminAreas })
      queryClient.setQueryData(mapQueryKeys.recommendations, recommendations)

      if (recommendations.length === 0) {
        setErrorMessage("선택한 업종의 추천 상권이 없습니다.")
      }
    } catch (error) {
      setErrorMessage(getErrorMessage(error))
    } finally {
      setLoadingCategoryCode(null)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center gap-2 text-xs text-muted-foreground">
        <Spinner className="size-3.5" />
        성향 분석 결과를 확인하는 중입니다.
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center">
        <Sparkles className="h-6 w-6 text-muted-foreground" />
        <p className="text-xs leading-relaxed text-muted-foreground">
          저장된 성향 분석 결과를 불러오지 못했습니다.
        </p>
        <Button asChild variant="outline" size="sm">
          <Link href="/onboarding">성향 분석 다시 보기</Link>
        </Button>
      </div>
    )
  }

  if (!resultCode || categories.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center">
        <Sparkles className="h-6 w-6 text-muted-foreground" />
        <p className="text-xs leading-relaxed text-muted-foreground">
          아직 추천 상권이 없습니다. 성향 분석을 완료하면 어울리는 행정동 상권이
          자동으로 추천됩니다.
        </p>
        <Button asChild variant="outline" size="sm">
          <Link href="/onboarding">성향 분석 시작하기</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="border-b border-border px-1 pb-3">
        <div className="flex items-center gap-2 text-xs font-semibold text-foreground">
          <Sparkles className="h-4 w-4 text-primary" />
          추천 업종
        </div>
        <p className="mt-2 text-[11px] leading-relaxed text-muted-foreground">
          업종을 선택하면 어울리는 행정동 상권을 지도에 표시합니다.
        </p>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto py-3">
        <div className="flex flex-col gap-2">
          {categories.slice(0, 8).map((category) => {
            const isLoadingCategory =
              loadingCategoryCode === category.service_category_code

            return (
              <button
                key={category.service_category_code}
                type="button"
                onClick={() => handleSelectCategory(category)}
                disabled={loadingCategoryCode !== null}
                className="flex w-full items-center gap-3 rounded-lg border border-border px-3 py-2.5 text-left transition-colors hover:bg-muted/40 disabled:pointer-events-none disabled:opacity-60"
              >
                <span className="flex min-w-0 flex-1 flex-col gap-1">
                  <span className="flex items-center gap-2">
                    <span className="truncate text-sm font-medium text-foreground">
                      {category.service_category_name}
                    </span>
                    <Badge variant="outline" className="shrink-0">
                      {Math.round(category.score * 100)}%
                    </Badge>
                  </span>
                  <span className="truncate text-[11px] text-muted-foreground">
                    {category.category_group} · {category.service_category_code}
                  </span>
                </span>
                {isLoadingCategory ? (
                  <Spinner className="size-3.5 shrink-0" />
                ) : (
                  <ArrowRight className="size-3.5 shrink-0 text-muted-foreground" />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {errorMessage ? (
        <p className="border-t border-border pt-3 text-[11px] leading-relaxed text-destructive">
          {errorMessage}
        </p>
      ) : null}
    </div>
  )
}
