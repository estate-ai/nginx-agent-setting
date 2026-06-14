import { expect, fn, userEvent } from "storybook/test"
import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { HitlInterruptCard } from "@/features/llm-chat/components/hitl/hitl-interrupt-card"
import { createHitlInterrupts } from "@/features/llm-chat/testing/fixtures"

const meta = {
  title: "LLM Chat/HITL/HitlInterruptCard",
  component: HitlInterruptCard,
  tags: ["autodocs"],
  args: {
    interrupts: createHitlInterrupts(),
    onDecide: fn(),
  },
} satisfies Meta<typeof HitlInterruptCard>

export default meta

type Story = StoryObj<typeof meta>

export const Default: Story = {
  play: async ({ canvas }) => {
    await expect(
      canvas.getByText("도구 실행 승인이 필요합니다")
    ).toBeInTheDocument()
    await expect(canvas.getByText("send_email")).toBeInTheDocument()
  },
}

export const EditFlow: Story = {
  play: async ({ canvas }) => {
    await userEvent.click(canvas.getByRole("button", { name: /edit/i }))
    await expect(canvas.getByDisplayValue("send_email")).toBeInTheDocument()
  },
}

export const RespondFlow: Story = {
  play: async ({ canvas }) => {
    await userEvent.click(canvas.getByRole("button", { name: /respond/i }))
    await expect(
      canvas.getByPlaceholderText("AI에게 전달할 응답")
    ).toBeInTheDocument()
  },
}
