<template>
  <details v-if="artifacts.length || mediaTasks.length" class="artifact-drawer">
    <summary>
      <span>产物与媒体任务</span>
      <small>{{ artifacts.length }} 个产物 · {{ mediaTasks.length }} 个任务</small>
    </summary>
    <div class="artifact-grid">
      <article v-for="artifact in artifacts" :key="artifact.id" class="artifact-card">
        <span>{{ artifact.artifact_type }}</span>
        <h3>{{ artifact.title }}</h3>
        <p>{{ artifact.content_markdown }}</p>
        <div>
          <button @click="$emit('exportArtifact', artifact)">导出 Markdown</button>
          <button @click="$emit('createDraft', artifact)">转业务草稿</button>
        </div>
      </article>
      <article v-for="task in mediaTasks" :key="task.id" class="task-card">
        <span>{{ task.task_type }}</span>
        <strong>{{ task.status }} · {{ task.progress }}%</strong>
      </article>
    </div>
  </details>
</template>

<script setup lang="ts">
import type { Artifact, MediaTask } from "../types"

defineProps<{
  artifacts: Artifact[]
  mediaTasks: MediaTask[]
}>()

defineEmits<{
  exportArtifact: [artifact: Artifact]
  createDraft: [artifact: Artifact]
}>()
</script>
