import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import { llmChatTools } from "@/features/llm-chat/testing/fixtures"
import { ToolPolicyList } from "@/features/llm-chat/components/tool-policy/tool-policy-list"

describe("ToolPolicyList", () => {
  it("renders one row per tool", () => {
    render(
      <ToolPolicyList
        tools={llmChatTools}
        allowedToolNames={new Set(["search_web"])}
        onToggleTool={vi.fn()}
      />
    )

    expect(screen.getByText("search_web")).toBeInTheDocument()
    expect(screen.getByText("send_email")).toBeInTheDocument()
  })

  it("passes the clicked tool name to onToggleTool", async () => {
    const onToggleTool = vi.fn()

    render(
      <ToolPolicyList
        tools={llmChatTools}
        allowedToolNames={new Set()}
        onToggleTool={onToggleTool}
      />
    )

    await userEvent.click(screen.getAllByRole("switch")[1]!)
    expect(onToggleTool).toHaveBeenCalledWith("send_email")
  })
})
