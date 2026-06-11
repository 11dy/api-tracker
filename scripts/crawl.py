#!/usr/bin/env python3
"""광고 매체 API 공지 수집기.

sources.json에 정의된 소스에서 최신 공지를 파싱하고,
state/seen.json과 비교해 신규 공지만 out/new_items.json으로 저장한다.
LLM 호출 없음 — 전 과정 결정적(deterministic) 처리.
"""
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = ROOT / "sources.json"
SEEN_FILE = ROOT / "state" / "seen.json"
OUT_DIR = ROOT / "out"
NEW_ITEMS_FILE = OUT_DIR / "new_items.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 "
        "ad-api-notice-watcher"
    )
}
TIMEOUT = 25
MAX_ITEMS_PER_SOURCE = 10
SEEN_LIMIT_PER_SOURCE = 200
CONTENT_MAX_CHARS = 3000


def item_id(url: str) -> str:
    """URL 기준 sha1 해시로 공지 고유 id 생성."""
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


FALLBACK_HEADERS = {"User-Agent": "Mozilla/5.0"}  # 일부 사이트(Meta)가 브라우저 UA + Python TLS 조합을 차단


def fetch(url: str, as_json: bool = False):
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    if 400 <= resp.status_code < 500:
        resp = requests.get(url, headers=FALLBACK_HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json() if as_json else resp.text


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


# ---------------------------------------------------------------------------
# 소스별 파서 — 각 파서는 [{id, title, url, date, content}] 반환 (최신순, 최대 10건)
# content는 목록 단계에서 얻을 수 있는 경우에만 채우고, 없으면 "" (후단에서 본문 fetch 시도)
# ---------------------------------------------------------------------------

def parse_naver_searchad(source):
    """GitHub Issues API — title/html_url/created_at, body가 곧 본문."""
    issues = fetch(source["url"], as_json=True)
    items = []
    for issue in issues[:MAX_ITEMS_PER_SOURCE]:
        if "pull_request" in issue:  # PR 제외
            continue
        url = issue["html_url"]
        items.append({
            "id": item_id(url),
            "title": clean_text(issue["title"]),
            "url": url,
            "date": (issue.get("created_at") or "")[:10],
            "content": clean_text(issue.get("body") or "")[:CONTENT_MAX_CHARS],
        })
    return items


def parse_naver_gfa(source):
    """Docusaurus 블로그 — article[itemprop=blogPost] 단위."""
    soup = BeautifulSoup(fetch(source["url"]), "html.parser")
    items = []
    for article in soup.select('article[itemprop="blogPost"]')[:MAX_ITEMS_PER_SOURCE]:
        link = article.select_one('a[itemprop="url"]')
        if not link or not link.get("href"):
            continue
        url = urljoin(source["url"], link["href"])
        time_tag = article.select_one("time[datetime]")
        date = (time_tag["datetime"][:10] if time_tag else "")
        items.append({
            "id": item_id(url),
            "title": clean_text(link.get_text()),
            "url": url,
            "date": date,
            "content": "",
        })
    return items


def parse_kakao_devtalk(source):
    """Discourse JSON 엔드포인트 — /c/notice.json의 topic 목록."""
    data = fetch(source["url"].rstrip("/") + ".json", as_json=True)
    base = "https://devtalk.kakao.com"
    items = []
    for topic in data["topic_list"]["topics"][:MAX_ITEMS_PER_SOURCE]:
        url = f"{base}/t/{topic['slug']}/{topic['id']}"
        items.append({
            "id": item_id(url),
            "title": clean_text(topic["title"]),
            "url": url,
            "date": (topic.get("created_at") or "")[:10],
            "content": clean_text(topic.get("excerpt") or "")[:CONTENT_MAX_CHARS],
        })
    return items


def parse_google_ads(source):
    """단일 페이지 누적형 릴리즈 노트 — 'v24.1 (2026-05-13)' 형식 h2 단위로 아이템화."""
    soup = BeautifulSoup(fetch(source["url"]), "html.parser")
    heading_re = re.compile(r"^v[\d.]+\s*\((\d{4}-\d{2}-\d{2})\)")
    items = []
    for h2 in soup.find_all("h2"):
        text = clean_text(h2.get_text())
        m = heading_re.match(text)
        if not m or not h2.get("id"):
            continue
        url = f"{source['url']}#{h2['id']}"
        # 다음 h2 전까지의 형제 노드 텍스트를 본문으로 수집
        parts = []
        for sib in h2.find_next_siblings():
            if sib.name == "h2":
                break
            parts.append(sib.get_text(" ", strip=True))
        items.append({
            "id": item_id(url),
            "title": text,
            "url": url,
            "date": m.group(1),
            "content": clean_text(" ".join(parts))[:CONTENT_MAX_CHARS],
        })
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def parse_meta_marketing(source):
    """Graph API changelog — 버전 단위(changelog/versionXX.0 링크)로 아이템화."""
    soup = BeautifulSoup(fetch(source["url"]), "html.parser")
    seen_urls = {}
    for a in soup.select('a[href*="/docs/graph-api/changelog/version"]'):
        href = a.get("href", "")
        m = re.search(r"/changelog/(version[\d.]+)", href)
        if not m:
            continue
        url = urljoin("https://developers.facebook.com", href.split("#")[0].split("?")[0])
        version = m.group(1).replace("version", "v")
        seen_urls.setdefault(url, version)
    # 버전 내림차순 정렬 후 최신 10건
    def ver_key(pair):
        nums = re.findall(r"\d+", pair[1])
        return tuple(int(n) for n in nums) if nums else (0,)
    items = []
    for url, version in sorted(seen_urls.items(), key=ver_key, reverse=True)[:MAX_ITEMS_PER_SOURCE]:
        items.append({
            "id": item_id(url),
            "title": f"Graph API Changelog {version}",
            "url": url,
            "date": "",  # 목록 페이지에 날짜 노출 없음 (본문 fetch 단계에서 보강 시도 안 함)
            "content": "",
        })
    return items


def parse_criteo(source):
    """readme.io 릴리즈 노트 — 릴리즈 헤딩(h2/h3) 단위. 현재 URL 404로 enabled: false."""
    soup = BeautifulSoup(fetch(source["url"]), "html.parser")
    items = []
    for h in soup.select("article h2, article h3, main h2, main h3"):
        text = clean_text(h.get_text())
        if not text or not h.get("id") or "not found" in text.lower():
            continue
        url = f"{source['url']}#{h['id']}"
        date_m = re.search(r"\d{4}[-./]\d{1,2}[-./]\d{1,2}", text)
        items.append({
            "id": item_id(url),
            "title": text,
            "url": url,
            "date": date_m.group(0) if date_m else "",
            "content": "",
        })
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def parse_tiktok(source):
    """TikTok 포털 — Next.js JS 렌더링이라 requests로 파싱 불가. enabled: false."""
    return []


PARSERS = {
    "parse_naver_searchad": parse_naver_searchad,
    "parse_naver_gfa": parse_naver_gfa,
    "parse_kakao_devtalk": parse_kakao_devtalk,
    "parse_google_ads": parse_google_ads,
    "parse_meta_marketing": parse_meta_marketing,
    "parse_criteo": parse_criteo,
    "parse_tiktok": parse_tiktok,
}


# ---------------------------------------------------------------------------
# 본문 보강 — content가 비어 있는 신규 아이템은 상세 페이지 fetch 시도
# ---------------------------------------------------------------------------

def fetch_content(item):
    try:
        soup = BeautifulSoup(fetch(item["url"]), "html.parser")
        main = (
            soup.select_one('article div[class*="markdown"]')
            or soup.find("article")
            or soup.find("main")
            or soup.body
        )
        if main:
            return clean_text(main.get_text(" ", strip=True))[:CONTENT_MAX_CHARS]
    except Exception as exc:  # noqa: BLE001
        print(f"  [warn] 본문 수집 실패 ({item['url']}): {exc}", file=sys.stderr)
    return ""


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def load_seen():
    if SEEN_FILE.exists():
        raw = SEEN_FILE.read_text(encoding="utf-8").strip()
        if raw:
            return json.loads(raw)
    return {}


def main():
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    seen = load_seen()
    all_new = []

    for source in sources:
        sid = source["id"]
        if not source.get("enabled", True):
            print(f"[skip] {sid} (enabled: false)")
            continue

        parser = PARSERS.get(source["parser"])
        if parser is None:
            print(f"[warn] {sid}: 파서 {source['parser']} 미정의 — 스킵", file=sys.stderr)
            continue

        try:
            items = parser(source)
        except Exception as exc:  # noqa: BLE001 — 네트워크/파싱 실패 소스는 경고 후 스킵
            print(f"[warn] {sid}: 수집 실패 — {exc}", file=sys.stderr)
            continue

        print(f"[ok] {sid}: {len(items)}건 파싱")
        for it in items:
            print(f"     - ({it['date'] or '날짜없음'}) {it['title'][:70]} | {it['url']}")

        seen_ids = seen.get(sid)
        if seen_ids is None:
            # 초기화: 이 소스의 첫 수집 — 전체를 seen 처리만 하고 알림 대상 제외
            seen[sid] = [it["id"] for it in items]
            print(f"     → 최초 실행: {len(items)}건 seen 초기화 (알림 제외)")
            continue

        new_items = [it for it in items if it["id"] not in seen_ids]
        if new_items:
            print(f"     → 신규 {len(new_items)}건")
            for it in new_items:
                if not it["content"]:
                    it["content"] = fetch_content(it)
                all_new.append({
                    "id": it["id"],
                    "source_name": source["name"],
                    "title": it["title"],
                    "url": it["url"],
                    "date": it["date"],
                    "content": it["content"],
                })
            seen[sid] = ([it["id"] for it in new_items] + seen_ids)[:SEEN_LIMIT_PER_SOURCE]

    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(
        json.dumps(seen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if all_new:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        NEW_ITEMS_FILE.write_text(
            json.dumps(all_new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"\n신규 공지 {len(all_new)}건 → {NEW_ITEMS_FILE.relative_to(ROOT)}")
    else:
        NEW_ITEMS_FILE.unlink(missing_ok=True)  # 이전 실행 잔여물 제거
        print("\n신규 공지 없음")


if __name__ == "__main__":
    main()
