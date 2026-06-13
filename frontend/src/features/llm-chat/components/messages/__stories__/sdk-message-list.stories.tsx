import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { expect, within } from "storybook/test"
import {
  createAssembledToolCall,
  createReasoningMessage,
  createToolAiMessage,
  createToolMessage,
  createUserMessage,
} from "@/features/llm-chat/testing/fixtures"
import { SdkMessageList } from "@/features/llm-chat/components/messages/sdk-message-list"
import { Alert, AlertDescription } from "@/shared/components/ui/alert"

const meta = {
  title: "LLM Chat/Messages/SdkMessageList",
  component: SdkMessageList,
  tags: ["autodocs"],
} satisfies Meta<typeof SdkMessageList>

export default meta

type Story = StoryObj<typeof meta>

export const ConversationWithNotice: Story = {
  args: {
    messages: [
      createUserMessage(),
      createReasoningMessage(),
      createToolAiMessage(),
      createToolMessage(),
    ],
    toolCalls: [createAssembledToolCall("finished")],
    children: (
      <Alert variant="destructive">
        <AlertDescription>로컬 알림 예시</AlertDescription>
      </Alert>
    ),
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await expect(canvas.getByText("사용자 질문")).toBeInTheDocument()
    await expect(canvas.getByText("최종 답변")).toBeInTheDocument()
    await expect(canvas.getByText("send_email")).toBeInTheDocument()
    await expect(canvas.getByText("로컬 알림 예시")).toBeInTheDocument()
  },
}
