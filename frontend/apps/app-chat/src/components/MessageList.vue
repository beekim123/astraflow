<template>
  <div ref="messagesRef" class="messages">
    <section v-if="messages.length === 0 && !showStreamingMessage" class="empty-state">
      <span>Ask</span>
      <h2>从一个问题开始</h2>
      <p>可以直接聊天，也可以先上传图片、文件或视频，再让 AI 做分析、总结和草稿生成。</p>
    </section>

    <article v-for="message in messages" :key="message.id" class="message-row" :class="message.role">
      <div class="avatar">{{ roleAvatar(message.role) }}</div>
      <div class="message-card">
        <div class="message-meta">
          <span>{{ roleLabel(message.role) }}</span>
          <span v-if="message.mode || message.model">
            {{ message.mode }}{{ message.provider ? ` · ${message.provider}` : "" }}{{ message.model ? ` · ${message.model}` : "" }}
          </span>
        </div>
        <p class="message-content">{{ message.content }}</p>
        <details v-if="message.reasoning_summary || message.process_steps?.length" class="thought-card">
          <summary>查看思考过程</summary>
          <p v-if="message.reasoning_summary">{{ message.reasoning_summary }}</p>
          <ol v-if="message.process_steps?.length">
            <li v-for="step in message.process_steps" :key="step">{{ step }}</li>
          </ol>
        </details>
        <details v-if="message.request_id" class="debug-card">
          <summary>调用详情</summary>
          <code>{{ message.request_id }}</code>
        </details>
      </div>
    </article>

    <article v-if="showStreamingMessage" class="message-row assistant streaming">
      <div class="avatar">AI</div>
      <div class="message-card">
        <div class="message-meta">
          <span>AI 助手</span>
          <span>正在回复</span>
        </div>
        <details v-if="streamingThought || streamingSteps.length" class="thought-card streaming-thought" open>
          <summary>{{ streamingText ? "已完成思考" : "正在思考" }}</summary>
          <p v-if="streamingThought">{{ streamingThought }}</p>
          <ol v-if="streamingSteps.length">
            <li v-for="step in streamingSteps" :key="step">{{ step }}</li>
          </ol>
        </details>
        <p v-if="streamingText" class="message-content">{{ streamingText }}</p>
        <div v-else class="typing-indicator" aria-live="polite">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </article>

    <div class="message-bottom"></div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from "vue"
import type { Message } from "../types"

const props = defineProps<{
  messages: Message[]
  streamingText: string
  streamingThought: string
  streamingSteps: string[]
  showStreamingMessage: boolean
}>()

const messagesRef = ref<HTMLElement | null>(null)
let scrollFrame = 0

function roleAvatar(role: string) {
  return role === "user" ? "我" : "AI"
}

function roleLabel(role: string) {
  return role === "user" ? "你" : "AI 助手"
}

async function scrollToBottom(smooth = false) {
  await nextTick()
  if (scrollFrame) window.cancelAnimationFrame(scrollFrame)
  scrollFrame = window.requestAnimationFrame(() => {
    const messagesElement = messagesRef.value
    if (!messagesElement) {
      scrollFrame = 0
      return
    }
    messagesElement.scrollTo({
      top: messagesElement.scrollHeight,
      behavior: smooth ? "smooth" : "auto",
    })
    scrollFrame = 0
  })
}

watch(
  () => [props.messages.length, props.streamingText, props.streamingThought, props.streamingSteps.length, props.showStreamingMessage],
  () => {
    void scrollToBottom(false)
  },
)

defineExpose({ scrollToBottom })
</script>
