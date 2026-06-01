<template>
  <section class="featured-section">
    <div class="section-header container">
      <h2 class="section-title">精选推荐</h2>
      <span class="section-sub">全球最受欢迎的开源项目</span>
    </div>
    <div class="slider container">
      <div class="slider-track">
        <ProjectCard
          v-for="project in featured"
          :key="project.id"
          :project="project"
          class="slider-card"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { getFeatured } = useSearch()
const featured = getFeatured(8)
</script>

<style scoped>
.featured-section {
  padding: 48px 0;
}

.section-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 700;
}

.section-sub {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.slider {
  overflow-x: auto;
  padding-bottom: 8px;
}

.slider-track {
  display: flex;
  gap: 16px;
  scroll-snap-type: x mandatory;
}

.slider-card {
  min-width: 280px;
  max-width: 320px;
  flex-shrink: 0;
  scroll-snap-align: start;
}
</style>
