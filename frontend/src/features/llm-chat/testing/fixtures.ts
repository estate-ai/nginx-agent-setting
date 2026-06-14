import {
  AIMessage,
  HumanMessage,
  type ToolCall,
  ToolMessage,
} from "@langchain/core/messages"
import {
  type AssembledToolCall,
  assembledToBaseMessage,
} from "@langchain/langgraph-sdk/stream"
import { buildToolPolicy } from "@/features/llm-chat/lib/tool-policy/build-tool-policy"
import { buildToolPolicySummary } from "@/features/llm-chat/lib/tool-policy/build-tool-policy-summary"
import type { ChatModelOption } from "@/features/llm-chat/types/chat-model-selection"
import type { HitlInterrupt } from "@/features/llm-chat/types/hitl-interrupt-payload"
import type { LlmToolDefinition } from "@/features/llm-chat/types/llm-tool-definition"
import type { ToolPolicyState } from "@/features/llm-chat/types/tool-policy-state"

export const llmChatModels: ChatModelOption[] = [
  {
    id: "gpt-5-mini",
    object: "model",
    created: 1,
    supportedReasoningEfforts: ["none", "low", "medium"],
  },
  {
    id: "o4",
    object: "model",
    created: 2,
    supportedReasoningEfforts: ["low", "medium", "high"],
  },
]

export const llmChatTools: LlmToolDefinition[] = [
  {
    name: "search_web",
    description: "웹에서 관련 정보를 검색합니다.",
    category: "search",
    defaultAllowed: true,
    allowedDecisions: ["approve", "reject"],
  },
  {
    name: "send_email",
    description: "외부 사용자에게 이메일을 전송합니다.",
    category: "action",
    defaultAllowed: false,
    allowedDecisions: ["approve", "edit", "reject", "respond"],
  },
]

export function createToolPolicyState(
  allowedToolNames = new Set<string>(["search_web"])
): ToolPolicyState {
  const policy = buildToolPolicy(llmChatTools, allowedToolNames)

  return {
    ...policy,
    summary: buildToolPolicySummary(
      llmChatTools.length,
      policy.allowedTools.length
    ),
  }
}

export function createReasoningMessage() {
  return assembledToBaseMessage({
    id: "ai-1",
    role: "ai",
    blocks: [
      { type: "reasoning", reasoning: "단계별 추론" },
      { type: "text", text: "최종 답변" },
    ],
  })
}

export function createUserMessage() {
  return new HumanMessage({
    id: "human-1",
    content: "사용자 질문",
  })
}

export function createToolCall(): ToolCall {
  return {
    id: "call-1",
    name: "send_email",
    args: { to: "hello@example.com", subject: "테스트" },
    type: "tool_call",
  }
}

export function createToolMessage() {
  return new ToolMessage({
    content: "발송 완료",
    tool_call_id: "call-1",
  })
}

export function createToolAiMessage() {
  return new AIMessage({
    id: "ai-tool",
    content: "",
    tool_calls: [createToolCall()],
  })
}

export function createAssembledToolCall(
  status: "pending" | "finished" | "error" = "pending"
): AssembledToolCall {
  return {
    id: "call-1",
    callId: "call-1",
    name: "send_email",
    args: { to: "hello@example.com", subject: "테스트" },
    status,
    ...(status === "finished" ? { output: { ok: true } } : {}),
    ...(status === "error" ? { error: "SMTP unavailable" } : {}),
  } as AssembledToolCall
}

export function createHitlInterrupts(): HitlInterrupt[] {
  return [
    {
      value: {
        action_requests: [
          {
            name: "send_email",
            description: "사용자에게 승인 요청 메일을 보냅니다.",
            args: {
              to: "hello@example.com",
              subject: "검토 요청",
            },
          },
        ],
        review_configs: [
          {
            action_name: "send_email",
            allowed_decisions: ["approve", "edit", "reject", "respond"],
          },
        ],
      },
    } as HitlInterrupt,
  ]
}
