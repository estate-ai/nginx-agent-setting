import { useState } from "react"
import { expect, userEvent, within } from "storybook/test"
import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { ChatModelMenu } from "@/features/llm-chat/components/composer/chat-model-menu"
import { llmChatModels } from "@/features/llm-chat/testing/fixtures"
import type { ChatReasoningEffort } from "@/features/llm-chat/types/chat-model-selection"

function ChatModelMenuHarness() {
  const [selectedModelId, setSelectedModelId] = useState(llmChatModels[0].id)
  const [selectedReasoningEffort, setSelectedReasoningEffort] =
    useState<ChatReasoningEffort>("medium")

  const selectedModel =
    llmChatModels.find((model) => model.id === selectedModelId) ??
    llmChatModels[0]

  return (
    <ChatModelMenu
      models={llmChatModels}
      selectedModel={selectedModel}
      selectedReasoningEffort={selectedReasoningEffort}
      onSelectModel={setSelectedModelId}
      onSelectReasoningEffort={setSelectedReasoningEffort}
    />
  )
}

const meta = {
  title: "LLM Chat/Composer/ChatModelMenu",
  component: ChatModelMenuHarness,
  tags: ["autodocs"],
  render: () => <ChatModelMenuHarness />,
} satisfies Meta<typeof ChatModelMenuHarness>

export default meta

type Story = StoryObj<typeof meta>

export const Interactive: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await userEvent.click(canvas.getByRole("button", { name: /gpt-5-mini/i }))

    const body = within(document.body)
    await expect(body.getByText("reasoning effort")).toBeInTheDocument()
    await userEvent.click(body.getByRole("button", { name: "low" }))
    await userEvent.click(body.getByText("o4"))
    await userEvent.click(body.getByText(/^o4$/i))

    await expect(
      canvas.getByRole("button", { name: /o4/i })
    ).toBeInTheDocument()
  },
}
