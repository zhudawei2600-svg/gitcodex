<template>
  <div class="home-page">
    <NavBar />
    <section class="hero">
      <h1 class="hero-title neon-text">发现全球优秀开源产品</h1>
      <p class="hero-desc">用中文了解 GitHub 高星项目，每个人都能找到好工具</p>
      <SearchBox />
    </section>
    <FeaturedSlider />
    <CategoryGrid />
    <SiteFooter />
  </div>
</template>

<script setup lang="ts">
useHead({ title: "极光导航 - GitHub 高星产品中文导航" })
</script>

<style scoped>
.home-page {
  min-height: 100vh;
}

.hero {
  text-align: center;
  padding: 80px 24px 48px;
}

.hero-title {
  font-size: 2.6rem;
  font-weight: 800;
  margin-bottom: 12px;
  letter-spacing: 1px;
}

.hero-desc {
  color: var(--text-secondary);
  font-size: 1.1rem;
  margin-bottom: 36px;
}

@media (max-width: 768px) {
  .hero { padding: 48px 16px 32px; }
  .hero-title { font-size: 1.8rem; }
  .hero-desc { font-size: 1rem; }
}
</style>
