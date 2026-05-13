<template>
  <div v-if="open" class="drawer-backdrop" @click="$emit('close')"></div>

  <aside class="conversation-panel">
    <div class="brand-block">
      <span>AI</span>
      <div>
        <strong>AstraFlow Chat</strong>
        <small>Phase 2 AI Gateway</small>
      </div>
    </div>

    <button class="new-chat" @click="$emit('create')">新建聊天</button>

    <nav class="conversation-list" aria-label="会话列表">
      <button
        v-for="item in conversations"
        :key="item.id"
        class="conversation-item"
        :class="{ active: item.id === activeConversationId }"
        @click="$emit('select', item.id)"
      >
        <strong>{{ item.title }}</strong>
        <span>{{ item.mode }} · {{ item.updated_at }}</span>
      </button>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import type { Conversation } from "../types"

defineProps<{
  conversations: Conversation[]
  activeConversationId: string
  open: boolean
}>()

defineEmits<{
  close: []
  create: []
  select: [id: string]
}>()
</script>
