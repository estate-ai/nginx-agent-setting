import { describe, expect, it } from "vitest"
import {
  createToolPolicyState,
  llmChatTools,
} from "@/features/llm-chat/testing/fixtures"
import { buildToolPolicy } from "@/features/llm-chat/lib/tool-policy/build-tool-policy"
import { buildToolPolicySummary } from "@/features/llm-chat/lib/tool-policy/build-tool-policy-summary"

describe("buildToolPolicy", () => {
  it("marks allowed tools as auto and others as review", () => {
    const policy = buildToolPolicy(llmChatTools, new Set(["search_web"]))

    expect(policy.allowedTools).toEqual(["search_web"])
    expect(policy.interruptOn.search_web).toBe(false)
    expect(policy.interruptOn.send_email).toEqual({
      allowedDecisions: ["approve", "edit", "reject", "respond"],
    })
  })

  it("ignores unknown allowed tool names", () => {
    const policy = buildToolPolicy(llmChatTools, new Set(["missing"]))

    expect(policy.allowedTools).toEqual([])
    expect(policy.allowedToolNames.has("missing")).toBe(false)
  })
})

describe("buildToolPolicySummary", () => {
  it("formats auto/review counts", () => {
    expect(buildToolPolicySummary(2, 1)).toBe("1 auto / 1 review")
  })

  it("never returns a negative review count", () => {
    expect(buildToolPolicySummary(1, 3)).toBe("3 auto / 0 review")
  })

  it("keeps the derived summary in the fixture helper aligned", () => {
    expect(createToolPolicyState().summary).toBe("1 auto / 1 review")
  })
})
