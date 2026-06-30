"use client"

import type { ReactNode } from "react"
import { useRouter, useSelectedLayoutSegment } from "next/navigation"
import {
  Fingerprint,
  Folder,
  MapPinned,
  Menu,
  MessageSquare,
  NotebookPen,
  X,
} from "lucide-react"
import { toast } from "sonner"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { HttpStatusError } from "@/features/auth/lib/fetch-with-auth"
import { LibraryPanel } from "@/features/chat/components/workspace/library-panel"
import { MarketFavoritesPanel } from "@/features/chat/components/workspace/market-favorites-panel"
import { MemoryPanel } from "@/features/chat/components/workspace/memory-panel"
import {
  OnboardingPanel,
  type OnboardingPanelItem,
} from "@/features/chat/components/workspace/onboarding-panel"
import { ThreadList } from "@/features/chat/components/workspace/thread-list"
import { WorkspaceDetailDialog } from "@/features/chat/components/workspace/workspace-detail-dialog"
import { useChatWorkspace } from "@/features/chat/providers/chat-workspace-provider"
import type {
  ChatDetailDialogPayload,
  ChatOnboardingResultPreview,
  ChatOnboardingSelection,
} from "@/features/chat/types/workspace"
import { useListDocumentsApiV1AgentDocumentsGet } from "@/shared/api/generated/agent/endpoints/agent-documents/agent-documents"
import { useListMarketFavoritesApiV1AgentMarketFavoritesGet } from "@/shared/api/generated/agent/endpoints/agent-market-favorites/agent-market-favorites"
import { useListMemoriesApiV1AgentMemoriesGet } from "@/shared/api/generated/agent/endpoints/agent-memories/agent-memories"
import {
  getListThreadsApiV1AgentThreadsGetQueryKey,
  useDeleteThreadApiV1AgentThreadsThreadIdDelete,
  useListThreadsApiV1AgentThreadsGet,
} from "@/shared/api/generated/agent/endpoints/agent-threads/agent-threads"
import {
  getGetMySurveyProfileSurveysMeProfileGetQueryKey,
  getMySurveyProfileSurveysMeProfileGet,
  useGetSavedSurveyResultsSurveysMeSavedResultsGet,
} from "@/shared/api/generated/onboarding/endpoints/survey/survey"
import type {
  SavedSurveyResultSummary,
  SurveyResultResponse,
} from "@/shared/api/generated/onboarding/schemas"
import { Button } from "@/shared/components/ui/button"
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/shared/components/ui/resizable"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/shared/components/ui/tooltip"
import { cn } from "@/shared/lib/utils"

type ChatWorkspaceFrameProps = {
  children: ReactNode
}

