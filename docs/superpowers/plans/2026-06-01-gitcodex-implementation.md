# GitCodex（极光导航）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Chinese-friendly GitHub high-star project navigation site with AI-generated descriptions, frosted-glass neon UI, deployed to Cloudflare Pages.

**Architecture:** Python scripts fetch GitHub API data and call DeepSeek API to generate Chinese content, outputting JSON. Nuxt 3 SSG reads JSON at build time and generates static HTML. Site has home, category, and detail pages with client-side fuzzy search.

**Tech Stack:** Python 3 (urllib + json for scripts), DeepSeek API (OpenAI-compatible for content gen), Nuxt 3 (SSG mode), Vue 3 + TypeScript, custom CSS (frosted glass + neon), Fuse.js (client search), Cloudflare Pages (hosting)

---

### Task 1: Project scaffolding

**Files:**
- Create: `D:\gitcodex\.gitignore`
- Create: `D:\gitcodex\.env.example`
- Create: `D:\gitcodex\scripts\requirements.txt`

- [ ] **Step 1: Initialize git repository**

```bash
cd /d/gitcodex && git init
```

- [ ] **Step 2: Create .gitignore**

```gitignore
# Python
__pycache__/
*.pyc
.env

# Nuxt
nuxt-app/.output/
nuxt-app/.nuxt/
nuxt-app/node_modules/
nuxt-app/dist/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 3: Create .env.example**

```env
GITHUB_TOKEN=github_pat_xxxx
DEEPSEEK_API_KEY=sk-xxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

- [ ] **Step 4: Create scripts/requirements.txt**

```
requests
python-dotenv
```

- [ ] **Step 5: Commit**

```bash
cd /d/gitcodex && git add .gitignore .env.example scripts/requirements.txt && git commit -m "chore: project scaffolding"
```

---

### Task 2: GitHub data fetch script

**Files:**
- Create: `D:\gitcodex\scripts\fetch_github.py`

- [ ] **Step 1: Create fetch_github.py**

```python
"""Fetch high-star repos from GitHub Search API."""
import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "gitcodex",
}
PER_PAGE = 100
MAX_RESULTS = 500  # GitHub Search API caps at 1000 results


def search_repos(page: int) -> dict:
    url = (
        f"https://api.github.com/search/repositories"
        f"?q=stars:>1000&sort=stars&order=desc"
        f"&per_page={PER_PAGE}&page={page}"
    )
    req = Request(url, headers=HEADERS)
    with urlopen(req) as resp:
        return json.loads(resp.read())


def fetch_readme(owner: str, repo: str) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    req = Request(url, headers={**HEADERS, "Accept": "application/vnd.github.raw+json"})
    try:
        with urlopen(req) as resp:
            return resp.read().decode("utf-8", errors="replace")[:4000]
    except HTTPError as e:
        if e.code == 404:
            return ""
        raise


def main():
    output_dir = Path(__file__).parent.parent / "nuxt-app" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_repos = []
    for page in range(1, (MAX_RESULTS // PER_PAGE) + 2):
        print(f"Fetching page {page}...")
        try:
            data = search_repos(page)
        except HTTPError as e:
            print(f"  Error: {e}")
            if e.code == 422:
                break
            time.sleep(10)
            continue

        items = data.get("items", [])
        if not items:
            break

        for item in items:
            print(f"  {item['full_name']}")
            readme = fetch_readme(item["owner"]["login"], item["name"])
            time.sleep(0.3)  # rate limit safety

            all_repos.append({
                "id": item["full_name"],
                "name": item["name"],
                "owner": item["owner"]["login"],
                "stars": item["stargazers_count"],
                "language": item.get("language") or "",
                "topics": item.get("topics", []),
                "description_original": item.get("description") or "",
                "homepage": item.get("homepage") or "",
                "github_url": item["html_url"],
                "readme": readme,
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
            })

        if len(all_repos) >= MAX_RESULTS:
            break
        time.sleep(2)

    raw_path = output_dir / "raw_repos.json"
    raw_path.write_text(json.dumps(all_repos, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(all_repos)} repos to {raw_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the fetch script**

```bash
cd /d/gitcodex/scripts && cp ../.env.example .env
# Edit .env with real GITHUB_TOKEN, then:
python fetch_github.py
```

Expected: Creates `nuxt-app/data/raw_repos.json` with up to 500 repos.

- [ ] **Step 3: Commit**

```bash
cd /d/gitcodex && git add scripts/fetch_github.py && git commit -m "feat: add GitHub fetch script"
```

---

### Task 3: AI content generation script

**Files:**
- Create: `D:\gitcodex\scripts\generate_ai.py`

- [ ] **Step 1: Create generate_ai.py**

```python
"""Generate Chinese content for repos using DeepSeek (OpenAI-compatible) API."""
import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["DEEPSEEK_API_KEY"]
BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

