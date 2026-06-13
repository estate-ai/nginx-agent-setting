import { describe, expect, it } from "vitest"
import {
  clampReasoningEffort,
  getDefaultReasoningEffort,
} from "@/features/llm-chat/lib/model-selection/clamp-reasoning-effort"

describe("getDefaultReasoningEffort", () => {
  it("prefers medium when supported", () => {
    expect(getDefaultReasoningEffort(["low", "medium", "high"])).toBe("medium")
  })

  it("falls back to the first supported effort", () => {
    expect(getDefaultReasoningEffort(["high", "low"])).toBe("high")
  })

  it("returns none for an empty list", () => {
    expect(getDefaultReasoningEffort([])).toBe("none")
  })
})

describe("clampReasoningEffort", () => {
  it("keeps a supported effort", () => {
    expect(clampReasoningEffort("low", ["none", "low"])).toBe("low")
  })

  it("downgrades to the highest allowed lower effort", () => {
    expect(clampReasoningEffort("high", ["low", "medium"])).toBe("medium")
  })

  it("falls back to default when no lower effort exists", () => {
    expect(clampReasoningEffort("none", ["high"])).toBe("high")
  })
})
