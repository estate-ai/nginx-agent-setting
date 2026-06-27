import { z } from "zod"
import { ChatWorkspaceThreadView } from "@/features/chat/components/workspace/chat-workspace-thread-view"

const getSearchParamList = (value: unknown) => {
  if (Array.isArray(value)) {
    return value.filter(
      (item): item is string => typeof item === "string" && item.length > 0
    )
  }

  if (typeof value === "string" && value.length > 0) {
    return [value]
  }

  return []
}

const ChatThreadSearchParamsSchema = z.object({
  starter: z.preprocess(
    (value) => getSearchParamList(value)[0],
    z.string().optional()
  ),
  documentId: z.preprocess(getSearchParamList, z.array(z.string())),
  artifactId: z.preprocess(getSearchParamList, z.array(z.string())),
})

type ChatThreadPageProps = {
  params: Promise<{
    threadId: string
  }>
  searchParams?: Promise<Record<string, unknown> | undefined>
}

export default async function ChatThreadPage(props: ChatThreadPageProps) {
  const { threadId } = await props.params
  const rawSearchParams = (await props.searchParams) ?? {}
  const parsedSearchParams =
    ChatThreadSearchParamsSchema.safeParse(rawSearchParams)
  const starterPayload = parsedSearchParams.success
    ? parsedSearchParams.data
    : {
        starter: undefined,
        documentId: [],
        artifactId: [],
      }

  return (
    <ChatWorkspaceThreadView
      threadId={threadId}
      starterMessage={starterPayload.starter ?? null}
      starterSelections={{
        selectedArtifactIds: starterPayload.artifactId,
        selectedDocumentIds: starterPayload.documentId,
      }}
    />
  )
}