SYSTEM_PROMPT = """你是一个技术产品分析师，专门向中国普通用户介绍 GitHub 开源项目。
要求：
1. 用通俗易懂的中文，让非技术用户也能理解这个项目是什么
2. tagline 控制在20字以内，是项目的核心价值一句话
3. summary 控制在100字以内，像给朋友推荐一样介绍
4. description 在200-400字，讲清楚项目功能、特点、为什么受欢迎
5. highlights 列出3-5个核心亮点
6. useCases 列出2-3个典型使用场景和适合的用户群
7. comparisons 列出2-3个同类项目并说明区别
8. category 从["开发工具","AI & 机器学习","效率工具","设计创意","学习资源","安全隐私","其他"]中选择
9. subcategory 自行判断，如"前端框架"、"代码编辑器"、"大语言模型"等

只输出JSON，不要markdown代码块标记。"""

USER_PROMPT_TEMPLATE = """请分析以下 GitHub 开源项目：

项目名：{name}
GitHub 描述：{description}
编程语言：{language}
Star 数：{stars}
话题标签：{topics}
README 开头：{readme}

请输出 JSON："""


def call_deepseek(prompt: str) -> dict:
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")

    req = Request(
        f"{BASE_URL}/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )
    with urlopen(req) as resp:
        result = json.loads(resp.read())
    content = result["choices"][0]["message"]["content"]
    return json.loads(content)


def main():
    raw_path = Path(__file__).parent.parent / "nuxt-app" / "data" / "raw_repos.json"
    if not raw_path.exists():
        print("raw_repos.json not found. Run fetch_github.py first.")
        return

    repos = json.loads(raw_path.read_text(encoding="utf-8"))

    output_path = Path(__file__).parent.parent / "nuxt-app" / "data" / "projects.json"

    # Resume from existing output if any
    if output_path.exists():
        existing = {r["id"]: r for r in json.loads(output_path.read_text(encoding="utf-8"))}
    else:
        existing = {}

    results = []
    for i, repo in enumerate(repos):
        rid = repo["id"]
        print(f"[{i+1}/{len(repos)}] {rid}")

        if rid in existing and "summary" in existing[rid]:
            print("  (cached)")
            results.append(existing[rid])
            continue

        try:
            prompt = USER_PROMPT_TEMPLATE.format(
                name=repo["name"],
                description=repo["description_original"],
                language=repo["language"],
                stars=repo["stars"],
                topics=", ".join(repo["topics"][:10]),
                readme=repo["readme"][:2000],
            )
            ai_data = call_deepseek(prompt)
            time.sleep(1)  # rate limit
        except Exception as e:
            print(f"  Error: {e}")
            ai_data = {
                "tagline": repo["description_original"],
                "summary": repo["description_original"],
                "description": repo["description_original"],
                "highlights": [],
                "useCases": [],
                "comparisons": [],
                "category": "其他",
                "subcategory": "",
            }

        enriched = {
            "id": rid,
            "name": repo["name"],
            "owner": repo["owner"],
            "stars": repo["stars"],
            "language": repo["language"],
            "topics": repo["topics"],
            "tagline": ai_data.get("tagline", ""),
            "summary": ai_data.get("summary", ""),
            "description": ai_data.get("description", ""),
            "highlights": ai_data.get("highlights", []),
            "useCases": ai_data.get("useCases", []),
            "comparisons": ai_data.get("comparisons", []),
            "category": ai_data.get("category", "其他"),
            "subcategory": ai_data.get("subcategory", ""),
            "links": {
                "github": repo["github_url"],
                "website": repo["homepage"],
                "chinese_docs": "",
            },
            "updated_at": repo["updated_at"],
        }
        results.append(enriched)

        # Save incrementally
        output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nSaved {len(results)} enriched repos to {output_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run AI generation (limit first for testing)**

```bash
# First test with just 5 repos by editing the script temporarily
# Set a small slice: for repo in repos[:5]
cd /d/gitcodex/scripts && python generate_ai.py
```

Expected: Creates `nuxt-app/data/projects.json` with AI-generated Chinese content.

- [ ] **Step 3: Generate categories.json**

```bash
cd /d/gitcodex && python -c "
import json
from pathlib import Path
from collections import defaultdict

projects = json.loads(Path('nuxt-app/data/projects.json').read_text(encoding='utf-8'))
cats = defaultdict(lambda: {'name': '', 'subcategories': defaultdict(int), 'count': 0, 'icon': ''})

ICON_MAP = {
    '开发工具': 'code',
    'AI & 机器学习': 'brain',
    '效率工具': 'zap',
    '设计创意': 'palette',
    '学习资源': 'book-open',
    '安全隐私': 'shield',
    '其他': 'package',
}

for p in projects:
    cat = p['category']
    cats[cat]['name'] = cat
    cats[cat]['count'] += 1
    cats[cat]['icon'] = ICON_MAP.get(cat, 'package')
    if p['subcategory']:
        cats[cat]['subcategories'][p['subcategory']] += 1

result = []
for name, data in sorted(cats.items()):
    data['subcategories'] = dict(sorted(data['subcategories'].items(), key=lambda x: -x[1]))
    result.append(data)

Path('nuxt-app/data/categories.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Generated {len(result)} categories')
"
```

- [ ] **Step 4: Commit**

```bash
cd /d/gitcodex && git add scripts/generate_ai.py && git commit -m "feat: add AI content generation script"
```

---

### Task 4: Nuxt 3 project setup

**Files:**
- Create: `D:\gitcodex\nuxt-app\package.json`
- Create: `D:\gitcodex\nuxt-app\tsconfig.json`
- Create: `D:\gitcodex\nuxt-app\nuxt.config.ts`
- Create: `D:\gitcodex\nuxt-app\app.vue`
- Create: `D:\gitcodex\nuxt-app\composables\useSearch.ts`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "gitcodex",
  "private": true,
  "scripts": {
    "dev": "nuxi dev",
    "build": "nuxi build",
    "generate": "nuxi generate"
  },
  "devDependencies": {
    "nuxt": "^3.12.0",
    "@nuxtjs/tailwindcss": "^6.12.0",
    "typescript": "^5.4.0"
  },
  "dependencies": {
    "@iconify/vue": "^4.1.0",
    "fuse.js": "^7.0.0"
  }
}
```

- [ ] **Step 2: Create tsconfig.json**

```json
{
  "extends": "./.nuxt/tsconfig.json"
}
```

- [ ] **Step 3: Create nuxt.config.ts**

```ts
import { readFileSync } from "fs"
import { resolve } from "path"

function getProjectRoutes(): string[] {
  try {
    const dataPath = resolve(__dirname, "data/projects.json")
    const projects = JSON.parse(readFileSync(dataPath, "utf-8"))
    return projects.map((p: { id: string }) => `/project/${p.id}`)
  } catch {
    return []
  }
}

function getCategoryRoutes(): string[] {
  try {
    const dataPath = resolve(__dirname, "data/categories.json")
    const cats = JSON.parse(readFileSync(dataPath, "utf-8"))
    return cats.map((c: { name: string }) => `/category/${encodeURIComponent(c.name)}`)
  } catch {
    return []
  }
}

export default defineNuxtConfig({
  ssr: true,
  app: {
    head: {
      title: "极光导航 - GitHub 高星产品中文导航",
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        { name: "description", content: "发现全球优秀的开源产品，用中文了解 GitHub 高星项目" },
      ],
    },
  },
  nitro: {
    prerender: {
      routes: ["/", ...getProjectRoutes(), ...getCategoryRoutes()],
    },
  },
  css: ["~/assets/css/main.css"],
})
```

- [ ] **Step 4: Create minimal app.vue**

```vue
<template>
  <NuxtPage />
