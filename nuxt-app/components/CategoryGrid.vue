<template>
  <section class="category-section">
    <div class="section-header container">
      <h2 class="section-title">按分类浏览</h2>
    </div>
    <div class="category-grid container">
      <NuxtLink
        v-for="(cat, key) in categories"
        :key="key"
        :to="`/category/${encodeURIComponent(key)}`"
        class="category-card glass-card"
      >
        <Icon :icon="iconMap[key] || 'lucide:package'" class="cat-icon" />
        <div class="cat-info">
          <span class="cat-name">{{ key }}</span>
          <span class="cat-count">{{ cat.count }} 个项目</span>
        </div>
        <div class="cat-glow"></div>
      </NuxtLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Icon } from "@iconify/vue"

const { getCategories } = useSearch()
const categories = getCategories()

const iconMap: Record<string, string> = {
  "开发工具": "lucide:code-2",
  "AI & 机器学习": "lucide:brain",
  "效率工具": "lucide:zap",
  "设计创意": "lucide:palette",
  "学习资源": "lucide:book-open",
  "安全隐私": "lucide:shield",
  "其他": "lucide:package",
}
</script>

<style scoped>
.category-section {
  padding: 48px 0;
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 700;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.category-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  overflow: hidden;
}

.category-card:hover .cat-glow {
  opacity: 1;
}

.cat-icon {
  font-size: 1.8rem;
  color: var(--neon-cyan);
  flex-shrink: 0;
}

.cat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cat-name {
  font-weight: 600;
  font-size: 1rem;
}

.cat-count {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.cat-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at 50% 50%,
    rgba(167, 139, 250, 0.08),
    transparent 60%
  );
  opacity: 0;
  transition: opacity var(--transition-slow);
  pointer-events: none;
}

@media (max-width: 768px) {
  .category-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
