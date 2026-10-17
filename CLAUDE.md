# 햄스터 마을 — 작업 노트

재료를 합쳐 이웃 햄스터의 부탁을 들어주고 마을을 꾸미는 모바일 웹 머지 게임(PWA).

- 배포: GitHub Pages — https://lee-cloud999.github.io/hamster-village/
- 테스트 모드: `?test` (🛠 개발 도구·플레이 시간). PC 큰 화면에서는 `tester.html`의 휴대폰 틀(412×800)로 열림, `?test&pc`는 PC 배치 그대로
- 대상 기기: 안드로이드 폰(세로 전용), 아이패드(가로 배치), PC

## 파일 구조
- `index.html` — 게임 전체(HTML·CSS·JS 한 파일). 그림은 대부분 base64 WebP 상수(IMG_B64, RES_B64, EXPR_B64, EVI_B64, BOXG_B64, STONE_B64, DEC_B64 …)를 blob URL로 바꿔 씀
- `sw.js` — 서비스 워커. 화면 파일은 항상 새로 확인(no-cache), 나머지는 network-first. 캐시 이름 `hamster-village-vN` (오프라인 파일 목록을 바꾸면 N을 올림). `/bgm/`은 게임이 직접 캐시
- `bg/` 배경(day, wide, walk, walk_mid, path) · `bgm/` 배경음 · `icons/` · `press/` 포트폴리오용 스크린샷 · `tester.html`
- CSS 덮어쓰기는 `</head>` 뒤 첫 `</style>` 바로 앞에 덧붙이는 방식으로 쌓여 있음 (뒤에 있는 규칙이 이김)
- 가로 배치 미디어쿼리: `(min-aspect-ratio:1/1) and (min-width:700px) and (min-height:540px)`

## 게임 구조 요약
- 보드 6×7, 맨 윗줄 생성기, 맨 아랫줄 잠긴 칸(25부터 두 배씩)
- 주민 8명(PET_ORDER [0,1,2,3,5,6,4,7]): 보리→콩이(쳇바퀴)→밤톨→호두→참깨 할배→별이→솜 할머니→두부. 각 표정 8종(EXPR_B64), 이야기 3편(STORY, 단락별 표정 STORY_EMO, 한 단락 안 줄바꿈은 `\n`)
- 이웃 등장 조건: 앞 재료 6단계(PET_COND) + 플레이어 레벨(PET_LV) + 앞 이웃 이야기 3편(petNeed). 오기 전 '누가 오고 있어요!' 창(comingPopup)
- 주문판: 햄스터 뒤 크게, 오른쪽 보상(ordRw), 앞 선반 재료. 카드를 누르면 전하기
- 시즌 1: 레벨 30이 끝(LV_MAX, 이후 경험치는 코인으로·경험치 바 MAX). 주민 8명 + 이야기 24편을 모두 읽으면 '시즌1 종료!' 창 한 번(seasonCheck, st.s1), 도감에 배지
- 레벨 보상 '보리의 산책길'(renderPass, rewardOf, PASS_LAST=30): 레벨업하면 산책길이 열리고(openWalkAuto) 돌을 눌러 받기
- 특수 아이템: 황금 도토리 xp, 에너지 en(5단계), 도구 tl, 꿀단지 tg, 상자 bx(나무·은·금; 탭할 때마다 하나씩)
- 기간 이벤트 EVENT(가을 도토리 축제 10/15~11/15): 출석 도장, 기본/황금 패스 30칸, 축제 미션(evTrack ← track())
- 튜토리얼: st.tut 단계(tutTarget/tutDraw), 첫 등장 안내 tips(xp·eni·tgi 등, 한 번만), '다음 할 일' 칩(nextGoal)
- 상점: 에너지, 생성기 강화(GU: 500/1000/1500/2000), 보드 정리. 에너지 칸을 누르면 충전 창(#ebuy)

## 작업 규칙
- 수정할 때마다 일반 주소와 `?test` 주소를 함께 알려 주고, 가끔 강력 새로고침(Ctrl+Shift+R, 폰은 앱 완전히 닫았다 열기) 안내
- 안내 문구는 짧게 한 줄, 팝업은 흰 바탕·검은 글씨, 강조색은 연한 로즈(#ffad9e 계열), 작은 안내 글씨는 로즈색
- 스토리는 업데이트로 계속 이어지므로 엔딩을 만들지 않음. 대사는 사용자가 직접 쓴 대본을 그대로 넣음
- 커밋은 저장소 주인(Lee-cloud999) 계정으로 하고 `git push origin main`으로 바로 배포

## 확인 방법
- 로컬 서버 `python3 -m http.server 8766` + Playwright(크로미움 설치됨)로 412×800 모바일, 1000~1180 가로 화면 스크린샷 확인
- 문법 검사: index.html에서 가장 큰 `<script>` 블록을 뽑아 `node --check`
- 큰 변경 뒤에는 튜토리얼을 처음부터 '준비 끝!'까지 돌려 볼 것
