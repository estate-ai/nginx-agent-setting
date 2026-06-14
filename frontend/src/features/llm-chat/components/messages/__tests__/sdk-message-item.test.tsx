import { describe, expect, it } from "vitest"
import { render, screen } from "@testing-library/react"
import { SdkMessageItem } from "@/features/llm-chat/components/messages/sdk-message-item"
import {
  createAssembledToolCall,
  createReasoningMessage,
  createToolAiMessage,
  createToolMessage,
  createUserMessage,
} from "@/features/llm-chat/testing/fixtures"

describe("SdkMessageItem", () => {
  it("renders reasoning separately from answer text", () => {
    const message = createReasoningMessage()

    render(
      <SdkMessageItem message={message} messages={[message]} toolCalls={[]} />
    )

    expect(screen.getByText("thinking")).toBeInTheDocument()
    expect(screen.getByText("단계별 추론")).toBeInTheDocument()
    expect(screen.getByText("최종 답변")).toBeInTheDocument()
  })

  it("renders user messages with the correct label", () => {
    const message = createUserMessage()

    render(
      <SdkMessageItem message={message} messages={[message]} toolCalls={[]} />
    )

    expect(screen.getByText("사용자")).toBeInTheDocument()
    expect(screen.getByText("사용자 질문")).toBeInTheDocument()
  })

  it("does not render tool messages directly", () => {
    const { container } = render(
      <SdkMessageItem
        message={createToolMessage()}
        messages={[createToolMessage()]}
        toolCalls={[]}
      />
    )

    expect(container).toBeEmptyDOMElement()
  })

  it("pairs AI tool calls with assembled results", () => {
    const message = createToolAiMessage()

    render(
      <SdkMessageItem
        message={message}
        messages={[message, createToolMessage()]}
        toolCalls={[createAssembledToolCall("finished")]}
      />
    )

    expect(screen.getByText("send_email")).toBeInTheDocument()
    expect(screen.getByText("완료")).toBeInTheDocument()
    expect(screen.getByText(/발송 완료/)).toBeInTheDocument()
  })
})
