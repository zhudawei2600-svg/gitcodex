<template>
  <div class="detail-page">
    <NavBar />
    <div v-if="project" class="page-body container">
      <main class="detail-main">
        <div class="detail-header">
          <h1 class="detail-name">{{ project.name }}</h1>
          <div class="detail-badges">
            <span class="badge star-badge">
              <Icon icon="lucide:star" /> {{ formatStars(project.stars) }}
            </span>
            <span v-if="project.language" class="badge">{{ project.language }}</span>
            <span class="badge cat-badge">{{ project.subcategory || project.category }}</span>
          </div>
        </div>

        <p class="detail-summary">{{ project.summary }}</p>

        <div class="detail-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <div v-if="activeTab === 'overview'" class="tab-content">
          <div class="content-block">
            <p class="detail-desc">{{ project.description }}</p>
          </div>
        </div>

        <div v-if="activeTab === 'highlights'" class="tab-content">
          <div class="content-block">
            <ul class="highlight-list">
              <li v-for="h in project.highlights" :key="h" class="highlight-item">
                <Icon icon="lucide:sparkles" class="highlight-icon" />
                {{ h }}
              </li>
            </ul>
          </div>
        </div>

        <div v-if="activeTab === 'usecases'" class="tab-content">
          <div class="content-block">
            <div v-for="(uc, uci) in project.useCases" :key="uci" class="use-case">
              <span class="uc-who">{{ typeof uc === 'string' ? uc : uc.who }}</span>
              <span v-if="typeof uc !== 'string'" class="uc-what">{{ uc.what }}</span>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'compare'" class="tab-content">
          <div class="content-block">
            <div v-for="c in project.comparisons" :key="c.name" class="compare-row">
              <span class="compare-name">{{ c.name }}</span>
              <span class="compare-diff">{{ c.diff || c.difference }}</span>
            </div>
          </div>
        </div>
      </main>

      <aside class="detail-sidebar">
        <div class="sidebar-card glass-card">
          <h3 class="sidebar-card-title">快速链接</h3>
          <a :href="project.links.github" target="_blank" rel="noopener" class="quick-link">
            <Icon icon="lucide:github" /> GitHub 仓库
          </a>
          <a v-if="project.links.website" :href="project.links.website" target="_blank" rel="noopener" class="quick-link">
            <Icon icon="lucide:globe" /> 官方网站
          </a>
          <a v-if="project.links.chinese_docs" :href="project.links.chinese_docs" target="_blank" rel="noopener" class="quick-link">
            <Icon icon="lucide:book-open" /> 中文文档
          </a>
        </div>
      </aside>
    </div>
    <SiteFooter />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue"
import { Icon } from "@iconify/vue"

const route = useRoute()
const { getById } = useSearch()

const project = computed(() => {
  const id = (route.params.id as string[]).join("/")
  return getById(decodeURIComponent(id))
})

useHead({
  title: computed(() => project.value ? `${project.value.name} - 极光导航` : "极光导航"),
})

const activeTab = ref("overview")
const tabs = [
  { id: "overview", label: "概述" },
  { id: "highlights", label: "功能亮点" },
  { id: "usecases", label: "适用场景" },
  { id: "compare", label: "同类对比" },
]

function formatStars(n: number): string {
  if (n >= 100000) return `${(n / 1000).toFixed(0)}k`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}
</script>

<style scoped>
.detail-page { min-height: 100vh; }

.page-body {
  display: flex;
  gap: 32px;
  padding-top: 32px;
  padding-bottom: 48px;
}

.detail-main { flex: 1; min-width: 0; }

.detail-header {
  margin-bottom: 16px;
}

.detail-name {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 10px;
}

.detail-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.badge {
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 0.82rem;
  background: var(--bg-card);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.star-badge {
  color: var(--neon-purple);
  background: rgba(167, 139, 250, 0.1);
}

.cat-badge {
  color: var(--neon-cyan);
  background: rgba(103, 232, 249, 0.08);
}

.detail-summary {
  font-size: 1.1rem;
  color: var(--text-secondary);
  margin-bottom: 24px;
  line-height: 1.7;
}

.detail-tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 20px;
}

.tab-btn {
  padding: 10px 18px;
  border: none;
  background: none;
  color: var(--text-secondary);
  font-size: 0.9rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color var(--transition-base), border-color var(--transition-base);
}

.tab-btn:hover { color: var(--text-primary); }
.tab-btn.active {
  color: var(--neon-purple);
  border-bottom-color: var(--neon-purple);
}

.tab-content {
  animation: tab-in 200ms ease-out;
}

@keyframes tab-in {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.content-block {
  padding: 8px 0;
}

.detail-desc {
  line-height: 1.8;
  color: var(--text-primary);
}

.highlight-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.highlight-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  line-height: 1.6;
}

.highlight-icon {
  color: var(--neon-purple);
  margin-top: 3px;
  flex-shrink: 0;
}

.use-case {
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--bg-card);
  margin-bottom: 8px;
  display: flex;
  gap: 12px;
  align-items: baseline;
}

.uc-who {
  font-weight: 600;
  color: var(--neon-cyan);
  white-space: nowrap;
}

.uc-what { color: var(--text-secondary); font-size: 0.9rem; }

.compare-row {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--bg-card);
  margin-bottom: 8px;
  align-items: baseline;
}

.compare-name {
  font-weight: 600;
  white-space: nowrap;
  min-width: 80px;
}

.compare-diff { color: var(--text-secondary); font-size: 0.9rem; }

/* Sidebar */
.detail-sidebar { width: 260px; flex-shrink: 0; }

.sidebar-card {
  padding: 20px;
  position: sticky;
  top: 80px;
}

.sidebar-card-title {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.quick-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: background var(--transition-base);
  margin-bottom: 4px;
}

.quick-link:hover {
  background: var(--bg-card-hover);
  color: var(--neon-cyan);
}

@media (max-width: 768px) {
  .page-body { flex-direction: column; }
  .detail-sidebar { width: 100%; }
}
</style>