</template>
```

- [ ] **Step 5: Create composables/useSearch.ts**

```ts
import Fuse from "fuse.js"
import projectsData from "~/data/projects.json"

export interface Project {
  id: string
  name: string
  tagline: string
  stars: number
  category: string
  subcategory: string
  language: string
  topics: string[]
  summary: string
  description: string
  highlights: string[]
  useCases: { who: string; what: string }[]
  comparisons: { name: string; diff: string }[]
  links: { github: string; website: string; chinese_docs: string }
  updated_at: string
}

const projects = projectsData as unknown as Project[]

const fuse = new Fuse(projects, {
  keys: [
    { name: "name", weight: 0.4 },
    { name: "tagline", weight: 0.3 },
    { name: "summary", weight: 0.2 },
    { name: "topics", weight: 0.1 },
  ],
  threshold: 0.4,
})

export function useSearch() {
  function search(query: string, limit = 10): Project[] {
    if (!query.trim()) return []
    return fuse.search(query.trim()).slice(0, limit).map(r => r.item)
  }

  function getByCategory(cat: string): Project[] {
    return projects.filter(p => p.category === cat)
  }

  function getById(id: string): Project | undefined {
    return projects.find(p => p.id === id)
  }

  function getFeatured(limit = 8): Project[] {
    return projects.slice(0, limit)
  }

  function getCategories() {
    return projects.reduce<Record<string, { name: string; count: number; subcategories: Record<string, number> }>>((acc, p) => {
      if (!acc[p.category]) {
        acc[p.category] = { name: p.category, count: 0, subcategories: {} }
      }
      acc[p.category].count++
      if (p.subcategory) {
        acc[p.category].subcategories[p.subcategory] = (acc[p.category].subcategories[p.subcategory] || 0) + 1
      }
      return acc
    }, {})
  }

  return { search, getByCategory, getById, getFeatured, getCategories, projects }
}
```

- [ ] **Step 6: Install dependencies**

```bash
cd /d/gitcodex/nuxt-app && npm install
```

- [ ] **Step 7: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/package.json nuxt-app/tsconfig.json nuxt-app/nuxt.config.ts nuxt-app/app.vue nuxt-app/composables/ && git commit -m "feat: scaffold Nuxt 3 project"
```

