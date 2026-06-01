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