export function ChatWorkspaceFrame({ children }: ChatWorkspaceFrameProps) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const currentThreadSegment = useSelectedLayoutSegment()
  const currentThreadId = currentThreadSegment ?? null
  const activeLeftTab = useChatWorkspace((state) => state.activeLeftTab)
  const detailDialog = useChatWorkspace((state) => state.detailDialog)
  const isLeftSidebarOpen = useChatWorkspace((state) => state.isLeftSidebarOpen)
  const selectedDocumentIds = useChatWorkspace(
    (state) => state.selectedDocumentIds
  )
  const selectedMarketDongCodes = useChatWorkspace(
    (state) => state.selectedMarketDongCodes
  )
  const selectedOnboarding = useChatWorkspace(
    (state) => state.selectedOnboarding
  )
  const setDetailDialog = useChatWorkspace((state) => state.setDetailDialog)
  const setActiveLeftTab = useChatWorkspace((state) => state.setActiveLeftTab)
  const setIsLeftSidebarOpen = useChatWorkspace(
    (state) => state.setIsLeftSidebarOpen
  )
  const toggleDocument = useChatWorkspace((state) => state.toggleDocument)
  const toggleMarketArea = useChatWorkspace((state) => state.toggleMarketArea)
  const setSelectedOnboarding = useChatWorkspace(
    (state) => state.setSelectedOnboarding
  )
  const threadsQuery = useListThreadsApiV1AgentThreadsGet()
  const documentsQuery = useListDocumentsApiV1AgentDocumentsGet()
  const marketFavoritesQuery =
    useListMarketFavoritesApiV1AgentMarketFavoritesGet()
  const memoriesQuery = useListMemoriesApiV1AgentMemoriesGet()
  const deleteThread = useDeleteThreadApiV1AgentThreadsThreadIdDelete()

  const documents = documentsQuery.data?.documents ?? []
  const marketFavorites = marketFavoritesQuery.data?.favorites ?? []
  const threads = threadsQuery.data?.threads ?? []
  const memories = memoriesQuery.data?.memories ?? []
  const scopedDetailDialog =
    detailDialog?.scopeThreadId === currentThreadId ? detailDialog : null
  const isOnboardingTabActive =
    activeLeftTab === "onboarding" && isLeftSidebarOpen
  const defaultProfileQuery = useQuery({
    queryKey: getGetMySurveyProfileSurveysMeProfileGetQueryKey(),
    enabled:
      isOnboardingTabActive || scopedDetailDialog?.kind === "onboarding-result",
    retry: false,
    queryFn: () => readOptionalResource(getMySurveyProfileSurveysMeProfileGet),
  })
  const savedResultsQuery = useGetSavedSurveyResultsSurveysMeSavedResultsGet({
    query: {
      enabled: isOnboardingTabActive,
    },
  })
  const defaultProfile = defaultProfileQuery.data ?? null
  const onboardingItems = buildOnboardingPanelItems({
    currentResultCode: selectedOnboarding?.resultCode ?? null,
    defaultProfile,
    savedResults: savedResultsQuery.data?.results ?? [],
  })
  const mainPanelDefaultSize = isLeftSidebarOpen ? "76%" : "100%"
  const activityButtonClassName =
    "size-8 cursor-pointer rounded-md text-muted-foreground transition-colors hover:bg-muted/70 hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/30"
  const activeActivityButtonClassName =
    "bg-muted text-foreground ring-1 ring-border/40 hover:bg-muted"

  const invalidateThreads = () => {
    void queryClient.invalidateQueries({
      queryKey: getListThreadsApiV1AgentThreadsGetQueryKey(),
    })
  }

  const handleCreateThread = () => {
    router.push("/chat")
  }

  const handleDeleteThread = (threadId: string) => {
    deleteThread.mutate(
      { threadId },
      {
        onSuccess: () => {
          invalidateThreads()
          if (currentThreadId === threadId) {
            router.push("/chat")
          }
          toast("대화가 삭제되었습니다.")
        },
      }
    )
  }

  const openDetailDialog = (nextDialog: ChatDetailDialogPayload) => {
    setDetailDialog({
      ...nextDialog,
      scopeThreadId: currentThreadId,
    })
    if (window.innerWidth < 768) {
      setIsLeftSidebarOpen(false)
    }
  }

  const handleToggleOnboardingContext = (
    result: ChatOnboardingResultPreview
  ) => {
    const isAttached = selectedOnboarding?.resultCode === result.resultCode

    if (isAttached) {
      setSelectedOnboarding(null)
      toast("성향분석을 채팅에서 제거했습니다.")
      return
    }

    setSelectedOnboarding({
      resultCode: result.resultCode,
      profileName: result.profileName,
      selectedCategoryCode: result.selectedCategoryCode ?? null,
    } satisfies ChatOnboardingSelection)
    toast.success("성향분석을 채팅에 추가했습니다.")
  }

  return (
    <div className="relative flex h-[calc(100dvh-4rem)] w-full overflow-hidden bg-background text-foreground">
      <div className="relative z-0 flex w-10 shrink-0 flex-col items-center justify-between border-r border-border/30 bg-background/95 py-3">
        <div className="flex flex-col gap-2">
          <ActivityButton
            className={cn(
              activityButtonClassName,
              activeLeftTab === "threads" && isLeftSidebarOpen
                ? activeActivityButtonClassName
                : "hover:bg-muted/70"
            )}
            label="채팅 목록"
            onClick={() => {
              setActiveLeftTab("threads")
              setIsLeftSidebarOpen(true)
            }}
          >
            <MessageSquare className="size-4" />
          </ActivityButton>
          <ActivityButton
            className={cn(
              activityButtonClassName,
              activeLeftTab === "library" && isLeftSidebarOpen
                ? activeActivityButtonClassName
                : "hover:bg-muted/70"
            )}
            label="라이브러리"
            onClick={() => {
              setActiveLeftTab("library")
              setIsLeftSidebarOpen(true)
            }}
          >
            <Folder className="size-4" />
          </ActivityButton>
          <ActivityButton
            className={cn(
              activityButtonClassName,
              activeLeftTab === "onboarding" && isLeftSidebarOpen
                ? activeActivityButtonClassName
                : "hover:bg-muted/70"
            )}
            label="성향분석"
            onClick={() => {
              setActiveLeftTab("onboarding")
              setIsLeftSidebarOpen(true)
            }}
          >
            <Fingerprint className="size-4" />
          </ActivityButton>
          <ActivityButton
            className={cn(
              activityButtonClassName,
              activeLeftTab === "market-favorites" && isLeftSidebarOpen
                ? activeActivityButtonClassName
                : "hover:bg-muted/70"
            )}
            label="관심 상권"
            onClick={() => {
              setActiveLeftTab("market-favorites")
              setIsLeftSidebarOpen(true)
            }}
          >
            <MapPinned className="size-4" />
          </ActivityButton>
          <ActivityButton
            className={cn(
              activityButtonClassName,
              activeLeftTab === "memory" && isLeftSidebarOpen
                ? activeActivityButtonClassName
                : "hover:bg-muted/70"
            )}
            label="AI 메모리"
            onClick={() => {
              setActiveLeftTab("memory")
              setIsLeftSidebarOpen(true)
            }}
          >
            <NotebookPen className="size-4" />
          </ActivityButton>
        </div>
      </div>

      {isLeftSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={() => setIsLeftSidebarOpen(false)}
        />
      )}

      <div className="relative flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={() => setIsLeftSidebarOpen(!isLeftSidebarOpen)}
          className="absolute top-3 left-3 z-30 cursor-pointer md:hidden"
          id="mobile-menu-btn"
        >
          {isLeftSidebarOpen ? (
            <X className="size-4" />
          ) : (
            <Menu className="size-4" />
          )}
        </Button>

        <ResizablePanelGroup orientation="horizontal" className="h-full w-full">
          {isLeftSidebarOpen && (
            <>
              <ResizablePanel defaultSize="24%" minSize="18%" maxSize="36%">
                {activeLeftTab === "threads" && (
                  <ThreadList
                    threads={threads}
                    isLoading={threadsQuery.isLoading}
                    activeThreadId={currentThreadId}
                    onSelectThread={(threadId) => {
                      router.push(`/chat/${threadId}`)
                      if (window.innerWidth < 768) {
                        setIsLeftSidebarOpen(false)
                      }
                    }}
                    onCreateThread={handleCreateThread}
                    onDeleteThread={handleDeleteThread}
                    onToggleCollapse={() => setIsLeftSidebarOpen(false)}
                  />
                )}
                {activeLeftTab === "library" && (
                  <LibraryPanel
                    documents={documents}
                    isLoading={documentsQuery.isLoading}
                    selectedDocumentIds={selectedDocumentIds}
                    onToggleDocument={toggleDocument}
                    onOpenDocument={(document) =>
                      openDetailDialog({
                        kind: "library-document",
                        document,
                      })
                    }
                    onCollapsePanel={() => setIsLeftSidebarOpen(false)}
                    side="left"
                  />
                )}
                {activeLeftTab === "onboarding" && (
                  <OnboardingPanel
                    items={onboardingItems}
                    isLoading={
                      defaultProfileQuery.isLoading ||
                      savedResultsQuery.isLoading
                    }
                    isInteractionPending={false}
                    onOpenResult={(result) =>
                      openDetailDialog({
                        kind: "onboarding-result",
                        result,
                      })
                    }
                    onToggleContext={handleToggleOnboardingContext}
                    onCollapsePanel={() => setIsLeftSidebarOpen(false)}
                  />
                )}
                {activeLeftTab === "market-favorites" && (
                  <MarketFavoritesPanel
                    favorites={marketFavorites}
                    isLoading={marketFavoritesQuery.isLoading}
                    selectedMarketDongCodes={selectedMarketDongCodes}
                    onToggleMarketArea={toggleMarketArea}
                    onOpenFavorite={(favorite) =>
                      openDetailDialog({
                        kind: "market-favorite",
                        favorite,
                      })
                    }
                    onCollapsePanel={() => setIsLeftSidebarOpen(false)}
                  />
                )}
                {activeLeftTab === "memory" && (
                  <MemoryPanel
                    memories={memories}
                    isLoading={memoriesQuery.isLoading}
                    onCloseSidebar={() => setIsLeftSidebarOpen(false)}
                  />
                )}
              </ResizablePanel>
              <ResizableHandle
                withHandle
                className="z-10 !w-1.5 cursor-col-resize bg-border/40 transition-colors hover:bg-primary/40"
              />
            </>
          )}

          <ResizablePanel defaultSize={mainPanelDefaultSize} minSize="40%">
            {/* 좌측 공통 프레임을 layout에 고정해 스레드 이동 시에도 유지합니다. */}
            {children}
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>

      <WorkspaceDetailDialog
        currentOnboardingSelection={selectedOnboarding}
        currentThreadId={currentThreadId}
        defaultProfile={defaultProfile}
        dialog={scopedDetailDialog}
        isOnboardingContextPending={false}
        onClose={() => setDetailDialog(null)}
        onToggleOnboardingContext={handleToggleOnboardingContext}
      />
    </div>
  )
}

