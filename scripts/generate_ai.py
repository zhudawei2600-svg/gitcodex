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
