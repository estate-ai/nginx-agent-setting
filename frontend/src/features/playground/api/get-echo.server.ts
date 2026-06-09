import "server-only"
import { type QueryClient } from "@tanstack/react-query"
import {
  echoQueryKey,
  getEchoClient,
} from "@/features/playground/api/get-echo.client"

export const prefetchEcho = async (
  queryClient: QueryClient,
  gatewayBase: string,
  jwt: string
) => {
  await queryClient.prefetchQuery({
    queryKey: echoQueryKey(gatewayBase),
    queryFn: () => getEchoClient(gatewayBase, jwt),
  })
}
