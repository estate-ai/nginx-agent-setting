import type { HumanMessage } from "@langchain/langgraph-sdk"

export const buildSubmitInput = (
  content: string
): { messages: [HumanMessage] } => ({
  messages: [
    {
      type: "human",
      content,
      id: crypto.randomUUID(),
    },
  ],
})
