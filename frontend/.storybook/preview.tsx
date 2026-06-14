import { type PropsWithChildren, useState } from "react"
import type { Preview } from "@storybook/nextjs-vite"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { queryConfig } from "@/shared/lib/react-query"
import "../src/app/globals.css"

function StorybookProviders({ children }: PropsWithChildren) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: queryConfig,
      })
  )

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    layout: "centered",
  },
  decorators: [
    (Story) => (
      <StorybookProviders>
        <div className="min-h-screen min-w-80 bg-background p-6 text-foreground">
          <Story />
        </div>
      </StorybookProviders>
    ),
  ],
}

export default preview
