<template>
  <main class="chat-app" :class="{ 'sidebar-open': mobileSidebarOpen }">
    <ConversationSidebar
      :conversations="conversations"
      :active-conversation-id="activeConversationId"
      :open="mobileSidebarOpen"
      @close="mobileSidebarOpen = false"
      @create="createConversation"
      @select="selectConversation"
    />

    <section class="chat-panel">
      <ChatHeader
        v-model:mode="mode"
        v-model:task-type="taskType"
        :model-routes="modelRoutes"
        :task-type-label="taskTypeLabel"
        @open-sidebar="mobileSidebarOpen = true"
        @create-conversation="createConversation"
      />

      <MessageList
        ref="messageListRef"
        :messages="messages"
        :streaming-text="streamingText"
        :streaming-thought="streamingThought"
        :streaming-steps="streamingSteps"
        :show-streaming-message="showStreamingMessage"
      />

      <ArtifactDrawer
        :artifacts="artifacts"
        :media-tasks="mediaTasks"
        @export-artifact="exportArtifact"
        @create-draft="createDraft"
      />

      <ComposerBox
        v-model:draft="draft"
        :sending="sending"
        :error="error"
        :attachments="attachments"
        @send="send"
        @stop="stopStreaming"
        @upload="uploadFiles"
      />
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { ElMessage } from "element-plus"
import { getApiErrorMessage } from "@astraflow/shared-api"
import {
  createChatConversation,
  createChatDraft,
  exportChatArtifact,
  getConversationDetail,
  listConversations,
  listModelRoutes,
  streamConversationMessage,
  uploadConversationAttachment,
  type ChatStreamEvent,
} from "./api/chat"
import ArtifactDrawer from "./components/ArtifactDrawer.vue"
import ChatHeader from "./components/ChatHeader.vue"
import ComposerBox from "./components/ComposerBox.vue"
import ConversationSidebar from "./components/ConversationSidebar.vue"
import MessageList from "./components/MessageList.vue"
import { DEFAULT_MODEL_ROUTE, getTaskTypeLabel } from "./constants"
import type { Artifact, Attachment, Conversation, MediaTask, Message, ModelRoute } from "./types"

const conversations = ref<Conversation[]>([])
const messages = ref<Message[]>([])
const attachments = ref<Attachment[]>([])
const artifacts = ref<Artifact[]>([])
const mediaTasks = ref<MediaTask[]>([])
const modelRoutes = ref<ModelRoute[]>([DEFAULT_MODEL_ROUTE])
const activeConversationId = ref("")
const draft = ref("")
const mode = ref("mock")
const taskType = ref("chat-general")
const sending = ref(false)
const streamingText = ref("")
const streamingThought = ref("")
const streamingSteps = ref<string[]>([])
const error = ref("")
const mobileSidebarOpen = ref(false)
const pendingAttachmentIds = ref<string[]>([])
const messageListRef = ref<InstanceType<typeof MessageList> | null>(null)

let activeAbortController: AbortController | null = null

const showStreamingMessage = computed(() => Boolean(streamingText.value || streamingThought.value || streamingSteps.value.length || sending.value))
const taskTypeLabel = computed(() => getTaskTypeLabel(taskType.value))

async function scrollToBottom(smooth = false) {
  await messageListRef.value?.scrollToBottom(smooth)
}

async function loadConversations() {
  conversations.value = await listConversations()
}

async function loadModelRoutes() {
  const routes = await listModelRoutes()
  if (routes.length === 0) return
  modelRoutes.value = routes
  if (!routes.some((item) => item.mode === mode.value)) {
    mode.value = routes[0].mode
  }
}

async function createConversation() {
  const item = await createChatConversation()
  await loadConversations()
  await selectConversation(item.id)
  mobileSidebarOpen.value = false
}

async function selectConversation(id: string) {
  mobileSidebarOpen.value = false
  activeConversationId.value = id
  const detail = await getConversationDetail(id)
  messages.value = detail.messages
  attachments.value = detail.attachments
  artifacts.value = detail.artifacts
  mediaTasks.value = detail.media_tasks
  await scrollToBottom(false)
}

async function uploadFiles(event: Event) {
  if (!activeConversationId.value) await createConversation()
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])
  for (const file of files) {
    const uploaded = await uploadConversationAttachment(activeConversationId.value, file)
    pendingAttachmentIds.value.push(uploaded.id)
  }
  input.value = ""
  await selectConversation(activeConversationId.value)
}

async function send() {
  const content = draft.value.trim()
  if (!content || sending.value) {
    if (!content) ElMessage.warning("请输入内容")
    return
  }

  sending.value = true
  error.value = ""
  streamingText.value = ""
  streamingThought.value = ""
  streamingSteps.value = []

  try {
    if (!activeConversationId.value) await createConversation()
    appendLocalUserMessage(content)
    draft.value = ""
    await scrollToBottom(false)
    await streamMessage(content)
    pendingAttachmentIds.value = []
    await loadConversations()
    await selectConversation(activeConversationId.value)
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      error.value = "已停止生成"
      if (activeConversationId.value) await selectConversation(activeConversationId.value)
    } else {
      error.value = getApiErrorMessage(err, "流式请求失败，请稍后重试。")
    }
  } finally {
    sending.value = false
    activeAbortController = null
    streamingText.value = ""
    streamingThought.value = ""
    streamingSteps.value = []
  }
}

function appendLocalUserMessage(content: string) {
  messages.value = [
    ...messages.value,
    {
      id: `local-${Date.now()}`,
      role: "user",
      content,
      mode: mode.value,
      provider: "",
      model: "",
      request_id: "",
      reasoning_summary: "",
      process_steps: [],
    },
  ]
}

function stopStreaming() {
  activeAbortController?.abort()
}

async function streamMessage(content: string) {
  activeAbortController = new AbortController()
  await streamConversationMessage(
    activeConversationId.value,
    {
      content,
      mode: mode.value,
      task_type: taskType.value,
      attachment_ids: pendingAttachmentIds.value,
    },
    {
      signal: activeAbortController.signal,
      onEvent: handleSseEvent,
    },
  )
}

function handleSseEvent(data: ChatStreamEvent) {
  if (data.type === "answer_delta" || data.type === "delta") streamingText.value += data.content || ""
  if (data.type === "reasoning_delta") streamingThought.value += data.content || ""
  if (data.type === "status" && data.content) streamingSteps.value.push(data.content)
  if (data.type === "evidence") {
    const count = data.data?.items?.length || 0
    streamingSteps.value.push(`知识库检索完成，命中 ${count} 条证据`)
  }
  if (data.type === "error") error.value = data.content || "模型服务不可用"

  if (data.type === "trace_start") {
    streamingThought.value = ""
    streamingSteps.value = []
  }
  if (data.type === "trace_delta") streamingThought.value += data.content || ""
  if (data.type === "trace_step" && data.content) streamingSteps.value.push(data.content)
  if (data.type === "trace") {
    streamingThought.value = data.reasoning_summary || ""
    streamingSteps.value = data.process_steps || []
  }
}

async function exportArtifact(artifact: Artifact) {
  await exportChatArtifact(artifact.id)
  ElMessage.success("已生成 Markdown 导出内容")
}

async function createDraft(artifact: Artifact) {
  const draftData = await createChatDraft(artifact.id)
  ElMessage.success(`已生成业务草稿：${draftData.title}`)
}

onMounted(async () => {
  await loadModelRoutes()
  await loadConversations()
  if (conversations.value[0]) await selectConversation(conversations.value[0].id)
})
</script>