---

### Task 5: Global CSS theme

**Files:**
- Create: `D:\gitcodex\nuxt-app\assets\css\main.css`

- [ ] **Step 1: Create main.css**

```css
/* ===== CSS Variables ===== */
:root {
  --bg-deep: #0d1117;
  --bg-card: rgba(255, 255, 255, 0.04);
  --bg-card-hover: rgba(255, 255, 255, 0.07);
  --border-subtle: rgba(255, 255, 255, 0.06);
  --border-glow: rgba(167, 139, 250, 0.4);
  --neon-purple: #a78bfa;
  --neon-cyan: #67e8f9;
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --radius: 12px;
  --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* ===== Reset & Base ===== */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial,
    sans-serif;
  background: var(--bg-deep);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
  overflow-x: hidden;
}

a {
  color: inherit;
  text-decoration: none;
}

/* ===== Glass card base ===== */
.glass-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius);
  transition: transform var(--transition-slow), box-shadow var(--transition-slow),
    border-color var(--transition-slow);
}

.glass-card:hover {
  transform: translateY(-4px);
  border-color: var(--border-glow);
  box-shadow: 0 8px 32px rgba(167, 139, 250, 0.12),
              0 0 0 1px rgba(167, 139, 250, 0.15);
}

/* ===== Neon text glow ===== */
.neon-text {
  background: linear-gradient(135deg, var(--neon-purple), var(--neon-cyan));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ===== Page transition ===== */
.page-enter-active {
  animation: page-in var(--transition-base);
}

.page-leave-active {
  animation: page-out var(--transition-base);
}

@keyframes page-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes page-out {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-8px); }
}

/* ===== Search input glow ===== */
.glass-input {
  width: 100%;
  padding: 16px 24px;
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  color: var(--text-primary);
  font-size: 1.1rem;
  outline: none;
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
}

.glass-input::placeholder {
  color: var(--text-secondary);
}

.glass-input:focus {
  border-color: var(--neon-purple);
  box-shadow: 0 0 24px rgba(167, 139, 250, 0.2),
              0 0 0 1px rgba(167, 139, 250, 0.3);
}

/* ===== Scrollbar ===== */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* ===== Container ===== */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .container {
    padding: 0 16px;
  }
  .glass-input {
    padding: 12px 16px;
    font-size: 1rem;
  }
}
```

