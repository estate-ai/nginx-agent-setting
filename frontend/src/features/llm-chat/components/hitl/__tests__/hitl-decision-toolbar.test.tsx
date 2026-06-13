import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import { HitlDecisionToolbar } from "@/features/llm-chat/components/hitl/hitl-decision-toolbar"

describe("HitlDecisionToolbar", () => {
  it("shows only allowed decision buttons", () => {
    render(
      <HitlDecisionToolbar
        activeDecision="approve"
        allowedDecisions={["approve", "reject"]}
        onSelect={vi.fn()}
      />
    )

    expect(screen.getByRole("button", { name: /approve/i })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /reject/i })).toBeInTheDocument()
    expect(
      screen.queryByRole("button", { name: /respond/i })
    ).not.toBeInTheDocument()
  })

  it("calls onSelect when a button is clicked", async () => {
    const onSelect = vi.fn()

    render(
      <HitlDecisionToolbar
        activeDecision="approve"
        allowedDecisions={["approve", "edit"]}
        onSelect={onSelect}
      />
    )

    await userEvent.click(screen.getByRole("button", { name: /edit/i }))
    expect(onSelect).toHaveBeenCalledWith("edit")
  })
})
