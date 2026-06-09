import "server-only"
import { type QueryClient } from "@tanstack/react-query"
import {
  getProfileClient,
  profileQueryKey,
} from "@/features/playground/api/get-profile.client"

export const prefetchProfile = async (
  queryClient: QueryClient,
  gatewayBase: string,
  jwt: string
) => {
  await queryClient.prefetchQuery({
    queryKey: profileQueryKey(gatewayBase),
    queryFn: () => getProfileClient(gatewayBase, jwt),
  })
}
