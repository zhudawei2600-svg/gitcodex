<template>
  <NuxtLink :to="`/project/${project.id}`" class="project-card glass-card">
    <div class="card-header">
      <h3 class="card-name">{{ project.name }}</h3>
      <span class="card-stars">
        <Icon icon="lucide:star" class="star-icon" />
        {{ formatStars(project.stars) }}
      </span>
    </div>
    <p class="card-tagline">{{ project.tagline }}</p>
    <div class="card-meta">
      <span v-if="project.language" class="meta-badge">{{ project.language }}</span>
      <span class="meta-badge category-badge">{{ project.subcategory || project.category }}</span>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
import { Icon } from "@iconify/vue"
import type { Project } from "~/composables/useSearch"

defineProps<{ project: Project }>()

function formatStars(n: number): string {
  if (n >= 100000) return `${(n / 1000).toFixed(0)}k`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}
</script>

<style scoped>
.project-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px;
  cursor: pointer;
}

.card-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}

.card-name {
  font-size: 1.05rem;
  font-weight: 600;
}

.card-stars {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  color: var(--neon-purple);
  white-space: nowrap;
}

.star-icon {
  font-size: 0.9rem;
}

.card-tagline {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  gap: 6px;
  margin-top: auto;
}

.meta-badge {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.06);
}

.category-badge {
  color: var(--neon-cyan);
  background: rgba(103, 232, 249, 0.08);
}
</style>
