import { createRef } from "react"
import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { ChatComposerTextarea } from "@/features/llm-chat/components/composer/chat-composer-textarea"

describe("ChatComposerTextarea", () => {
  it("submits on Enter without Shift", () => {
    const onSubmit = vi.fn()

    render(
      <ChatComposerTextarea
        disabled={false}
        textareaRef={createRef<HTMLTextAreaElement>()}
        onSubmit={onSubmit}
      />
    )

    fireEvent.keyDown(screen.getByPlaceholderText(/메시지 입력/), {
      key: "Enter",
    })

    expect(onSubmit).toHaveBeenCalled()
  })

  it("does not submit on Shift+Enter", () => {
    const onSubmit = vi.fn()

    render(
      <ChatComposerTextarea
        disabled={false}
        textareaRef={createRef<HTMLTextAreaElement>()}
        onSubmit={onSubmit}
      />
    )

    fireEvent.keyDown(screen.getByPlaceholderText(/메시지 입력/), {
      key: "Enter",
      shiftKey: true,
    })

    expect(onSubmit).not.toHaveBeenCalled()
  })
})
