import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import {
  createToolPolicyState,
  llmChatTools,
} from "@/features/llm-chat/testing/fixtures"
import { ChatComposer } from "@/features/llm-chat/components/composer/chat-composer"

describe("ChatComposer", () => {
  it("does not submit an empty message", async () => {
    const onSubmit = vi.fn()

    render(
      <ChatComposer
        disabled={false}
        onSubmit={onSubmit}
        tools={llmChatTools}
        toolPolicy={createToolPolicyState()}
        onToggleTool={vi.fn()}
        streamStatus="idle"
        modelControl={<div>model control</div>}
      />
    )

    await userEvent.click(screen.getByRole("button", { name: /전송/i }))
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it("submits trimmed text and clears the textarea", async () => {
    const onSubmit = vi.fn()

    render(
      <ChatComposer
        disabled={false}
        onSubmit={onSubmit}
        tools={llmChatTools}
        toolPolicy={createToolPolicyState()}
        onToggleTool={vi.fn()}
        streamStatus="idle"
        modelControl={<div>model control</div>}
      />
    )

    const textarea = screen.getByPlaceholderText(/메시지 입력/) as HTMLTextAreaElement
    await userEvent.type(textarea, "  안녕하세요  ")
    await userEvent.click(screen.getByRole("button", { name: /전송/i }))

    expect(onSubmit).toHaveBeenCalledWith("안녕하세요")
    expect(textarea.value).toBe("")
  })

  it("does not submit while disabled", async () => {
    const onSubmit = vi.fn()

    render(
      <ChatComposer
        disabled
        onSubmit={onSubmit}
        tools={llmChatTools}
        toolPolicy={createToolPolicyState()}
        onToggleTool={vi.fn()}
        streamStatus="streaming"
        modelControl={<div>model control</div>}
      />
    )

    expect(screen.getByRole("button", { name: /전송/i })).toBeDisabled()
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
