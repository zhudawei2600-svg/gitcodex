<template>
  <div class="category-page">
    <NavBar />
    <div class="page-body container">
      <aside class="sidebar glass-card">
        <h3 class="sidebar-title">分类</h3>
        <NuxtLink
          v-for="(cat, key) in categories"
          :key="key"
          :to="`/category/${encodeURIComponent(key)}`"
          class="sidebar-link"
          :class="{ active: key === currentCategory }"
        >
          <span>{{ key }}</span>
          <span class="sidebar-count">{{ cat.count }}</span>
        </NuxtLink>
      </aside>
      <main class="content">
        <div class="content-header">
          <h2 class="content-title">{{ currentCategory }}</h2>
          <select v-model="sortBy" class="sort-select">
            <option value="stars">按 Star 数</option>
            <option value="name">按名称</option>
          </select>
        </div>
        <div class="project-grid">
          <ProjectCard
            v-for="project in sortedProjects"
            :key="project.id"
            :project="project"
          />
        </div>
      </main>
    </div>
    <SiteFooter />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue"

const route = useRoute()
const { getCategories, projects } = useSearch()

const categories = getCategories()
const currentCategory = computed(() => decodeURIComponent(route.params.slug as string))
const sortBy = ref("stars")

useHead({
  title: computed(() => `${currentCategory.value} - 极光导航`),
})

const categoryProjects = computed(() =>
  projects.filter(p => p.category === currentCategory.value)
)

const sortedProjects = computed(() => {
  const list = [...categoryProjects.value]
  if (sortBy.value === "stars") {
    list.sort((a, b) => b.stars - a.stars)
  } else {
    list.sort((a, b) => a.name.localeCompare(b.name))
  }
  return list
})
</script>

<style scoped>
.category-page { min-height: 100vh; }

.page-body {
  display: flex;
  gap: 24px;
  padding-top: 24px;
  padding-bottom: 48px;
}

.sidebar {
  width: 200px;
  flex-shrink: 0;
  padding: 16px;
  align-self: flex-start;
  position: sticky;
  top: 80px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-title {
  font-size: 0.85rem;
  color: var(--text-secondary);
  padding: 8px 10px;
  margin-bottom: 4px;
}

.sidebar-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: background var(--transition-base);
}

.sidebar-link:hover,
.sidebar-link.active {
  background: var(--bg-card-hover);
}

.sidebar-link.active {
  color: var(--neon-purple);
}

.sidebar-count {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.content { flex: 1; min-width: 0; }

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-title {
  font-size: 1.4rem;
  font-weight: 700;
}

.sort-select {
  padding: 8px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.85rem;
  outline: none;
  cursor: pointer;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

@media (max-width: 768px) {
  .page-body { flex-direction: column; }
  .sidebar {
    width: 100%;
    position: static;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0;
  }
  .sidebar-title { display: none; }
  .sidebar-link { font-size: 0.8rem; padding: 6px 8px; }
  .sidebar-count { display: none; }
  .project-grid { grid-template-columns: 1fr; }
}
</style>
