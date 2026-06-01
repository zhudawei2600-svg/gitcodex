<template>
  <footer class="site-footer">
    <div class="footer-inner container">
      <p class="footer-text">
        数据来源
        <a href="https://github.com" target="_blank" rel="noopener" class="footer-link">GitHub</a>
        · 中文内容由 AI 生成，仅供参考
      </p>
      <p class="footer-date">更新于 {{ updateDate }}</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import projectsData from "~/data/projects.json"

const dates = (projectsData as { updated_at: string }[]).map(p => p.updated_at).sort().reverse()
const updateDate = dates.length ? dates[0].slice(0, 10) : "2025-01-01"
</script>

<style scoped>
.site-footer {
  margin-top: 80px;
  padding: 32px 0;
  border-top: 1px solid var(--border-subtle);
}

.footer-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.footer-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.footer-link {
  color: var(--neon-cyan);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.footer-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
  opacity: 0.7;
}
</style>
