# [신규 기능 소개] 카카오톡 공유: 대상 선택 화면에서 [나에게] 버튼 숨기기 | [New Feature] Kakao Talk Share: Hide the [Me] button in the share picker

- 매체: 카카오 데브톡 공지 (`kakao_devtalk`)
- 공지일: 2026-11-09
- 수집일: 2026-11-12 (KST)
- 중요도: 🟡
- 원문: https://devtalk.kakao.com/t/new-feature-kakao-talk-share-hide-the-me-button-in-the-share-picker/152677
- id: `b83e470f467fb207a95cbe4b354a27dbd658ad25`

## 요약

카카오톡 공유 API에 `pickerSettings.showSendToMe=false` 옵션이 추가돼 공유 대상 선택 화면의 [나에게] 버튼을 숨길 수 있음 (기본값 true). JavaScript SDK 2.8.2 / Android·iOS SDK 26.9.0 이상.

## 원문 발췌

카카오 데브톡 [신규 기능 소개] 카카오톡 공유: 대상 선택 화면에서 [나에게] 버튼 숨기기 | [New Feature] Kakao Talk Share: Hide the [Me] button in the share picker Notice / 공지 kakao 11월 9, 2026, 8:55오전 1 안녕하세요. 카카오입니다. 카카오디벨로퍼스를 이용해 주셔서 감사합니다. 카카오톡 공유 API 호출 시 나타나는 공유 대상 선택 화면 에서 사용자 본인에게 공유하는 [나에게] 버튼을 숨길 수 있는 옵션 이 추가되었습니다. 이런 서비스에 유용해요 보상이 있는 이벤트처럼 사용자 간 공유를 전제로 한 캠페인 에 적용할 수 있어요. 친구 초대 리워드 이벤트 참여 보상 쿠폰·링크 공유 혜택 [나에게] 로 공유해 혼자 보상을 받는 경우를 줄이고, 더 많은 다른 사용자에게 공유가 닿도록 공유 대상 선택 화면을 조정할 수 있어요. share_picker_send_me_off_ko 2040×1116 128 KB 사용 방법 카카오톡 공유 API 호출 시 pickerSettings.showSendToMe 파라미터를 false 로 설정합니다. 값 결과 true [나에게] 아이콘 노출 (기본값) false [나에게] 아이콘 숨김 지원 버전 JavaScript SDK 2.8.2 이상 Android SDK : 26.9.0 이상 iOS SDK : 26.9.0 이상 관련 문서 카카오톡 공유 > 공유 대상 선택 화면 설정 궁금한 점이 있으면 데브톡으로 문의해 주세요. 감사합니다. 카카오디벨로퍼스 Hello, this is Kakao. Thank you for using Kakao Developers. The Kakao Talk Share target selection screen that appears when calling the Kakao Talk Sharing API now supports an option to hide the [Me] button . When it’s useful Use this option for campaigns that assume user-to-user sharing , such as reward events. Friend invite rewards Event participation rewards Coupon or link sharing benefits You can reduce cases where users share to themselves to claim rewards alone and adjust the share picker so that content reaches more users. How to use Set the pickerSettings.showSendToMe parameter to false when calling the Kakao Talk Share API. Value Result true [Send to me] icon shown (default) false [Send to me] icon hidden Supported versions JavaScript SDK : 2.8.2 or later Android SDK : 26.9.0 or later iOS SDK : 26.9.0 or later References Kakao Talk Sharing > Customize share picker If you have any questions, please contact us via Devtalk. Thank you. Kakao Developers 홈 카테고리 가이드라인 이용약관 개인정보 취급방침 Discourse 를 사용합니다. JavaScript가 활성화된 상태에서 가장 잘 보입니다.
