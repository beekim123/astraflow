import type { ModelRoute } from "./types"

export const DEFAULT_MODEL_ROUTE: ModelRoute = {
  mode: "mock",
  display_name: "开发 Mock",
  provider: "mock",
  model: "mock-assistant",
  health_status: "healthy",
}

export const TASK_TYPE_OPTIONS = [
  { value: "chat-general", label: "通用助手", shortLabel: "通用" },
  { value: "file-analysis", label: "资料分析", shortLabel: "资料" },
  { value: "image-analysis", label: "图片理解", shortLabel: "图片" },
  { value: "video-task", label: "视频任务", shortLabel: "视频" },
  { value: "ticket-draft", label: "工单草稿", shortLabel: "工单" },
]

export function getTaskTypeLabel(taskType: string) {
  return TASK_TYPE_OPTIONS.find((item) => item.value === taskType)?.shortLabel || "通用"
}
