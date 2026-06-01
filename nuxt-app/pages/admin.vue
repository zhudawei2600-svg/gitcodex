<template>
  <div class="admin-page">
    <div v-if="!authed" class="auth-gate">
      <div class="auth-card glass-card">
        <Icon icon="lucide:lock" class="auth-icon" />
        <h2>管理面板</h2>
        <p>请输入管理密码</p>
        <input
          v-model="password"
          type="password"
          class="glass-input auth-input"
          placeholder="输入密码..."
          @keydown.enter="checkPassword"
        />
        <button class="auth-btn" @click="checkPassword">进入</button>
        <p v-if="error" class="auth-error">{{ error }}</p>
      </div>
    </div>
    <template v-else>
    <NavBar />
    <div class="page-body container">
      <h1 class="page-title">管理面板</h1>
      <p class="page-desc">极光导航数据管理中心</p>

      <div class="stats-grid">
        <div class="stat-card glass-card">
          <Icon icon="lucide:package" class="stat-icon" />
          <div class="stat-value">{{ projects.length }}</div>
          <div class="stat-label">收录项目</div>
        </div>
        <div class="stat-card glass-card">
          <Icon icon="lucide:folder-tree" class="stat-icon" />
          <div class="stat-value">{{ Object.keys(categories).length }}</div>
          <div class="stat-label">分类</div>
        </div>
        <div class="stat-card glass-card">
          <Icon icon="lucide:calendar" class="stat-icon" />
          <div class="stat-value">{{ updateDate }}</div>
          <div class="stat-label">最后更新</div>
        </div>
      </div>

      <div class="category-breakdown glass-card">
        <h2>分类统计</h2>
        <div class="cat-list">
          <div v-for="(cat, name) in categories" :key="name" class="cat-row">
            <span class="cat-name">{{ name }}</span>
            <div class="cat-bar-wrap">
              <div class="cat-bar" :style="{ width: (cat.count / maxCount * 100) + '%' }"></div>
            </div>
            <span class="cat-num">{{ cat.count }}</span>
          </div>
        </div>
      </div>

      <div class="actions glass-card">
        <h2>更新管理</h2>
        <p class="actions-desc">数据更新通过 VSCode 中的 Claude Code 助手完成。打开项目目录后告诉助手 "更新极光导航数据" 即可执行全流程。</p>
        <div class="action-btns">
          <div class="action-item">
            <Icon icon="lucide:terminal" class="action-icon" />
            <div>
              <strong>本地更新</strong>
              <p>双击项目目录下的 update.bat</p>
            </div>
          </div>
          <div class="action-item">
            <Icon icon="lucide:bot" class="action-icon" />
            <div>
              <strong>AI 助手更新</strong>
              <p>在 VSCode 中打开 D:\gitcodex，告诉 Claude 更新数据</p>
            </div>
          </div>
          <div class="action-item">
            <Icon icon="lucide:refresh-cw" class="action-icon" />
            <div>
              <strong>自动同步</strong>
              <p>GitHub 高星仓库发生重大变化时手动触发</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <SiteFooter />
    </template>
  </div>
</template>

<script setup lang="ts">
import { Icon } from "@iconify/vue"
import { computed, ref } from "vue"

const { projects, getCategories } = useSearch()
const categories = getCategories()

const maxCount = computed(() =>
  Math.max(...Object.values(categories).map(c => c.count), 1)
)

const updateDate = computed(() => {
  const dates = projects.map(p => p.updated_at).sort().reverse()
  return dates.length ? dates[0].slice(0, 10) : "暂无"
})


const password = ref("")
const authed = ref(false)
const error = ref("")

function checkPassword() {
  // Simple hash check: password is "gitcodex2026"
  if (password.value === "gitcodex2026") {
    authed.value = true
    error.value = ""
  } else {
    error.value = "密码错误"
    password.value = ""
  }
}

useHead({ title: "管理面板 - 极光导航" })
</script>

<style scoped>

.auth-gate {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 380px;
  padding: 40px 32px;
  text-align: center;
}

.auth-icon {
  font-size: 2.5rem;
  color: var(--neon-purple);
  margin-bottom: 12px;
}

.auth-card h2 {
  font-size: 1.3rem;
  margin-bottom: 6px;
}

.auth-card p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 20px;
}

.auth-input {
  margin-bottom: 12px;
  text-align: center;
}

.auth-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--neon-purple), var(--neon-cyan));
  color: #fff;
  font-size: 0.95rem;
  cursor: pointer;
  transition: opacity 200ms;
}

.auth-btn:hover { opacity: 0.85; }

.auth-error {
  color: #f87171;
  font-size: 0.85rem;
  margin-top: 8px;
}

.admin-page { min-height: 100vh; }

.page-body { padding-top: 40px; padding-bottom: 60px; }

.page-title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 4px;
}

.page-desc {
  color: var(--text-secondary);
  margin-bottom: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  padding: 24px;
  text-align: center;
}

.stat-icon {
  font-size: 1.8rem;
  color: var(--neon-cyan);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 1.6rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.category-breakdown,
.actions {
  padding: 24px;
  margin-bottom: 24px;
}

.category-breakdown h2,
.actions h2 {
  font-size: 1.1rem;
  margin-bottom: 16px;
}

.cat-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cat-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cat-name {
  width: 120px;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.cat-bar-wrap {
  flex: 1;
  height: 8px;
  background: var(--bg-card);
  border-radius: 4px;
  overflow: hidden;
}

.cat-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan));
  border-radius: 4px;
  transition: width 500ms ease-out;
}

.cat-num {
  width: 40px;
  text-align: right;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.actions-desc {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 20px;
  line-height: 1.6;
}

.action-btns {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  border-radius: 10px;
  background: var(--bg-card);
}

.action-icon {
  font-size: 1.3rem;
  color: var(--neon-purple);
  margin-top: 2px;
  flex-shrink: 0;
}

.action-item strong {
  font-size: 0.95rem;
}

.action-item p {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-top: 2px;
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
}
</style>
