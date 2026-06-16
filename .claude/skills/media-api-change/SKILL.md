---
name: media-api-change
description: 광고/미디어 매체 API의 최신 공지·릴리즈 노트를 온디맨드로 조회해 요약한다. `/media-api-change <매체명>` (예: naver, kakao, google, meta, all). 크론/seen.json과 무관하게 소스 사이트를 그 자리에서 직접 조회→현재 세션에 요약한다.
---

# /media-api-change — 매체 API 변경 온디맨드 확인

사용자가 입력한 매체명에 해당하는 공식 공지/릴리즈 노트를 **그 자리에서 직접 조회**해
현재 세션에 요약한다. 별도 파이썬 크롤러·`seen.json`·크론과 무관하게 동작한다.

- **수집**: Claude의 `curl`/WebFetch (신규 판별 없이 최신 목록을 그대로 가져옴)
- **요약**: 이 세션 (아래 `notice-summary` 규칙 적용)

## 입력

`/media-api-change <매체명>` — 매체명은 아래 표의 키. 인자가 없으면 사용자에게 묻는다.

| 매체명 | 대상 소스 |
|---|---|
| `naver` | 검색광고 API + GFA(성과형 디스플레이) **둘 다** |
| `searchad` | 네이버 검색광고 API |
| `gfa` | 네이버 GFA |
| `kakao` | 카카오 데브톡 공지 |
| `google` | Google Ads API |
| `meta` | Meta Graph API |
| `all` | 활성 소스 전부 (검색광고·GFA·카카오·Google·Meta) |
| `criteo` / `tiktok` | 현재 비활성 — 조회 불가 안내만 |

## 절차

1. **대상 소스 결정**: 위 표로 매체명 → 소스를 정한다 (`naver`는 2개).
2. **조회**: 소스별로 아래 "소스 상세"의 방법으로 받아온다.
   - 검색광고(RSS/XML)·카카오(JSON)는 `curl -s`로 받아 파싱.
   - HTML 페이지(GFA·Google·Meta)는 WebFetch로 본문 추출.
3. **요약 (현재 세션)**: `.claude/skills/notice-summary/SKILL.md`의 중요도 분류(🔴/🟡/🟢)·ETL 강제 규칙·출력 포맷을 그대로 적용해 **채팅에 요약을 출력**한다. (파일로 저장하지 않음)

## 소스 상세 (조회 힌트)

- **네이버 검색광고** (공식 공지 RSS 피드, XML)
  - 사람용 공지 페이지(원문 확인용): `https://naver.github.io/searchad-apidoc/#/notice`
  - 조회 소스(curl 대상): `curl -s "https://naver.github.io/searchad-apidoc/feed.xml"`
  → `<item>` 목록(최신순). 각 항목 `title` / `link`(원문 링크) / `pubDate`(날짜) / `category`(`notice`=공지, `release`=릴리즈노트) / `description`(HTML 이스케이프된 본문, 한글 다음에 영어 번역이 중복되니 한글만 보면 됨).
  ⚠️ `#/notice`는 AngularJS로 그려지는 SPA라 curl하면 빈 앱 껍데기만 온다. 같은 공지의 curl 가능한 데이터 원본이 `feed.xml`이므로 **조회는 항상 feed.xml로** 한다.
  ⚠️ **GitHub Issues(`/issues`)는 사용자 Q&A지 공식 공지가 아니므로 쓰지 말 것.**

- **카카오 데브톡** (Discourse JSON 엔드포인트)
  `curl -s https://devtalk.kakao.com/c/notice.json`
  → `topic_list.topics[]`: `title` / `slug` / `id` / `created_at` / `excerpt`. 원문 URL = `https://devtalk.kakao.com/t/{slug}/{id}`.

- **네이버 GFA** (Docusaurus 블로그, HTML)
  WebFetch `https://naver-ad-api.github.io/openapi-guide/blog` — 블로그 글 제목 / 날짜 / 요약 추출.

- **Google Ads** (릴리즈 노트, HTML)
  WebFetch `https://developers.google.com/google-ads/api/docs/release-notes` — `v24.1 (2026-05-13)` 형식의 버전 헤딩 단위로 변경점 정리.

- **Meta Graph API** (changelog, HTML)
  `https://developers.facebook.com/docs/graph-api/changelog` — 버전(`vXX.0`)별 변경 목록.
  ⚠️ Meta는 **브라우저형 UA + Python TLS 조합을 400 차단**한다. `curl`로 받을 땐 풀 브라우저 UA 말고 단순 UA를 써라: `curl -s -A "Mozilla/5.0" "<url>"`. (WebFetch가 막히면 이 방식으로 폴백)

- **criteo / tiktok**: 현재 `sources.json`에서 비활성 (criteo는 release-notes URL 404, tiktok은 Next.js JS 렌더링이라 정적 조회 불가). 요청 시 "현재 조회 불가"만 안내한다.

## 원칙

- 요약 규칙·중요도 기준·포맷은 `notice-summary` SKILL을 **단일 출처**로 따른다 (여기서 중복 정의하지 않음). 포맷/중요도 변경이 필요하면 그 파일만 고친다.
- 이 스킬은 `state/seen.json`을 읽지도 쓰지도 않는다 — 크론 알림 파이프라인과 완전히 독립이며, 같은 공지를 몇 번이고 조회/요약할 수 있다.
- 수집은 `curl`/WebFetch(결정적 조회), 요약만 Claude — 프로젝트 아키텍처 원칙과 동일.
