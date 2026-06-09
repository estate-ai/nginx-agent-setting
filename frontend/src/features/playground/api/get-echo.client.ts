import { useSuspenseQuery } from "@tanstack/react-query"

type JsonObject = Record<string, unknown>
type GatewayResult = { ok: boolean; status: number; data: unknown }

const parseJsonSafe = (text: string): unknown => {
  try {
    return JSON.parse(text) as unknown
  } catch {
    return { raw: text } satisfies JsonObject
  }
}

export const getEchoClient = async (
  gatewayBase: string,
  jwt: string
): Promise<GatewayResult> => {
  const res = await fetch(`${gatewayBase}/api/echo/echo`, {
    method: "GET",
    headers: { Authorization: `Bearer ${jwt}` },
    cache: "no-store",
  })
  const text = await res.text()
  return { ok: res.ok, status: res.status, data: parseJsonSafe(text) }
}

export const echoQueryKey = (gatewayBase: string) =>
  ["echo", gatewayBase] as const

export function useSuspenseEchoQuery(gatewayBase: string, jwt: string) {
  return useSuspenseQuery({
    queryKey: echoQueryKey(gatewayBase),
    queryFn: () => getEchoClient(gatewayBase, jwt),
  })
}
