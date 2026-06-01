<template>
  <nav class="navbar glass-card" :class="{ scrolled }">
    <div class="navbar-inner container">
      <NuxtLink to="/" class="logo">
        <span class="logo-icon">◇</span>
        <span class="logo-text neon-text">极光导航</span>
      </NuxtLink>
      <div class="nav-links">
        <NuxtLink
          v-for="cat in topCategories"
          :key="cat.name"
          :to="`/category/${encodeURIComponent(cat.name)}`"
          class="nav-link"
        >
          {{ cat.name }}
        </NuxtLink>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"

const scrolled = ref(false)

function onScroll() {
  scrolled.value = window.scrollY > 20
}

onMounted(() => window.addEventListener("scroll", onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener("scroll", onScroll))

const topCategories = [
  { name: "开发工具" },
  { name: "AI & 机器学习" },
  { name: "效率工具" },
  { name: "设计创意" },
  { name: "学习资源" },
  { name: "安全隐私" },
]
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  border-top: none;
  border-left: none;
  border-right: none;
  border-radius: 0;
  transition: background var(--transition-base), border-color var(--transition-base);
}

.navbar:not(.scrolled) {
  background: transparent;
  border-color: transparent;
}

.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.2rem;
  font-weight: 700;
}

.logo-icon {
  font-size: 1.4rem;
  color: var(--neon-purple);
}

.logo-text {
  letter-spacing: 0.5px;
}

.nav-links {
  display: flex;
  gap: 4px;
}

.nav-link {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  transition: color var(--transition-base), background var(--transition-base);
}

.nav-link:hover,
.nav-link.router-link-exact-active {
  color: var(--text-primary);
  background: var(--bg-card);
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
}
</style>
