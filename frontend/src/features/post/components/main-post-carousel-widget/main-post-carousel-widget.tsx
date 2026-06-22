"use client"

import { useState } from "react"
import { ArrowRight, BookOpen, ImageOff, Sparkles } from "lucide-react"
import type { PostSourceType } from "@/features/post/types/post"
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/shared/components/ui/carousel"
import { Skeleton } from "@/shared/components/ui/skeleton"

export type MainPostCarouselItem = {
  id: string
  title: string
  summary: string
  thumbnailUrl: string | null
  sourceType: PostSourceType
  createdAt: string
}

type MainPostCarouselWidgetProps = {
  posts?: MainPostCarouselItem[]
  isLoading?: boolean
  error?: string | null
  onPostClick?: (postId: string) => void
}

const sourceLabels: Record<PostSourceType, string> = {
  LLM_REPORT: "AI 리포트",
  CRAWLING: "크롤링",
  MANUAL: "일반",
}

function Thumbnail({
  thumbnailUrl,
  title,
}: Pick<MainPostCarouselItem, "thumbnailUrl" | "title">) {
  const [hasImageError, setHasImageError] = useState(false)
  const showFallback = !thumbnailUrl || hasImageError

  return (
    <div className="absolute inset-0 overflow-hidden bg-neutral-900">
      {showFallback ? (
        <div
          className="flex h-full items-center justify-center bg-[radial-gradient(circle_at_70%_30%,rgba(255,255,255,0.16),transparent_38%),linear-gradient(135deg,#262626,#0a0a0a)] text-white/50"
          aria-label={`${title} 썸네일 없음`}
        >
          <ImageOff className="size-10" aria-hidden="true" />
        </div>
      ) : (
        // 크롤링 출처의 이미지 호스트는 런타임에 결정되어 Next Image allowlist를 사용할 수 없다.
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={thumbnailUrl}
          alt={`${title} 썸네일`}
          className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
          loading="lazy"
          onError={() => setHasImageError(true)}
        />
      )}
      <div className="absolute inset-0 bg-gradient-to-r from-black/90 via-black/65 to-black/20" />
      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-black/10" />
    </div>
  )
}

function LoadingState() {
  return (
    <div
      className="relative min-h-[320px] overflow-hidden rounded-xl border border-neutral-200 bg-neutral-950 p-7 sm:min-h-[380px] sm:p-10"
      role="status"
      aria-label="게시글을 불러오는 중"
    >
      <div className="flex max-w-2xl flex-col gap-4">
        <Skeleton className="h-6 w-24 bg-white/15" />
        <Skeleton className="h-10 w-4/5 bg-white/15" />
        <Skeleton className="h-10 w-3/5 bg-white/15" />
        <Skeleton className="mt-3 h-4 w-full bg-white/10" />
        <Skeleton className="h-4 w-5/6 bg-white/10" />
        <Skeleton className="mt-5 h-10 w-32 bg-white/15" />
      </div>
      <span className="sr-only">게시글을 불러오는 중입니다.</span>
    </div>
  )
}

export function MainPostCarouselWidget({
  posts = [],
  isLoading = false,
  error = null,
  onPostClick = () => undefined,
}: MainPostCarouselWidgetProps = {}) {
  return (
    <section className="space-y-4" aria-labelledby="main-post-carousel-title">
      <div className="flex items-end justify-between border-b border-neutral-200 pb-4">
        <div>
          <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold tracking-[0.16em] text-neutral-500 uppercase">
            <Sparkles className="size-3.5" aria-hidden="true" />
            Market intelligence
          </p>
          <h2
            id="main-post-carousel-title"
            className="flex items-center gap-2 text-xl font-bold tracking-[-0.03em] text-neutral-950 sm:text-2xl"
          >
            <BookOpen className="size-5" aria-hidden="true" />
            뉴스 기반 창업 상권 AI 리포트
          </h2>
        </div>
        <span className="hidden text-xs text-neutral-400 sm:block">
          최신 리포트
        </span>
      </div>

      {isLoading ? (
        <LoadingState />
      ) : error ? (
        <div
          role="alert"
          className="rounded-xl border border-red-200 bg-red-50 px-5 py-14 text-center text-sm text-red-700"
        >
          {error}
        </div>
      ) : posts.length === 0 ? (
        <div className="flex min-h-[260px] flex-col items-center justify-center rounded-xl border border-dashed border-neutral-300 bg-neutral-50 px-5 text-center">
          <Sparkles
            className="mb-3 size-6 text-neutral-400"
            aria-hidden="true"
          />
          <p className="text-sm font-semibold text-neutral-700">
            아직 등록된 리포트가 없습니다.
          </p>
          <p className="mt-1 text-xs text-neutral-500">
            새로운 AI 분석 리포트가 발행되면 이곳에 표시됩니다.
          </p>
        </div>
      ) : (
        <Carousel
          opts={{ align: "start", loop: false }}
          aria-label="최신 AI 리포트 캐러셀"
          className="group/carousel"
        >
          <div className="overflow-hidden rounded-xl">
            <CarouselContent className="ml-0">
              {posts.map((post) => (
                <CarouselItem key={post.id} className="basis-full pl-0">
                  <article className="group relative min-h-[320px] overflow-hidden bg-neutral-950 sm:min-h-[380px]">
                    <Thumbnail
                      thumbnailUrl={post.thumbnailUrl}
                      title={post.title}
                    />
                    <div className="relative z-10 flex min-h-[320px] max-w-3xl flex-col justify-end px-6 py-8 text-white sm:min-h-[380px] sm:px-10 sm:py-10 lg:px-12">
                      <div className="mb-auto flex items-center gap-2">
                        <span className="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-[11px] font-semibold backdrop-blur-sm">
                          {sourceLabels[post.sourceType]}
                        </span>
                        <time
                          dateTime={post.createdAt}
                          className="text-xs text-white/65"
                        >
                          {new Date(post.createdAt).toLocaleDateString("ko-KR")}
                        </time>
                      </div>
                      <h3 className="max-w-2xl text-2xl leading-tight font-black tracking-[-0.04em] text-balance sm:text-4xl">
                        {post.title}
                      </h3>
                      <p className="mt-4 line-clamp-3 max-w-2xl text-sm leading-6 text-white/75 sm:text-base sm:leading-7">
                        {post.summary}
                      </p>
                      <button
                        type="button"
                        aria-label={`${post.title} 게시글 보기`}
                        className="mt-6 flex h-10 w-fit items-center gap-2 rounded-lg bg-white px-4 text-sm font-bold text-neutral-950 transition-colors hover:bg-neutral-200 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-neutral-950 focus-visible:outline-none"
                        onClick={() => onPostClick(post.id)}
                      >
                        리포트 보기
                        <ArrowRight className="size-4" aria-hidden="true" />
                      </button>
                    </div>
                  </article>
                </CarouselItem>
              ))}
            </CarouselContent>
          </div>
          {posts.length > 1 ? (
            <>
              <CarouselPrevious className="left-3 hidden border-white/20 bg-black/35 text-white hover:bg-black/60 hover:text-white sm:inline-flex" />
              <CarouselNext className="right-3 hidden border-white/20 bg-black/35 text-white hover:bg-black/60 hover:text-white sm:inline-flex" />
            </>
          ) : null}
        </Carousel>
      )}
    </section>
  )
}
