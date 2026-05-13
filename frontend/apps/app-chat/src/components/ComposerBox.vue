<template>
  <div v-if="attachments.length" class="attachment-list">
    <span v-for="file in attachments" :key="file.id">{{ file.filename }} · {{ Math.ceil(file.size_bytes / 1024) }}KB</span>
  </div>

  <footer class="composer">
    <div class="composer-inner">
      <textarea
        :value="draft"
        placeholder="给 AstraFlow 发送消息"
        rows="1"
        @input="$emit('update:draft', ($event.target as HTMLTextAreaElement).value)"
        @keydown.enter.exact.prevent="$emit('send')"
        @keydown.meta.enter.prevent="$emit('send')"
      />
      <div class="composer-actions">
        <label class="attach-button">
          上传
          <input type="file" multiple @change="$emit('upload', $event)" />
        </label>
        <button class="send-button" :disabled="!sending && !draft.trim()" @click="sending ? $emit('stop') : $emit('send')">
          {{ sending ? "停止" : "发送" }}
        </button>
      </div>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </footer>
</template>

<script setup lang="ts">
import type { Attachment } from "../types"

defineProps<{
  draft: string
  sending: boolean
  error: string
  attachments: Attachment[]
}>()

defineEmits<{
  "update:draft": [value: string]
  send: []
  stop: []
  upload: [event: Event]
}>()
</script>
