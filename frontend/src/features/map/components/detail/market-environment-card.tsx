import { CommercialChangeIndicatorSection } from "@/features/map/components/detail/commercial-change-indicator"
import { CompetitionAnalysisSection } from "@/features/map/components/detail/competition-analysis"
import type {
  CommercialChangeIndicator,
  CompetitionStats,
} from "@/features/map/types/map"
import { Card, CardContent } from "@/shared/components/ui/card"

type MarketEnvironmentCardProps = {
  competition: CompetitionStats | null
  indicator: CommercialChangeIndicator | null
}

export function MarketEnvironmentCard({
  competition,
  indicator,
}: MarketEnvironmentCardProps) {
  return (
    <Card className="lg:col-span-2">
      <CardContent className="space-y-8">
        {competition ? (
          <CompetitionAnalysisSection competition={competition} />
        ) : null}
        {competition && indicator ? <div className="border-t" /> : null}
        {indicator ? (
          <CommercialChangeIndicatorSection indicator={indicator} />
        ) : null}
      </CardContent>
    </Card>
  )
}
