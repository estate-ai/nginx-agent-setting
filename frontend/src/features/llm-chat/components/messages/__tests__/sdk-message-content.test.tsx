import { describe, expect, it } from "vitest"
import { render, screen } from "@testing-library/react"
import { SdkMessageContent } from "@/features/llm-chat/components/messages/sdk-message-content"
import { createReasoningMessage } from "@/features/llm-chat/testing/fixtures"

describe("SdkMessageContent", () => {
  it("renders only the visible text projection", () => {
    render(<SdkMessageContent message={createReasoningMessage()} />)

    expect(screen.getByText("최종 답변")).toBeInTheDocument()
    expect(screen.queryByText("단계별 추론")).not.toBeInTheDocument()
  })

  it("renders nothing when a message has no text", () => {
    const { container } = render(
      <SdkMessageContent
        message={
          {
            id: "empty",
            text: "",
          } as never
        }
      />
    )

    expect(container).toBeEmptyDOMElement()
  })
})
