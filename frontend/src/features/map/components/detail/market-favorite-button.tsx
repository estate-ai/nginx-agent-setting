"use client"

import { Heart } from "lucide-react"
import { toast } from "sonner"
import { useQueryClient } from "@tanstack/react-query"
import { HttpStatusError } from "@/features/auth/lib/fetch-with-auth"
import {
  invalidateListMarketFavoritesApiV1AgentMarketFavoritesGet,
  useDeleteMarketFavoriteApiV1AgentMarketFavoritesDongCodeDelete,
  useListMarketFavoritesApiV1AgentMarketFavoritesGet,
  useUpsertMarketFavoriteApiV1AgentMarketFavoritesPost,
} from "@/shared/api/generated/agent/endpoints/agent-market-favorites/agent-market-favorites"
import { Button } from "@/shared/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/shared/components/ui/tooltip"
import { cn } from "@/shared/lib/utils"

type MarketFavoriteButtonProps = {
  dongCode: string
  dongName: string
}

export function MarketFavoriteButton({
  dongCode,
  dongName,
}: MarketFavoriteButtonProps) {
  const queryClient = useQueryClient()
  const normalizedDongCode = dongCode.trim()
  const normalizedDongName = dongName.trim() || normalizedDongCode
  const favoritesQuery = useListMarketFavoritesApiV1AgentMarketFavoritesGet({
    query: {
      enabled: normalizedDongCode.length > 0,
    },
  })
  const upsertFavorite = useUpsertMarketFavoriteApiV1AgentMarketFavoritesPost()
  const deleteFavorite =
    useDeleteMarketFavoriteApiV1AgentMarketFavoritesDongCodeDelete()
  const isFavorite =
    favoritesQuery.data?.favorites.some(
      (favorite) => favorite.dong_code === normalizedDongCode
    ) ?? false
  const isPending =
    favoritesQuery.isLoading ||
    upsertFavorite.isPending ||
    deleteFavorite.isPending
  const tooltip = isFavorite ? "상권 좋아요 해제" : "상권 좋아요"

  const invalidateFavorites = () => {
    void invalidateListMarketFavoritesApiV1AgentMarketFavoritesGet(queryClient)
  }

  const handleToggle = () => {
    if (!normalizedDongCode) {
      toast("상권을 먼저 선택해 주세요.")
      return
    }

    if (isFavorite) {
      deleteFavorite.mutate(
        { dongCode: normalizedDongCode },
        {
          onSuccess: () => {
            invalidateFavorites()
            toast("상권 좋아요를 해제했습니다.")
          },
          onError: (error) => {
            toast.error(
              resolveFavoriteError(error, "좋아요 해제에 실패했습니다.")
            )
          },
        }
      )
      return
    }

    upsertFavorite.mutate(
      {
        data: {
          dong_code: normalizedDongCode,
          dong_name: normalizedDongName,
        },
      },
      {
        onSuccess: () => {
          invalidateFavorites()
          toast.success("상권을 좋아요 목록에 추가했습니다.")
        },
        onError: (error) => {
          toast.error(
            resolveFavoriteError(error, "좋아요 추가에 실패했습니다.")
          )
        },
      }
    )
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            disabled={isPending || !normalizedDongCode}
            onClick={handleToggle}
            className="h-9 cursor-pointer gap-1.5 border border-primary-foreground/15 bg-primary-foreground/10 px-3 text-primary-foreground shadow-none hover:bg-primary-foreground/15 hover:text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Heart
              className={cn(
                "size-4",
                isFavorite && "fill-current text-red-300"
              )}
            />
            <span>{isFavorite ? "관심있음" : "관심표시"}</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>{tooltip}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

const resolveFavoriteError = (error: unknown, fallbackMessage: string) => {
  if (error instanceof HttpStatusError) {
    if (error.status === 401) {
      return "로그인 세션을 확인하지 못했습니다. 다시 로그인한 뒤 시도해 주세요."
    }

    const detail =
      typeof error.body === "object" &&
      error.body !== null &&
      "detail" in error.body &&
      typeof error.body.detail === "string"
        ? error.body.detail
        : null

    return detail ?? fallbackMessage
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallbackMessage
}
