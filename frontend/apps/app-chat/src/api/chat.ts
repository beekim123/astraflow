import { api, authFetch, unwrap } from "@astraflow/shared-api"
import type { Attachment, Conversation, ConversationDetail, ModelRoute } from "../types"

export type StreamMessagePayload = {
  content: string
  mode: string
  task_type: string
  attachment_ids: string[]
}

export type ChatStreamEvent = {
  type: string
  content?: string
  data?: {
    items?: unknown[]
    [key: string]: unknown
  }
  reasoning_summary?: string
  process_steps?: string[]
}

export function listConversations() {
  return unwrap<Conversation[]>(api.get("/chat/conversations"))
}

export function listModelRoutes() {
  return unwrap<ModelRoute[]>(api.get("/chat/model-routes"))
}

export function createChatConversation() {
  return unwrap<Conversation>(api.post("/chat/conversations", { title: "AI 工作台会话", mode: "general" }))
}

export function getConversationDetail(id: string) {
  return unwrap<ConversationDetail>(api.get(`/chat/conversations/${id}`))
}

export function uploadConversationAttachment(conversationId: string, file: File) {
  const form = new FormData()
  form.append("file", file)
  return unwrap<Attachment>(api.post(`/chat/conversations/${conversationId}/attachments`, form))
}

export function exportChatArtifact(artifactId: string) {
  return unwrap(api.post(`/chat/artifacts/${artifactId}/export`))
}

export function createChatDraft(artifactId: string) {
  return unwrap<{ title: string }>(api.post(`/chat/artifacts/${artifactId}/draft`))
}

export async function streamConversationMessage(
  conversationId: string,
  payload: StreamMessagePayload,
  options: { signal?: AbortSignal; onEvent: (event: ChatStreamEvent) => void },
) {
  const response = await authFetch(`/chat/conversations/${conversationId}/messages/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: options.signal,
  })

  if (!response.ok || !response.body) {
    throw new Error(await getStreamErrorMessage(response))
  }

  await consumeSseStream(response.body, options.onEvent)
}

async function consumeSseStream(body: ReadableStream<Uint8Array>, onEvent: (event: ChatStreamEvent) => void) {
  const reader = body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split("\n\n")
    buffer = parts.pop() || ""
    for (const part of parts) {
      parseSseBlock(part, onEvent)
    }
  }

  if (buffer.trim()) {
    parseSseBlock(buffer, onEvent)
  }
}

function parseSseBlock(block: string, onEvent: (event: ChatStreamEvent) => void) {
  const payload = block
    .split("\n")
    .filter((line) => line.startsWith("data: "))
    .map((line) => line.slice(6))
    .join("\n")

  if (!payload) return
  onEvent(JSON.parse(payload) as ChatStreamEvent)
}

async function getStreamErrorMessage(response: Response) {
  try {
    const data = (await response.json()) as { message?: string }
    if (data.message) return data.message
  } catch {
    // The streaming endpoint may fail before returning a JSON body.
  }
  return `流式请求失败：HTTP ${response.status}`
}
