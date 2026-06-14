import { expect } from "storybook/test"
import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { EmptyChatState } from "@/features/llm-chat/components/empty-chat-state"

const meta = {
  title: "LLM Chat/Components/EmptyChatState",
  component: EmptyChatState,
  tags: ["autodocs"],
} satisfies Meta<typeof EmptyChatState>

export default meta

type Story = StoryObj<typeof meta>

export const Default: Story = {
  play: async ({ canvas }) => {
    await expect(
      canvas.getByText("메시지를 입력해 대화를 시작하세요.")
    ).toBeInTheDocument()
  },
}
