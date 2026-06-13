import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { expect } from "storybook/test"
import {
  createAssembledToolCall,
  createReasoningMessage,
  createToolAiMessage,
  createToolMessage,
  createUserMessage,
} from "@/features/llm-chat/testing/fixtures"
import { SdkMessageItem } from "@/features/llm-chat/components/messages/sdk-message-item"

const meta = {
  title: "LLM Chat/Messages/SdkMessageItem",
  component: SdkMessageItem,
  tags: ["autodocs"],
} satisfies Meta<typeof SdkMessageItem>

export default meta

type Story = StoryObj<typeof meta>

export const Reasoning: Story = {
  args: {
    message: createReasoningMessage(),
    messages: [createReasoningMessage()],
    toolCalls: [],
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("thinking")).toBeInTheDocument()
    await expect(canvas.getByText("최종 답변")).toBeInTheDocument()
  },
}

export const UserMessage: Story = {
  args: {
    message: createUserMessage(),
    messages: [createUserMessage()],
    toolCalls: [],
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("사용자")).toBeInTheDocument()
    await expect(canvas.getByText("사용자 질문")).toBeInTheDocument()
  },
}

export const WithToolCall: Story = {
  args: {
    message: createToolAiMessage(),
    messages: [createToolAiMessage(), createToolMessage()],
    toolCalls: [createAssembledToolCall("finished")],
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("send_email")).toBeInTheDocument()
    await expect(canvas.getByText("완료")).toBeInTheDocument()
  },
}
