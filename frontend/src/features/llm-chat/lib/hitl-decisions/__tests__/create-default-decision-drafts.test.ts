import { describe, expect, it } from "vitest"
import { createDefaultDecisionDrafts } from "@/features/llm-chat/lib/hitl-decisions/create-default-decision-drafts"
import { createHitlInterrupts } from "@/features/llm-chat/testing/fixtures"

describe("createDefaultDecisionDrafts", () => {
  it("builds approve drafts keyed by action index", () => {
    const [interrupt] = createHitlInterrupts()
    const actionRequests = interrupt.value?.action_requests ?? []

    expect(createDefaultDecisionDrafts(actionRequests)).toEqual({
      "0": {
        type: "approve",
        editedName: "send_email",
        editedArgsText: JSON.stringify(
          {
            to: "hello@example.com",
            subject: "검토 요청",
          },
          null,
          2
        ),
      },
    })
  })
})
