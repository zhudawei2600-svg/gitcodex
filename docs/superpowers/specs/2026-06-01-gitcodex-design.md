# GitCodex（极光导航）设计规格书

## 项目定位

为中国人打造的 GitHub 高星产品可视化导航站。让不熟悉 GitHub 和英文的国内用户也能发现、了解全

球的优秀开源产品。

## 技术架构

```
[GitHub API]  →  [Python 数据脚本]  →  [JSON 数据文件]  →  [Nuxt 3 SSG]  →  [Cloudflare Pages]
```

- **数据层：** Python 脚本调用 GitHub Search API 拉取高星仓库，调用 AI API 生成中文内容，输出 JSON
- **展示层：** Nuxt 3 静态生成模式（SSG），部署 Cloudflare Pages
- **无需后端服务器，全静态托管**

## 页面结构

### 首页
1. 顶部导航：Logo"极光导航" + 分类菜单
2. 搜索区：居中大搜索框，磨砂玻璃背景，输入时霓虹光边亮起，实时联想下拉
3. 精选推荐：横向滑动卡片，5-8 个最热门项目
4. 分类浏览：大色块/图标网格，每个分类一个入口
5. 底部：数据来源说明 + 更新日期

### 分类页
- 左侧分类筛选 + 右侧仓库卡片列表
- 支持按语言、star 数排序

### 详情页
- 左侧：仓库名 + 标签 + 分段介绍（概述/功能亮点/适用场景/同类对比）
- 右侧：star 数 + 快速链接（GitHub、官网、中文文档）+ 截图预览

### 对比页
- 同类产品并排卡片比较

## 数据模型

```json
{
  "id": "facebook/react",
  "name": "React",
  "tagline": "构建用户界面的 JavaScript 库",
  "stars": 234000,
  "category": "开发工具",
  "subcategory": "前端框架",
  "language": "JavaScript",
  "summary": "React 是 Facebook 开源的...（100字内通俗介绍）",
  "description": "（300-500字详细介绍）",
  "highlights": ["组件化开发", "虚拟DOM", "生态强大"],
  "useCases": [
    {"who": "前端开发者", "what": "用组件快速搭建复杂网页"}
  ],
  "comparisons": [
    {"name": "Vue", "diff": "Vue 上手更简单，React 生态更大"}
  ],
  "links": {
    "github": "https://github.com/facebook/react",
    "website": "https://react.dev",
    "chinese_docs": "https://zh-hans.react.dev"
  },
  "images": ["screenshot_url"]
}
```

## 分类体系

| 一级分类 | 二级分类示例 |
|---------|------------|
| 开发工具 | 前端框架、后端框架、数据库、代码编辑器 |
| AI & 机器学习 | 大语言模型、图像生成、数据分析 |
| 效率工具 | 笔记、任务管理、自动化 |
| 设计创意 | UI组件库、图标、设计工具 |
| 学习资源 | 教程合集、电子书、面试题库 |
| 安全隐私 | 密码管理、VPN工具、加密通信 |

## UI 设计规范

**设计风格：** 极简科技风，参考 Dribbble 设计师 Gleb Kuznetsov 风格

**配色：**
- 背景深灰 `#0d1117`
- 卡片半透明 `rgba(255,255,255,0.04)`
- 主霓虹色：柔紫 `#a78bfa` / 青蓝 `#67e8f9`
- 文字主色 `#e6edf3` / 次要 `#8b949e`

**质感：**
- 全局轻微磨砂玻璃效果（backdrop-filter: blur）
- 卡片圆角 12px，半透明背景
- 图标极简线性款

**动效规范：**
- 页面切换：淡入 + 上移 8px，200ms ease-out
- 卡片悬浮：上浮 4px + 阴影扩散 + 边框霓虹渐变，300ms
- 搜索联想：列表项顺次滑入，每项延迟 30ms
- 所有过渡使用 cubic-bezier 缓出曲线，不突兀

**响应式：** 桌面端优先，移动端适配（768px 断点）

## 数据脚本设计

**输入：** GitHub Personal Access Token（环境变量）、目标 star 数阈值、分类配置

**流程：**
1. 调用 GitHub Search API 获取 star > 1000 的仓库（按 star 降序，分页获取 Top 500）
2. 对每个仓库，获取 README、语言、话题标签
3. 调用 AI API 生成中文内容（tagline、summary、description、highlights、useCases、comparisons）
4. 自动分类 + 人工审核标记
5. 输出 projects.json 到 Nuxt 项目的 data/ 目录

**输出：** `data/projects.json`（所有仓库数据）、`data/categories.json`（分类元数据）

## 部署方案

- 平台：Cloudflare Pages
- 构建命令：`cd nuxt-app && npm run generate`
- 输出目录：`nuxt-app/.output/public`
- Git 推送自动触发部署

## 项目目录结构

```
D:\gitcodex\
├── scripts/              # Python 数据脚本
│   ├── fetch_github.py   # GitHub API 拉取
│   ├── generate_ai.py    # AI 内容生成
│   └── requirements.txt
├── nuxt-app/             # Nuxt 3 前端项目
│   ├── data/             # 生成的 JSON 数据文件
│   ├── pages/            # 路由页面
│   ├── components/       # Vue 组件
│   ├── assets/           # 样式/图标
│   └── nuxt.config.ts
└── docs/
```
