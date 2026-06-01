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
