import { describe, expect, it } from "vitest"
import { parseEditedActionArgs } from "@/features/llm-chat/lib/hitl-decisions/parse-edited-action-args"

describe("parseEditedActionArgs", () => {
  it("parses a valid JSON object", () => {
    expect(parseEditedActionArgs('{"to":"hello@example.com"}')).toEqual({
      to: "hello@example.com",
    })
  })

  it("throws on invalid JSON", () => {
    expect(() => parseEditedActionArgs("{")).toThrow(
      "edited args must be valid JSON"
    )
  })

  it("throws when the JSON is not an object", () => {
    expect(() => parseEditedActionArgs('"text"')).toThrow(
      "edited args must be a JSON object"
    )
  })
})