function ActivityButton({
  children,
  className,
  label,
  onClick,
}: {
  children: ReactNode
  className: string
  label: string
  onClick: () => void
}) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClick}
            className={className}
          >
            {children}
          </Button>
        </TooltipTrigger>
        <TooltipContent side="right">{label}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

const readOptionalResource = async <T,>(loader: () => Promise<T>) => {
  try {
    return await loader()
  } catch (error) {
    if (error instanceof HttpStatusError && error.status === 404) {
      return null
    }
    throw error
  }
}

const buildOnboardingPanelItems = ({
  currentResultCode,
  defaultProfile,
  savedResults,
}: {
  currentResultCode: string | null
  defaultProfile: SurveyResultResponse | null
  savedResults: SavedSurveyResultSummary[]
}) => {
  const items: OnboardingPanelItem[] = []

  if (defaultProfile) {
    items.push({
      resultCode: defaultProfile.result_code,
      profileName: defaultProfile.profile_name,
      isDefault: true,
      savedLabel: "기본 프로필",
      savedSource: "default_profile",
      createdAt: defaultProfile.created_at,
      isAttached: currentResultCode === defaultProfile.result_code,
    })
  }

  for (const result of savedResults) {
    if (result.result_code === defaultProfile?.result_code) {
      continue
    }

    items.push({
      resultCode: result.result_code,
      profileName: result.profile_name,
      isDefault: false,
      savedLabel: result.saved_label,
      savedSource: result.saved_source,
      createdAt: result.saved_at,
      isAttached: currentResultCode === result.result_code,
    })
  }

  return items
}
