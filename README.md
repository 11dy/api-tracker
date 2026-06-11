# ad-api-notice-watcher

광고 매체 API 공지/릴리즈 노트를 매일 확인해서 **신규 공지만** Claude로 요약하고 텔레그램으로 발송하는 시스템.

## 동작 흐름

```
GitHub Actions (매일 09:00 KST / 수동 실행)
│
├─ 1. scripts/crawl.py                     ← 결정적 처리 (LLM 없음)
│     sources.json의 각 소스에서 최신 공지 최대 10건 파싱
│     → { id: sha1(url), source, title, url, date }
│     → state/seen.json에 없는 id만 신규로 분류
│     → 신규 있으면 본문 수집 후 out/new_items.json 생성
│     → seen.json 갱신 (소스별 최근 200개 유지)
│
├─ 2. out/new_items.json 존재? ──── 없음 → 종료 (Claude 호출 안 함)
│                          │
│                         있음
│                          ▼
├─ 3. anthropics/claude-code-action       ← Claude는 요약에만 사용
│     .claude/skills/notice-summary 규칙으로
│     중요도(🔴🟡🟢) 분류 + 요약 → out/summary.md
│
├─ 4. scripts/notify.py                   ← 결정적 처리
│     summary.md → 텔레그램 sendMessage (4096자 초과 시 분할)
│
└─ 5. state/seen.json 변경 시 git commit & push
```

## 모니터링 대상

| 소스 | 방식 | 상태 |
|---|---|---|
| 네이버 검색광고 API | GitHub Issues API | ✅ |
| 네이버 GFA API | Docusaurus 블로그 HTML | ✅ |
| 카카오 데브톡 공지 | Discourse JSON (`/c/notice.json`) | ✅ |
| Google Ads API | 릴리즈 노트 페이지의 버전 헤딩(h2) 단위 | ✅ |
| Meta Graph API | changelog의 버전 링크 단위 | ✅ |
| Criteo Marketing API | — | ❌ URL 404 (`enabled: false`) |
| TikTok Business API | — | ❌ JS 렌더링 (`enabled: false`) |

## 설정

### 1. 텔레그램 봇 생성

1. 텔레그램에서 [@BotFather](https://t.me/BotFather) 검색 → `/newbot` → 봇 이름/username 입력
2. 발급된 **bot token** 저장 (예: `123456789:AAH...`)
3. 생성한 봇에게 아무 메시지나 보낸 뒤(또는 그룹에 봇 초대 후 메시지), 아래로 **chat_id** 확인:
   ```bash
   curl "https://api.telegram.org/bot<BOT_TOKEN>/getUpdates"
   # → result[].message.chat.id 값이 chat_id (그룹은 음수일 수 있음)
   ```

### 2. GitHub Secrets 등록

repo → Settings → Secrets and variables → Actions → New repository secret

| Secret | 값 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API 키 |
| `TELEGRAM_BOT_TOKEN` | BotFather가 발급한 토큰 |
| `TELEGRAM_CHAT_ID` | 위에서 확인한 chat_id |

### 3. 첫 실행

push 후 Actions 탭에서 `ad-api-notice-watch` → Run workflow (수동 실행).
**최초 실행은 현재 공지 전체를 seen 처리만 하고 알림을 보내지 않는다** (초기화).
이후 실행부터 신규 공지만 알림.

## 로컬 테스트

```bash
pip install -r requirements.txt

# 1) 첫 실행 — 소스별 파싱 결과 출력 + seen.json 초기화 (알림 대상 없음)
python scripts/crawl.py

# 2) state/seen.json에서 id 몇 개를 삭제한 뒤 재실행
#    → 삭제한 id가 신규로 분류되어 out/new_items.json이 생성되는지 확인
python scripts/crawl.py
cat out/new_items.json

# 3) 텔레그램 발송 테스트 (out/summary.md를 직접 만들어서)
echo "📢 테스트 메시지" > out/summary.md
TELEGRAM_BOT_TOKEN=xxx TELEGRAM_CHAT_ID=yyy python scripts/notify.py
```

## 소스 추가 방법

1. `sources.json`에 항목 추가:
   ```json
   {
     "id": "new_source",
     "name": "표시될 소스명",
     "url": "https://...",
     "type": "html | json | github_api",
     "parser": "parse_new_source",
     "enabled": true
   }
   ```
2. `scripts/crawl.py`에 파서 함수 작성 후 `PARSERS` 딕셔너리에 등록.
   파서는 `[{ id, title, url, date, content }]`를 최신순으로 반환 (최대 10건, `id`는 `item_id(url)` 사용).
3. 로컬에서 `python scripts/crawl.py` 실행 → 파싱 결과 확인.
   새 소스는 첫 실행 때 자동으로 seen 초기화되어 기존 공지가 알림으로 쏟아지지 않는다.

## 디렉토리 구조

```
├── .github/workflows/watch.yml          # 크론 워크플로
├── .claude/skills/notice-summary/SKILL.md  # 요약 규칙 (중요도 분류)
├── scripts/
│   ├── crawl.py                         # 수집 → 신규 판별 → new_items.json
│   └── notify.py                        # 텔레그램 발송
├── sources.json                         # 모니터링 대상 정의
├── state/seen.json                      # 알림 완료 id (git 커밋 대상)
└── out/                                 # new_items.json, summary.md (커밋 안 함)
```