- [ ] **Step 2: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/assets/ && git commit -m "feat: add global CSS theme with glass + neon styles"
```

---

### Task 6: NavBar component

**Files:**
- Create: `D:\gitcodex\nuxt-app\components\NavBar.vue`

- [ ] **Step 1: Create NavBar.vue**

```vue
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
```

- [ ] **Step 2: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/components/NavBar.vue && git commit -m "feat: add NavBar component"
```

---

### Task 7: SearchBox component

**Files:**
- Create: `D:\gitcodex\nuxt-app\components\SearchBox.vue`

- [ ] **Step 1: Create SearchBox.vue**

```vue
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
```

- [ ] **Step 2: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/components/SearchBox.vue && git commit -m "feat: add SearchBox component with fuzzy search"
```

---

### Task 8: ProjectCard component

**Files:**
- Create: `D:\gitcodex\nuxt-app\components\ProjectCard.vue`

- [ ] **Step 1: Create ProjectCard.vue**

```vue
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
```

- [ ] **Step 2: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/components/ProjectCard.vue && git commit -m "feat: add ProjectCard component"
```

---

### Task 9: FeaturedSlider component

**Files:**
- Create: `D:\gitcodex\nuxt-app\components\FeaturedSlider.vue`

- [ ] **Step 1: Create FeaturedSlider.vue**

```vue
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
```

- [ ] **Step 2: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/components/FeaturedSlider.vue && git commit -m "feat: add FeaturedSlider component"
```

---

### Task 10: CategoryGrid component

**Files:**
- Create: `D:\gitcodex\nuxt-app\components\CategoryGrid.vue`

- [ ] **Step 1: Create CategoryGrid.vue**

```vue
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
```

- [ ] **Step 2: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/components/CategoryGrid.vue && git commit -m "feat: add CategoryGrid component"
```

---

### Task 11: Footer component

**Files:**
- Create: `D:\gitcodex\nuxt-app\components\SiteFooter.vue`

- [ ] **Step 1: Create SiteFooter.vue**

```vue
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

// Use the most recent project update as site update date
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
```

- [ ] **Step 2: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/components/SiteFooter.vue && git commit -m "feat: add SiteFooter component"
```

---

### Task 12: Home page

**Files:**
- Create: `D:\gitcodex\nuxt-app\pages\index.vue`

- [ ] **Step 1: Create index.vue**

```vue
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
```

- [ ] **Step 2: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/pages/index.vue && git commit -m "feat: add home page"
```

---

### Task 13: Category page

**Files:**
- Create: `D:\gitcodex\nuxt-app\pages\category\[slug\].vue`

