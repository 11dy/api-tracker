# [신규 기능 소개] 쿼터 사용량 통계 개편 | [New Feature] New quota usage statistics

- 매체: 카카오 데브톡 공지 (`kakao_devtalk`)
- 공지일: 2026-11-05
- 수집일: 2026-11-12 (KST)
- 중요도: 🟡
- 원문: https://devtalk.kakao.com/t/new-feature-new-quota-usage-statistics/152615
- id: `cb9b146ebf88438c84477c7aefdb27e45c315256`

## 요약

앱 관리 > 통계의 쿼터 정보가 월간/일간 쿼터 페이지로 분리되어 사용률, 일별·시간대별·누적 사용량, 전월·전일 비교, 사용 추이를 제공. 콘솔 화면 개편이며 API 변경은 아님.

## 원문 발췌

카카오 데브톡 [신규 기능 소개] 쿼터 사용량 통계 개편 | [New Feature] New quota usage statistics Notice / 공지 kakao 11월 5, 2026, 9:57오전 1 안녕하세요. 카카오입니다. 카카오디벨로퍼스를 이용해 주셔서 감사합니다. 앱 관리 페이지 > [통계] 페이지에서 제공하던 쿼터 정보가 월간 쿼터 와 일간 쿼터 페이지로 분리되어 더 풍부한 데이터를 제공하게 되었습니다. 새로 개편된 페이지에서 제공하는 데이터를 소개합니다. 자세한 정보는 문서 를 참고합니다. 이번 달 사용량 / 오늘 사용량 : 앱에 적용된 월간/일간 쿼터와 사용량, 남은 쿼터를 제공합니다. 쿼터 사용률 로 소진 속도를 파악해 호출량을 미리 관리할 수 있어요. image 1810×872 71.2 KB image 1100×286 24.9 KB 일별·시간대별 사용량과 누적 사용량 : 이번 달의 일별 사용량과 오늘의 시간대별 사용량 및 누적 사용량을 제공합니다. 호출이 몰리는 시간대나 피크 요일을 찾아 요청 분산 전략을 세울 수 있어요. image 1836×800 68 KB 이전 사용량 지난 달 / 어제와의 비교 : 이번 달 사용량은 지난 달 과, 오늘 사용량은 어제 와 비교할 수 있어요. 사용 추이 : 지난 24개월간 월별 사용 추이, 최근 14일간 일별 사용 추이를 제공합니다. 이 데이터로 주중/주말 패턴을 파악하거나, 월별 특성을 파악하여 서비스를 안정적으로 운영할 수 있습니다. 변화량과 사용률을 보며 이상 징후를 포착할 수 있어요. image 1836×858 67 KB image 1298×352 18.4 KB 궁금한 점이 있으면 데브톡으로 문의해 주세요. 감사합니다. 카카오디벨로퍼스 Hello, this is Kakao. Thank you for using Kakao Developers. The quota statistics previously provided on the App management page > [Statistics] page have been split into Monthly quota and Daily quota pages, offering richer data. Here’s what the newly reorganized pages provide. For details, see the documentation . Usage this month / Usage today : View the monthly/daily quota and usage applied to your app, along with the remaining quota. The quota usage rate helps you track consumption pace and manage call volume in advance. ** Daily, hourly, and cumulative usage** : View this month’s daily usage, today’s hourly usage, and cumulative usage. Identify peak hours or days to build request distribution strategies. Previous usage Comparison with last month / yesterday : Compare this month’s usage with last month , and today’s usage with yesterday . Usage trends : Monthly usage trends over the last 24 months, and daily usage trends over the last 14 days. Use this data to understand weekday/weekend patterns or monthly characteristics for stable service operation. Spot anomalies by checking changes and usage rates. If you have any questions, please contact us via Devtalk. Thank you. Kakao Developers 홈 카테고리 가이드라인 이용약관 개인정보 취급방침 Discourse 를 사용합니다. JavaScript가 활성화된 상태에서 가장 잘 보입니다.
