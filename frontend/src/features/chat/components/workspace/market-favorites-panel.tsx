"use client"

import {
  Eye,
  MapPinned,
  MessageSquarePlus,
  MoreVertical,
  PanelLeftClose,
} from "lucide-react"
import type { MarketFavoriteResponse } from "@/shared/api/generated/agent/schemas"
import { Badge } from "@/shared/components/ui/badge"
import { Button } from "@/shared/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/shared/components/ui/dropdown-menu"
import { ScrollArea } from "@/shared/components/ui/scroll-area"
import { Skeleton } from "@/shared/components/ui/skeleton"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/shared/components/ui/tooltip"
import { cn } from "@/shared/lib/utils"

type MarketFavoritesPanelProps = {
  favorites: MarketFavoriteResponse[]
  isLoading?: boolean
  selectedMarketDongCodes?: string[]
  onToggleMarketArea: (dongCode: string) => void
  onOpenFavorite: (favorite: MarketFavoriteResponse) => void
  onCollapsePanel: () => void
}

export function MarketFavoritesPanel({
  favorites,
  isLoading,
  selectedMarketDongCodes = [],
  onToggleMarketArea,
  onOpenFavorite,
  onCollapsePanel,
}: MarketFavoritesPanelProps) {
  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden border-l border-border/20 bg-background">
      <div className="flex h-12 shrink-0 items-center justify-between border-b border-border/20 px-4">
        <div className="flex items-center gap-2">
          <MapPinned className="size-3.5 text-muted-foreground" />
          <span className="text-xs font-medium text-foreground">관심 상권</span>
          <Badge variant="outline" className="h-4 px-1.5 py-0 text-[10px]">
            {favorites.length}
          </Badge>
        </div>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon-xs"
                onClick={onCollapsePanel}
                className="ml-1 cursor-pointer text-muted-foreground hover:text-foreground"
                id="market-favorites-panel-collapse-btn"
              >
                <PanelLeftClose className="size-3.5" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">패널 접기</TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      <ScrollArea className="min-h-0 flex-1 [&_[data-slot=scroll-area-viewport]>div]:!block [&_[data-slot=scroll-area-viewport]>div]:!w-full [&_[data-slot=scroll-area-viewport]>div]:!min-w-0">
        <div className="space-y-0.5 p-2">
          {isLoading &&
            Array.from({ length: 5 }).map((_, index) => (
              <Skeleton key={index} className="h-12 rounded-lg" />
            ))}

          {!isLoading &&
            favorites.map((favorite) => (
              <MarketFavoriteRow
                key={favorite.id}
                favorite={favorite}
                isSelected={selectedMarketDongCodes.includes(
                  favorite.dong_code
                )}
                onAttach={() => onToggleMarketArea(favorite.dong_code)}
                onOpen={() => onOpenFavorite(favorite)}
              />
            ))}

          {!isLoading && favorites.length === 0 && (
            <p className="px-3 py-8 text-center text-xs text-muted-foreground">
              관심 표시한 상권이 없습니다
            </p>
          )}
        </div>
      </ScrollArea>

      <div className="shrink-0 border-t border-border/15 px-4 py-2.5">
        <p className="text-xs leading-relaxed text-muted-foreground">
          관심 상권을 채팅 입력에 추가하거나 상세를 열 수 있습니다
        </p>
      </div>
    </div>
  )
}

function MarketFavoriteRow({
  favorite,
  isSelected,
  onAttach,
  onOpen,
}: {
  favorite: MarketFavoriteResponse
  isSelected: boolean
  onAttach: () => void
  onOpen: () => void
}) {
  return (
    <div
      onClick={onOpen}
      className={cn(
        "group flex cursor-pointer items-center gap-2 rounded-lg px-2 py-2 transition-all",
        isSelected ? "bg-foreground/[0.04]" : "hover:bg-muted/30"
      )}
      id={`market-favorite-row-${favorite.dong_code}`}
    >
      <span className="flex size-7 shrink-0 items-center justify-center rounded-md border border-border/30 bg-muted/20 text-muted-foreground">
        <MapPinned className="size-3.5" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate text-xs leading-tight font-medium text-foreground">
          {favorite.dong_name}
        </p>
        <p className="mt-0.5 truncate text-xs text-muted-foreground">
          동 코드 {favorite.dong_code}
        </p>
      </div>
      {isSelected && (
        <Badge
          variant="outline"
          className="hidden h-5 px-1.5 text-[10px] sm:flex"
        >
          추가됨
        </Badge>
      )}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            type="button"
            onClick={(event) => event.stopPropagation()}
            className="shrink-0 cursor-pointer rounded-md p-1 text-muted-foreground opacity-0 transition-all group-hover:opacity-100 hover:bg-muted/50 hover:text-foreground"
            id={`market-favorite-menu-${favorite.dong_code}`}
          >
            <MoreVertical className="size-3" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-44">
          <DropdownMenuItem onClick={onAttach} className="cursor-pointer">
            <MessageSquarePlus className="size-3.5" />
            <span>{isSelected ? "채팅에서 제거" : "채팅에 추가"}</span>
          </DropdownMenuItem>
          <DropdownMenuItem onClick={onOpen} className="cursor-pointer">
            <Eye className="size-3.5" />
            <span>상세 보기</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
