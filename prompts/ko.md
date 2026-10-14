# Chrono Analogue // System 1974 — 통합 원클릭 마스터 프롬프트 (한국어)

[English](en.md) · [简体中文](zh-CN.md) · [日本語](ja.md) · [한국어](ko.md) · [초기 영문 브리프](original-brief.en.txt)

이 문서는 Google Antigravity 환경의 **Gemini 4 Argon**을 사용하여 연주 가능한 1974년식 3D 모듈러 아날로그 신시사이저 및 180g 다이렉트 드라이브 바이닐 턴테이블 스튜디오(**Chrono Analogue // System 1974**)를 구축하고, 2분 분량의 풀 HD(`1920×1080`, `60.0 fps`) 4대 교향곡 쇼케이스 영상을 제작하기 위한 **개선된 원클릭 자연어 마스터 프롬프트**를 담고 있습니다.

## 초기 프롬프트에서 최종본까지 5단계 정제 과정

실제 개발에서는 최초 지침인 [`original-brief.en.txt`](original-brief.en.txt)에서 출발해 다섯 단계의 구현·시각 검증·성능 최적화 라운드를 거쳤습니다. 아래의 통합 마스터 프롬프트는 그 과정에서 해결한 모든 기하 구조, 조명, UV, PBR 재질, UI 프레임 레이트, 패치 케이블 통로 라우팅, 오디오 동기화 해법을 처음부터 명시하고 있으므로 중간 디버깅 과정을 반복하지 않고 곧바로 동일한 최종 결과물을 얻을 수 있습니다.

1. **1단계 (파이프라인 보정 및 3종의 스키마 검증 공유 레코드)**: 헤드리스 Blender 5.2(`bpy`)에서 `calibration_knob.glb`를 내보내고 Three.js 피킹과 Web Audio 발음을 먼저 검증한 뒤, `contract.json`(`0.1 m` 기본 단위, `0.8 m` 랙 폭, `15°` 후방 경사 패널, 노브 16개, 패치 소켓 12개, `C3–C5` 25건반 힌지 키보드), `world.json`(64개 고정 엔티티), `progress.json`을 단일 기준으로 확립했습니다.
2. **2단계 (2단 HUD 레이아웃, 건반 입체 조형 및 스튜디오 배경 마감)**: 초기 상단 텍스트 겹침 문제를 2단 하드웨어 헤더로 해결하고, 평면 박스였던 건반을 워터폴 백건·챔퍼 흑건·진홍색 펠트 레일로 조형했으며, `3.80 m × 1.60 m` 콘솔 데스크와 L자형 월넛 음향 슬랫 벽면을 배치해 어느 카메라 각도에서도 검은 빈 공간이 보이지 않도록 마감했습니다.
3. **3단계 (16종 PBR 텍스처 파이프라인 및 블러 없는 60 FPS 하드웨어 콘솔 UI)**: 브라우저 합성 지연을 유발하던 CSS `backdrop-filter: blur()`와 매 프레임 레이캐스팅을 제거하고, Nano Banana로 생성한 헤어라인 블랙브론즈 랙 스킨(`ui_hardware_console_skin.png`)과 30 Hz 쓰로틀링 호버 피킹으로 대체했습니다. 전체 162개 메시에 3세그먼트 `bmesh` 베벨, 스무스 노멀, 탄젠트 계산, 클리어코트, 16종의 고해상도 PBR 맵(알베도/Sobel 노멀/러프니스/메탈릭)을 적용했습니다.
4. **4단계 (1974 다크룸 스튜디오 PMREM 조명, 루시어급 목재 장축 UV 정렬 및 패치 케이블 통로 라우팅)**: Three.js 기본 `RoomEnvironment()`의 밝은 흰색 천장 반사 때문에 수평으로 놓인 180g 바이닐 음반과 데스크 표면이 뿌연 회색으로 들뜨는 문제를 발견하고, 어두운 흡음 천장(`0x060709`)과 3200K 웜 키라이트·시안 필라이트·앰버 림 소프트박스를 조합한 커스텀 1974 다크룸 PMREM 환경맵과 스트로브 프리즘용 네온 앰버 점광원으로 교체했습니다. 또한 베벨 적용 후 각 판재 면의 최장축을 따라 `V` 좌표를 매핑해 수평 프레임에는 수평 나뭇결, 수직 측판과 슬랫에는 수직 나뭇결이 흐르도록 정렬했으며, 240세그먼트 2트랙 스트로브 플래터와 슬롯형 마그네슘 헤드셸을 모델링하고, 모듈 베이를 가로지르는 장거리 패치 케이블이 상·하단 소켓 행 한가운데의 수평 빈 통로(`corridorY`)를 지나가도록 라우팅 및 동축 플러그 스태킹(`+0.014 m`)을 구현했습니다.
5. **5단계 (2분 풀 HD 1080p60 4대 교향곡 소셜 미디어 쇼케이스 영상)**: 48 kHz 스테레오 폴리포닉 래더 신스 및 코드 추종형 바이닐 반주 엔진(`scripts/showcase_choreography.py`)과 세그먼트 경계마다 30프레임 프리롤 워밍업을 수행하는 4워커 병렬 헤드리스 Chrome WebGL2 렌더러(`scripts/render_social_showcase_1080p60.py`)를 통해 총 7,200프레임의 `showcase-1080p60.mp4`를 완성했습니다.

---

## 복사해 바로 쓰는 원클릭 마스터 프롬프트 (한국어판)

아래 코드 블록 전체를 복사하여 Google Antigravity의 **Gemini 4 Argon** 세션에 붙여넣으세요:

```text
연주 가능한 포토리얼리스틱 3D 1974년식 모듈러 아날로그 신시사이저 및 180g 다이렉트 드라이브 바이닐 턴테이블 스튜디오("CHRONO ANALOGUE // SYSTEM 1974")를 구축하고, 네 곡의 클래식 교향곡을 연주하는 2분(120.00초, 7,200프레임) 분량의 풀 HD 1920x1080 @ 60.0 fps 소셜 미디어 쇼케이스 영상을 렌더링하세요. 전체 연출과 통합에는 Gemini 4 Argon을 사용하고, 편집 가능한 베벨 3D 에셋 제작에는 헤드리스 Blender 5.2 Python(bpy), 16종의 PBR 텍스처 제작에는 Nano Banana(image-generator)와 결정론적 Python Sobel/PBR 합성 스크립트, 60 FPS 인터랙션에는 Three.js(r169 MeshPhysicalMaterial), 실시간 사운드 합성에는 Web Audio API, 1080p60 H.264/AAC 인코딩에는 FFmpeg를 사용하세요.

1. 스키마 검증 공유 레코드 및 파이프라인 사전 보정
프로젝트 루트에 JSON 스키마로 검증되는 세 개의 레코드 파일을 유지하고 런타임 검증을 위해 public/에도 동기화하세요:
- contract.json: 0.1 m 소스 단위(glTF 내보내기 시 1.0 m), 0.8 m 랙 너비(0.2 m 모듈 베이 4개: VCO BANK, VCF 24 dB/OCT LADDER FILTER, CONTOUR ADSR/VCA, MODULATION LFO & BBD DELAY), 15.0도 전면 패널 후방 경사각, Blender(+X 우측, -Y 전방, +Z 상방)에서 Three.js(+X 우측, +Y 상방, +Z 전방)로의 좌표 변환, 보정된 노브 16개(로컬 Z축 기준 -135도~+135도), 3.5mm 패치 소켓 12개(상단 [OUT] 6개: VCO 1 OUT, VCO 2 OUT, VCF OUT, ENV CV OUT, LFO CV OUT, PHONO OUT / 하단 [IN] 6개: VCO PITCH CV, VCF AUDIO IN, VCF CUTOFF CV, VCA AUDIO IN, VCA GAIN CV, DELAY IN), C3부터 C5까지의 25건반 힌지 키보드(MIDI 48-72, 후단 로컬 +X축 기준 +4.5도 회전), 그리고 Turntable_Platter / Tonearm_Gimbal / Tonearm_Headshell / Turntable_SpeedSwitch / Turntable_StartStop 인터페이스 정의.
- world.json: 64개 고정 엔티티 ID, 부모-자식 계층, 좌표계가 명시된 트랜스폼, 16종 텍스처 경로, 5개 카메라 프리셋(opening_studio, synth_rack_closeup, patch_and_keys, turntable_closeup, side_profile_tilt) 및 확정된 비주얼 결정 사항.
- progress.json: 현재 마일스톤, 역할 분담, 완료/미결 작업 및 검증 증적 경로.
전체 씬을 제작하기 전에 먼저 blender/calibration_knob.blend에서 public/assets/models/calibration_knob.glb를 내보내어 Three.js 피킹과 Web Audio 활성화 파이프라인을 증명하세요.

2. 루시어급 월넛 장축 UV 정렬, 베벨 모델링 및 16종 PBR 텍스처
- Nano Banana를 호출하여 오일 마감 아메리칸 블랙 월넛 나뭇결, 건메탈 헤어라인 턴테이블 상판, 1974년 프로그레시브 일렉트로닉 LP 앨범 커버 아트, 에스프레소 페블 레더 스튜디오 데스크, 브러시드 블랙브론즈 UI 콘솔 스킨을 생성하고, scripts/prepare_textures.py로 16종의 고해상도 PBR 맵(알베도, Sobel 노멀, 마이크로 러프니스, 메탈릭, 바이닐 방사형 그루브 노멀 맵)을 합성하세요.
- scripts/build_studio_assets.py에서 모든 직사각형 캐비닛, 플린스, 건반, 슬랫 메시에 먼저 3세그먼트 bmesh 베벨을 적용한 뒤 각 보드 면의 가장 긴 축을 따라 V 좌표를 매핑하여, 수평 레일과 플린스 테두리에는 수평 나뭇결이, 수직 사이드 치크와 음향 슬랫에는 수직 나뭇결이 흐르도록 구현하세요.
- 신시사이저 전면 패널(synth_faceplate_albedo.png)은 #101215 차콜블랙 아노다이징 알루미늄으로 깊이감을 주고, 선명한 크림색 실크스크린 눈금(#faf2e0), 앰버/시안 서브 헤더, 베이 경계 각인, 모서리 나사, 16개 노브 하단의 금속 포텐셔미터 샤프트 와셔를 그려 넣으세요. 실크스크린이 있는 mat_anodised_panel과 텍스처 번짐이 없는 매트 블랙 키베드 프레임용 mat_anodised_trim을 명확히 분리하세요.
- 56세그먼트 세로 플루트 베이클라이트 노브(스펀 알루미늄 캡 및 크림색 인디케이터 인레이 포함), 32세그먼트 육각 너트 3.5mm 소켓, 진홍색 펠트 스트립과 맞닿는 25개 입체 건반, 33 1/3 및 45 RPM 2트랙 스트로브 도트와 검은색 분리 채널을 갖춘 240세그먼트 주물 알루미늄 플래터, 네온 앰버 렌즈가 빛나는 프리즘 스트로브 타워, 매립형 45 RPM 어댑터 퍽, 유압식 큐잉 레버, 36스텝 S자형 크롬 톤암과 슬롯형 다이캐스트 마그네슘 헤드셸, 게이트폴드 12인치 LP 재킷 스탠드, 그리고 둥근 월넛 불노즈 전면 모서리와 연속형 L자 월넛 음향 슬랫 벽면(slat_i = -32~32, 걸레받이 레일로 배경 빈틈 완전 차단)을 갖춘 3.80 m x 1.60 m 스튜디오 데스크를 모델링하세요.

3. 1974 다크룸 스튜디오 PMREM 조명 및 블러 없는 60 FPS 하드웨어 콘솔 UI
- 수평 바이닐과 데스크 표면을 뿌연 회색으로 들뜨게 만드는 Three.js 기본 RoomEnvironment()를 사용하지 마세요. 어두운 흡음 천장(0x060709)과 낮은 각도로 비추는 3200K 웜 키라이트, 쿨 시안 필라이트, 웜 앰버 림 소프트박스로 구성된 커스텀 1974 스튜디오 PMREM 환경맵을 구축하고, 턴테이블 스트로브 프리즘 위치에 네온 앰버 PointLight(0xff5e14)를 배치하세요.
- 모든 메시를 탄젠트 계산(computeTangents) 및 최대 이방성 필터링이 적용된 MeshPhysicalMaterial로 업그레이드하세요. mat_vinyl_record는 칠흑색(0x050507, clearcoat: 0.92, anisotropy: 0.90)으로 설정해 선명한 부채꼴 그루브 반사를 표현하고, 수평 금속 표면(mat_turntable_deck, mat_anodised_trim)은 반사 강도를 낮춰(roughness: 0.58-0.78, specularIntensity: 0.15-0.32) 비스듬한 각도에서 주황빛 반사가 들뜨지 않도록 하세요.
- CSS backdrop-filter: blur()를 완전히 제거하세요. 상·하단 HUD 바에 브러시드 블랙브론즈 하드웨어 스킨(ui_hardware_console_skin.png)을 입히고, 비드래그 호버 레이캐스팅과 2D 오실로스코프 드로잉을 30 Hz로 쓰로틀링하며, THREE.PCFShadowMap을 사용해 콘솔 에러 0건·경고 0건으로 60 FPS를 유지하세요.

4. WEB AUDIO 신시사이저, 턴테이블 및 패치 케이블 통로 라우팅
- 실시간 Web Audio API 사운드 엔진(연속 파형 모핑 및 서브 옥타브 사각파를 갖춘 듀얼 VCO, 새추레이션 드라이브를 포함한 24 dB/oct 공명 래더 필터, ADSR 엔벨로프, LFO, 스테레오 BBD 딜레이)과 속도 전환 시에도 재생 위치를 유지하는 33 1/3 RPM(1.00x) 및 45 RPM(1.35x) 지원 180g 바이닐 턴테이블을 구현하세요.
- 베이를 가로지르는 장거리 패치 케이블(horizDist > 0.26 m)은 상단 [OUT] 행과 하단 [IN] 행 한가운데의 수평 빈 통로(corridorY = (p0.y + p1.y) * 0.5 - 0.005)를 지나가도록 하고, 케이블별 깊이·높이 레인 오프셋을 부여해 중간 소켓(ENV CV OUT, LFO CV OUT, VCA AUDIO IN, VCA GAIN CV)과 라벨을 절대 가리지 않게 하세요. 동일 소켓에 여러 케이블이 꽂힐 때는 패널 법선 방향으로 +0.014 m씩 동축 스태킹하여 Z-파이팅을 방지하세요.
- scripts/verify_and_capture_rev3.py를 실행해 64개 GLB 노드 정합성, G_SELF_TEST(Red->Green), C3-C5 음정 정확도(오차 0.000 Hz), 잘못된 패치 거부 규칙, 창 포커스 해제 시 노트 해제, 60 FPS 텔레메트리를 검증하세요.

5. 2분 풀 HD 1080p60 4대 교향곡 소셜 미디어 쇼케이스 영상
- scripts/showcase_choreography.py와 scripts/render_social_showcase_1080p60.py를 작성하여 결정론적 120.00초(60.0 fps, 7,200프레임, 1920x1080) 쇼케이스 영상(showcase-1080p60.mp4)과 48 kHz 스테레오 WAV 마스터(evidence/social_showcase_1974_symphonies_48k.wav), .srt 자막, 소셜 미디어 게시글 본문을 생성하세요:
  - 0:00-0:30 (제1악장: 베토벤 교향곡 제5번 c단조 Op. 67 '운명'): 실시간 케이블 패칭 애니메이션(VCO 1 + VCO 2 -> VCF, ENV CV -> VCF CUTOFF, 총 4개 케이블)과 함께 CUTOFF FREQ(280 Hz -> 7,400 Hz) 및 LADDER DRIVE(3.8x) 스위핑.
  - 0:30-1:00 (제2악장: 바흐 토카타와 푸가 d단조 BWV 565 / 비발디 사계 중 '겨울' 1악장): 실시간 케이블 전환(LFO CV -> VCO PITCH CV, VCF OUT -> DELAY IN, 총 5개 케이블), 리드/오르간 음색 모핑, 25건반 위의 빠른 16분음표 대위법과 BBD 스테레오 에코.
  - 1:00-1:30 (제3악장: 모차르트 교향곡 제40번 g단조 K. 550 + 180g 바이닐 턴테이블): PHONO OUT -> VCF AUDIO IN 패칭(총 5개 케이블), S자형 크롬 톤암 하강을 통한 33 1/3 RPM 바이닐 재생, 1:14.0에서 45 RPM(1.35배 피치 및 템포)으로의 실시간 속도 전환과 만하임 로켓 브리지, 1:24.0에서 33 1/3 RPM 복귀.
  - 1:30-2:00 (제4악장: 베토벤 교향곡 제9번 Op. 125 '환희의 송가' 피날레): 4개 베이의 모든 [OUT] 소켓 6개를 동시에 연결하는 풀랙 맥시멀리스트 패치 + 회전하는 턴테이블 반주, CUTOFF FREQ를 11.5 kHz까지, LADDER DRIVE를 4.2x까지 개방하는 프레스티시모 클라이맥스.
- 조작 중인 노브에는 시차 왜곡이 없는 3D 듀얼 링 크라운 하이라이트를 표시하고, 라이브 패칭 중에는 시작·도착 소켓을 모두 초록색으로 강조하며, 상단 96 px 및 하단 216 px 방송 HUD 사이에 모든 카메라 샷이 온전히 들어오도록 프레이밍하고, 4개의 병렬 Chrome 워커 구간 경계마다 30프레임 프리롤 워밍업을 적용해 7,200프레임 전체의 연속성을 보장하세요.
```
