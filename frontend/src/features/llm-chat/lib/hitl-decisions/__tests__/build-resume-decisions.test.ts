import { describe, expect, it } from "vitest"
import { createHitlInterrupts } from "@/features/llm-chat/testing/fixtures"
import { buildResumeDecisions } from "@/features/llm-chat/lib/hitl-decisions/build-resume-decisions"
import { buildResumeDecisionsFromForm } from "@/features/llm-chat/lib/hitl-decisions/build-resume-decisions-from-form"

describe("buildResumeDecisions", () => {
  const actionRequests = createHitlInterrupts()[0].value?.action_requests ?? []

  it("defaults to approve when no draft is provided", () => {
    expect(buildResumeDecisions(actionRequests, {})).toEqual([{ type: "approve" }])
  })

  it("builds an edit decision", () => {
    expect(
      buildResumeDecisions(actionRequests, {
        "0": {
          type: "edit",
          editedName: "send_sms",
          editedArgsText: '{"to":"+821012341234"}',
        },
      })
    ).toEqual([
      {
        type: "edit",
        editedAction: {
          name: "send_sms",
          args: { to: "+821012341234" },
        },
      },
    ])
  })

  it("trims reject messages and omits empty ones", () => {
    expect(
      buildResumeDecisions(actionRequests, {
        "0": {
          type: "reject",
          message: "  보안 검토 필요  ",
        },
      })
    ).toEqual([{ type: "reject", message: "보안 검토 필요" }])

    expect(
      buildResumeDecisions(actionRequests, {
        "0": {
          type: "reject",
          message: "   ",
        },
      })
    ).toEqual([{ type: "reject" }])
  })

  it("uses a default respond message when empty", () => {
    expect(
      buildResumeDecisions(actionRequests, {
        "0": {
          type: "respond",
          message: " ",
        },
      })
    ).toEqual([
      {
        type: "respond",
        message: "사용자가 직접 응답을 제공했습니다.",
      },
    ])
  })
})

describe("buildResumeDecisionsFromForm", () => {
  it("delegates to buildResumeDecisions using form values", () => {
    const actionRequests = createHitlInterrupts()[0].value?.action_requests ?? []

    expect(
      buildResumeDecisionsFromForm(actionRequests, {
        drafts: {
          "0": {
            type: "approve",
          },
        },
      })
    ).toEqual([{ type: "approve" }])
  })
})
