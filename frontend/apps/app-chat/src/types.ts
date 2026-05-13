export type Conversation = { id: string; title: string; mode: string; updated_at: string }

export type Message = {
  id: string
  role: string
  content: string
  mode: string
  provider: string
  model: string
  request_id: string
  reasoning_summary: string
  process_steps: string[]
}

export type Attachment = { id: string; filename: string; size_bytes: number }
export type Artifact = { id: string; artifact_type: string; title: string; content_markdown: string }
export type MediaTask = { id: string; task_type: string; status: string; progress: number }
export type ModelRoute = { mode: string; display_name: string; provider: string; model: string; health_status: string }

export type ConversationDetail = {
  messages: Message[]
  attachments: Attachment[]
  artifacts: Artifact[]
  media_tasks: MediaTask[]
}
