import { describe, expect, it, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import { AppShell } from "@/shared/components/layout/app-shell"

vi.mock("@/features/auth/components/header/header-auth-button", () => ({
  HeaderAuthButton: () => <div>HeaderAuthButton</div>,
}))

vi.mock(
  "@/features/auth/components/header/header-auth-button-fallback",
  () => ({
    HeaderAuthButtonFallback: () => <div>HeaderAuthButtonFallback</div>,
  })
)

vi.mock("@/shared/components/layout/header-nav-button", () => ({
  HeaderNavButton: ({ label }: { label: string }) => <div>{label}</div>,
}))

describe("AppShell", () => {
  it("renders the header auth control instead of the old profile link", () => {
    render(
      <AppShell>
        <div>content</div>
      </AppShell>
    )

    expect(screen.getByText("HeaderAuthButton")).toBeInTheDocument()
    expect(screen.queryByText("User Profile")).not.toBeInTheDocument()
  })
})
