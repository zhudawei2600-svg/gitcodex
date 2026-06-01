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