- [ ] **Step 1: Create category/[slug].vue**

```vue
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
```

- [ ] **Step 2: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/pages/category/ && git commit -m "feat: add category page"
```

---

### Task 14: Project detail page

**Files:**
- Create: `D:\gitcodex\nuxt-app\pages\project\[id\].vue`

- [ ] **Step 1: Create project/[id].vue**

```vue
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
            <div v-for="uc in project.useCases" :key="uc.who" class="use-case">
              <span class="uc-who">{{ uc.who }}</span>
              <span class="uc-what">{{ uc.what }}</span>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'compare'" class="tab-content">
          <div class="content-block">
            <div v-for="c in project.comparisons" :key="c.name" class="compare-row">
              <span class="compare-name">{{ c.name }}</span>
              <span class="compare-diff">{{ c.diff }}</span>
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
  const id = route.params.id as string
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
```

- [ ] **Step 2: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/pages/project/ && git commit -m "feat: add project detail page with tabs"
```

---

### Task 15: Cloudflare Pages deployment config

**Files:**
- Create: `D:\gitcodex\nuxt-app\wrangler.toml`

- [ ] **Step 1: Create wrangler.toml** (optional, for Cloudflare Wrangler CLI)

No file needed — Cloudflare Pages can be configured via dashboard with these settings:

- Build command: `npm run generate`
- Build output directory: `.output/public`
- Root directory: `nuxt-app`

If using Wrangler CLI:

```toml
name = "gitcodex"
compatibility_date = "2025-06-01"
pages_build_output_dir = "./.output/public"
```

- [ ] **Step 2: Test build**

```bash
cd /d/gitcodex/nuxt-app && npm run generate
```

Expected: Static HTML generated in `.output/public/`, one HTML file per route.

- [ ] **Step 3: Deploy to Cloudflare Pages**

Push to GitHub, then in Cloudflare Pages dashboard:
1. Connect Git repository
2. Set framework preset: "Nuxt"
3. Build command: `npm run generate`
4. Build output directory: `.output/public`
5. Root directory: `nuxt-app`
6. Deploy

Or via Wrangler CLI:
```bash
cd /d/gitcodex/nuxt-app && npx wrangler pages deploy .output/public
```

- [ ] **Step 4: Commit**

```bash
cd /d/gitcodex && git add nuxt-app/wrangler.toml && git commit -m "feat: add Cloudflare Pages deploy config"
```

---

### Task 16: Final integration and smoke test

- [ ] **Step 1: Verify project structure**

```bash
ls /d/gitcodex/nuxt-app/data/projects.json && echo "Data exists" || echo "MISSING DATA"
ls /d/gitcodex/nuxt-app/data/categories.json && echo "Categories exist" || echo "MISSING CATEGORIES"
```

- [ ] **Step 2: Build and check output**

```bash
cd /d/gitcodex/nuxt-app && npm run generate
```

Expected: Build succeeds, generates HTML for `/`, `/category/*`, `/project/*`.

- [ ] **Step 3: Check generated files**

```bash
ls /d/gitcodex/nuxt-app/.output/public/index.html && echo "Home page OK"
ls /d/gitcodex/nuxt-app/.output/public/project/facebook/react/index.html && echo "Detail page OK" || echo "Check a specific project path"
```

- [ ] **Step 4: Commit any remaining files**

```bash
cd /d/gitcodex && git status
cd /d/gitcodex && git add -A && git commit -m "chore: final integration and build verification"
```

---

### Task 17: Add data files to .gitignore (large JSON)

**Files:**
- Modify: `D:\gitcodex\.gitignore`

- [ ] **Step 1: Update .gitignore**

Add these lines to `.gitignore`:

```gitignore
# Generated data (large files)
nuxt-app/data/raw_repos.json
nuxt-app/data/projects.json
nuxt-app/data/categories.json
```

- [ ] **Step 2: Commit**

```bash
cd /d/gitcodex && git add .gitignore && git commit -m "chore: gitignore generated data files"
```
