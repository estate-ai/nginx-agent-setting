import Link from "next/link"
import { ArrowRight, Map, Sparkles } from "lucide-react"

// 홈 전용 CTA 영역이다. 온보딩과 지도 탐색으로 진입시키는 링크만 가진다.
export function HomeCtaWidget() {
  return (
    <section
      aria-label="창업 추천 서비스 바로가기"
      className="grid gap-5 lg:grid-cols-2"
    >
      <article className="group flex min-h-[190px] flex-col overflow-hidden rounded-xl border border-t-4 border-neutral-200 border-t-neutral-950 bg-white p-5 transition-transform duration-200 hover:-translate-y-1 sm:p-6">
        <div className="flex items-start gap-4">
          <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-neutral-100 text-neutral-950">
            <Sparkles className="size-5" aria-hidden="true" />
          </div>
          <div>
            <p className="text-xs font-semibold tracking-[0.14em] text-neutral-400 uppercase">
              Personal recommendation
            </p>
            <h2 className="mt-1 text-lg font-bold tracking-[-0.03em] text-neutral-950">
              1분 성향 분석 온보딩
            </h2>
            <p className="mt-2 text-sm leading-6 text-neutral-500">
              간단한 설문으로 경영 성향과 자본 상황을 분석해 어울리는 브랜드와
              상권 후보를 추천합니다.
            </p>
          </div>
        </div>
        <Link
          href="/onboarding"
          className="mt-5 flex h-11 items-center justify-between rounded-lg bg-neutral-950 px-4 text-sm font-semibold text-white transition-colors hover:bg-neutral-800 focus-visible:ring-2 focus-visible:ring-neutral-950 focus-visible:ring-offset-2 focus-visible:outline-none"
        >
          성향 분석 시작하기
          <ArrowRight
            className="size-4 transition-transform group-hover:translate-x-1"
            aria-hidden="true"
          />
        </Link>
      </article>

      <article className="group flex min-h-[190px] flex-col overflow-hidden rounded-xl border border-t-4 border-neutral-200 border-t-neutral-950 bg-white p-5 transition-transform duration-200 hover:-translate-y-1 sm:p-6">
        <div className="flex items-start gap-4">
          <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-neutral-100 text-neutral-950">
            <Map className="size-5" aria-hidden="true" />
          </div>
          <div>
            <p className="text-xs font-semibold tracking-[0.14em] text-neutral-400 uppercase">
              Commercial district data
            </p>
            <h2 className="mt-1 text-lg font-bold tracking-[-0.03em] text-neutral-950">
              몰입형 상권 지도 탐색
            </h2>
            <p className="mt-2 text-sm leading-6 text-neutral-500">
              서울 핵심 상권의 매출, 유동인구와 업종별 점포 데이터를 지도에서
              한눈에 비교해 보세요.
            </p>
          </div>
        </div>
        <Link
          href="/map"
          className="mt-5 flex h-11 items-center justify-between rounded-lg bg-neutral-100 px-4 text-sm font-semibold text-neutral-900 transition-colors hover:bg-neutral-200 focus-visible:ring-2 focus-visible:ring-neutral-500 focus-visible:ring-offset-2 focus-visible:outline-none"
        >
          상권 지도 살펴보기
          <Map
            className="size-4 transition-transform group-hover:rotate-12"
            aria-hidden="true"
          />
        </Link>
      </article>
    </section>
  )
}
