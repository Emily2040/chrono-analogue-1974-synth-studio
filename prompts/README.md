# Build Prompts · 创作提示词 · 制作プロンプト · 제작 프롬프트

| Language | Complete copy-pasteable single-shot prompt |
|---|---|
| **English** | [Improved single-shot build prompt](en.md) |
| **简体中文** | [单次复制版完整创作提示词](zh-CN.md) |
| **日本語** | [一括コピー用・完全制作プロンプト](ja.md) |
| **한국어** | [원클릭 복사용 전체 제작 프롬프트](ko.md) |
| **Original Initial Brief** | [`original-brief.en.txt`](original-brief.en.txt) |

## English

Each language file above contains the **distilled, improved natural-language prompt** for building the complete **Chrono Analogue // System 1974** playable 3D modular analogue synthesiser, direct-drive 180g vinyl turntable studio, and 2-minute Full HD (`1920×1080`, `60.0 fps`) four-symphony showcase video with **Gemini 4 Argon** in Google Antigravity, headless Blender 5.2 (`bpy`), Nano Banana (`image-generator`), Three.js (`r169`), Web Audio API, and FFmpeg.

During actual development, I started from [`original-brief.en.txt`](original-brief.en.txt) and ran four iterative engineering and visual verification cycles before recording the 2-minute four-symphony showcase. The improved prompts in [`en.md`](en.md), [`zh-CN.md`](zh-CN.md), [`ja.md`](ja.md), and [`ko.md`](ko.md) bake every geometric, lighting, UV, PBR material, UI performance, cable-corridor, and audio-synchronisation fix directly into a single specification so you can copy-paste one prompt without repeating the intermediate debugging steps.

## 简体中文

上方表格提供了四个语种的**提炼版单次自然语言完整提示词**，用于在 Google Antigravity 中驱动 **Gemini 4 Argon**，结合无头 Blender 5.2 (`bpy`)、Nano Banana (`image-generator`)、Three.js (`r169`)、Web Audio API 与 FFmpeg，直接构建完整的 **Chrono Analogue // System 1974** 可演奏 3D 模块化模拟合成器与直驱黑胶唱机工作室，并录制 2 分钟全高清（`1920×1080`、`60.0 fps`）四部交响曲演示视频。

在实际开发过程中，我从最初的 [`original-brief.en.txt`](original-brief.en.txt) 出发，先后经历了四轮工程实现、独立视觉审校与性能修复，随后完成了 2 分钟交响曲展示视频的合成与渲染。[`zh-CN.md`](zh-CN.md) 中的优化版主提示词已将我们在多轮迭代中验证过的所有几何倒角、暗房软箱光照、木纹长轴 UV 对齐、16 张 PBR 贴图、零模糊 60 帧硬件 HUD、跳线走廊防遮挡路由以及 48 kHz 声画同步方案一次性写清，复制粘贴即可直接复现最终效果，无需重走中间的排错与返工步骤。

## 日本語

上の表の各リンクには、Google Antigravity 上の **Gemini 4 Argon** とヘッドレス Blender 5.2 (`bpy`)、Nano Banana (`image-generator`)、Three.js (`r169`)、Web Audio API、FFmpeg を用いて、演奏可能な 1974 年式 3D モジュラー・アナログ・シンセサイザー＆ダイレクトドライブ・ターンテーブル・スタジオ（**Chrono Analogue // System 1974**）と、2 分間のフル HD（`1920×1080`・`60.0 fps`）4 大交響曲ショーケース映像を構築するための**改良版シングルショット自然言語プロンプト**を収録しています。

実際の制作では、最初の [`original-brief.en.txt`](original-brief.en.txt) から出発し、4 回の実装・視覚検証・UI 高速化サイクルを経て最終版に到達しました。[`ja.md`](ja.md) の改良版プロンプトには、ダークルーム照明、木目 UV の長軸整列、16 枚の PBR マップ、`backdrop-filter` を排した 60 fps ハードウェア HUD、ジャック間コリドーを通るパッチケーブル配線、48 kHz ステレオ音声合成と 1080p60 並列レンダリングの全要件があらかじめ織り込まれており、途中のバグ修正や UI 改修を繰り返すことなく一度のコピー＆ペーストで同等の結果を得られます。

## 한국어

위 표의 각 언어 파일에는 Google Antigravity의 **Gemini 4 Argon**, 헤드리스 Blender 5.2 (`bpy`), Nano Banana (`image-generator`), Three.js (`r169`), Web Audio API, FFmpeg를 결합하여 연주 가능한 1974년식 3D 모듈러 아날로그 신시사이저 및 다이렉트 드라이브 바이닐 턴테이블 스튜디오(**Chrono Analogue // System 1974**)와 2분 분량의 풀 HD(`1920×1080`, `60.0 fps`) 4대 교향곡 쇼케이스 영상을 제작할 수 있는 **개선된 원클릭 자연어 마스터 프롬프트**가 수록되어 있습니다.

실제 제작 과정에서는 초기 지침인 [`original-brief.en.txt`](original-brief.en.txt)에서 출발해 네 차례의 엔지니어링 및 시각 검증·성능 개선 라운드를 거쳐 완성본에 도달했습니다. [`ko.md`](ko.md)의 통합 마스터 프롬프트는 다크룸 스튜디오 조명, 목재 결 장축 UV 정렬, 16종 PBR 텍스처 파이프라인, `backdrop-filter`를 제거한 60 fps 하드웨어 콘솔 HUD, 소켓 행 사이 통로를 지나는 패치 케이블 라우팅, 48 kHz 스테레오 오디오 합성 및 1080p60 병렬 렌더링까지 모든 해결책을 처음부터 반영하고 있어 중간 디버깅 과정을 되풀이하지 않고도 곧바로 동일한 수준의 결과를 얻을 수 있습니다.
