import { expect } from "storybook/test"
import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { SdkToolCallCard } from "@/features/llm-chat/components/messages/sdk-tool-call-card"
import {
  createAssembledToolCall,
  createToolCall,
  createToolMessage,
} from "@/features/llm-chat/testing/fixtures"

const meta = {
  title: "LLM Chat/Messages/SdkToolCallCard",
  component: SdkToolCallCard,
  tags: ["autodocs"],
  args: {
    call: createToolCall(),
  },
} satisfies Meta<typeof SdkToolCallCard>

export default meta

type Story = StoryObj<typeof meta>

export const Pending: Story = {
  args: {
    assembled: createAssembledToolCall("pending"),
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("실행 중")).toBeInTheDocument()
  },
}

export const Completed: Story = {
  args: {
    assembled: createAssembledToolCall("finished"),
    result: createToolMessage(),
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("완료")).toBeInTheDocument()
    await expect(canvas.getByText(/발송 완료/)).toBeInTheDocument()
  },
}

export const Error: Story = {
  args: {
    assembled: createAssembledToolCall("error"),
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("오류")).toBeInTheDocument()
    await expect(canvas.getByText(/SMTP unavailable/)).toBeInTheDocument()
  },
}
