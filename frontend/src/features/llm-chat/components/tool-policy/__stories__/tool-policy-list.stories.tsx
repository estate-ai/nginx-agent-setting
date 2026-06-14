import { useState } from "react"
import { expect, userEvent } from "storybook/test"
import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { ToolPolicyList } from "@/features/llm-chat/components/tool-policy/tool-policy-list"
import { llmChatTools } from "@/features/llm-chat/testing/fixtures"

function ToolPolicyListHarness() {
  const [allowedToolNames, setAllowedToolNames] = useState(
    new Set<string>(["search_web"])
  )

  return (
    <ToolPolicyList
      tools={llmChatTools}
      allowedToolNames={allowedToolNames}
      onToggleTool={(toolName) => {
        setAllowedToolNames((current) => {
          const next = new Set(current)
          if (next.has(toolName)) {
            next.delete(toolName)
          } else {
            next.add(toolName)
          }
          return next
        })
      }}
    />
  )
}

const meta = {
  title: "LLM Chat/ToolPolicy/ToolPolicyList",
  component: ToolPolicyListHarness,
  tags: ["autodocs"],
  render: () => <ToolPolicyListHarness />,
} satisfies Meta<typeof ToolPolicyListHarness>

export default meta

type Story = StoryObj<typeof meta>

export const Interactive: Story = {
  play: async ({ canvas }) => {
    const switches = canvas.getAllByRole("switch")
    await userEvent.click(switches[1])
    await expect(canvas.getAllByText("auto")).toHaveLength(2)
  },
}
