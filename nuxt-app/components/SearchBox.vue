<template>
  <div class="search-wrapper">
    <div class="search-inner">
      <Icon icon="lucide:search" class="search-icon" />
      <input
        v-model="query"
        type="text"
        class="glass-input search-input"
        placeholder="搜索你感兴趣的项目..."
        @input="onInput"
        @keydown.escape="query = ''; results = []"
      />
    </div>
    <Transition name="dropdown">
      <div v-if="results.length" class="search-dropdown glass-card">
        <NuxtLink
          v-for="(item, i) in results"
          :key="item.id"
          :to="`/project/${item.id}`"
          class="search-result-item"
          :style="{ animationDelay: `${i * 30}ms` }"
          @click="clearSearch"
        >
          <span class="result-name">{{ item.name }}</span>
          <span class="result-tagline">{{ item.tagline }}</span>
          <span class="result-stars">★ {{ formatStars(item.stars) }}</span>
        </NuxtLink>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { Icon } from "@iconify/vue"

const { search } = useSearch()
const query = ref("")
const results = ref<ReturnType<typeof search>>([])

let timer: ReturnType<typeof setTimeout> | null = null

function onInput() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => {
    results.value = query.value ? search(query.value, 8) : []
  }, 150)
}

function clearSearch() {
  query.value = ""
  results.value = []
}

function formatStars(n: number): string {
  if (n >= 100000) return `${(n / 1000).toFixed(0)}k`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}
</script>

<style scoped>
.search-wrapper {
  position: relative;
  max-width: 640px;
  margin: 0 auto;
}

.search-inner {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.3rem;
  color: var(--text-secondary);
  pointer-events: none;
  z-index: 1;
}

.search-input {
  padding-left: 52px;
}

.search-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  padding: 8px;
  z-index: 50;
  overflow: hidden;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
  animation: slide-in 200ms ease-out both;
  transition: background var(--transition-base);
}

.search-result-item:hover {
  background: var(--bg-card-hover);
}

.result-name {
  font-weight: 600;
  white-space: nowrap;
}

.result-tagline {
  color: var(--text-secondary);
  font-size: 0.85rem;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-stars {
  color: var(--neon-purple);
  font-size: 0.85rem;
  white-space: nowrap;
}

/* Dropdown transition */
.dropdown-enter-active { animation: dropdown-in 150ms ease-out; }
.dropdown-leave-active { animation: dropdown-out 100ms ease-in; }

@keyframes dropdown-in {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes dropdown-out {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-8px); }
}

@keyframes slide-in {
  from { opacity: 0; transform: translateX(-8px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
