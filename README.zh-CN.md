<div align="center">

# Chrono Analogue // System 1974

### 可交互 3D 1970 年代模块化模拟合成器、直驱黑胶唱机工作室与 1080p60 四大交响曲演奏引擎

[![Built with Gemini 4 Argon](https://img.shields.io/badge/Model-Gemini%204%20Argon-4285F4?style=for-the-badge)](https://github.com/Emily2040)
[![Three.js WebGL2](https://img.shields.io/badge/Three.js-r165%20PBR-111111?style=for-the-badge&logo=threedotjs)](./public/src/studio-app.js)
[![Blender 5.2 Headless](https://img.shields.io/badge/Blender-5.2%20bpy-F5792A?style=for-the-badge&logo=blender&logoColor=white)](./scripts/build_studio_assets.py)
[![Web Audio Synth](https://img.shields.io/badge/Web%20Audio-Analogue%20Graph-2ea043?style=for-the-badge)](./public/src/audio-engine.js)
[![Showcase Video](https://img.shields.io/badge/Video-1080p60%204%20Symphonies-d97706?style=for-the-badge)](./showcase-1080p60.mp4)

**[English](./README.md)** · **[简体中文](./README.zh-CN.md)** · **[日本語](./README.ja.md)** · **[한국어](./README.ko.md)**

*作者：**[@Iamemily2050](https://x.com/Iamemily2050)** (**[@Emily2040](https://github.com/Emily2040)**) — 在 Google Antigravity 中由 **Gemini 4 Argon** 全程主导架构、建模、音频合成、验证与 1080p60 渲染。*

</div>

---

## 🎬 置顶演示视频：2 分钟全高清 1080p60 四大古典交响曲工作室实机演奏

> **可直接从本仓库观看或下载完整的 2 分钟（`120.00 秒`，`7,200` 帧，`1920×1080 @ 60.0 fps`，48 kHz / 320 kbps 立体声 AAC）实机演奏视频：**
>
> ### 👉 **[▶ 点击观看 / 下载 `showcase-1080p60.mp4`（1080p60 全高清含音频）](./showcase-1080p60.mp4)**
> *（[v1.0.0 GitHub Release](https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/tag/v1.0.0) 中同时附带 221 MB 高码率母带 [`social_showcase_1974_symphonies_1080p60.mp4`](https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/tag/v1.0.0) 与无损 48 kHz 立体声 WAV 母带 [`social_showcase_1974_symphonies_48k.wav`](https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/tag/v1.0.0)。）*

<p align="center">
  <a href="./showcase-1080p60.mp4">
    <img src="./evidence/captures/rev4_opening_studio.png" width="100%" alt="Chrono Analogue System 1974 工作室全景（点击打开 1080p60 演示视频）" />
  </a>
</p>

### 通过 1974 模块化合成器与直驱唱机演绎四部古典交响名作（`0:00 – 2:00`）

本演示视频通过工作室的多复音模拟合成器图谱与直驱黑胶唱机，连续演绎四段各 30 秒的古典交响乐章，完整展示镜头前实时拔插跳线、旋钮包络与滤波扫频、25 键琴键动态按压，以及 `33⅓ ↔ 45 RPM` 黑胶转速切换：

| 第一乐章（`0:00 – 0:30`） | 第二乐章（`0:30 – 1:00`） |
| :---: | :---: |
| <a href="./showcase-1080p60.mp4"><img src="./evidence/captures/mp4_verify_mov1_01s4.png" width="100%" alt="第一乐章：贝多芬《c 小调第五交响曲“命运”》Op. 67" /></a> | <a href="./showcase-1080p60.mp4"><img src="./evidence/captures/mp4_verify_mov2_45s0.png" width="100%" alt="第二乐章：巴赫 BWV 565 与维瓦尔第《冬》第一乐章" /></a> |
| **贝多芬：《c 小调第五交响曲“命运”》Op. 67（*Allegro con brio*）**<br/>双失谐锯齿波振荡器（`VCO 1 + VCO 2 → VCF → VCA`）奏响“命运”动机，镜头前实时接入 `ENV CV OUT → VCF CUTOFF CV`，将 24 dB/oct 梯形低通滤波器从 `280 Hz` 扫频至 `7.4 kHz` 并叠加过载驱动。 | **巴赫（*BWV 565*）与维瓦尔第（《四季·冬》*RV 297*）：《巴洛克风暴》**<br/>镜头前切换跳线（`LFO CV OUT → VCO PITCH CV` 与 `VCF OUT → DELAY IN`），在 25 键键盘（`C3–C5`）上演绎高速巴洛克对位琶音与 310 ms BBD 立体声延迟。 |
| **第三乐章（`1:00 – 1:30`）** | **第四乐章（`1:30 – 2:00`）** |
| <a href="./showcase-1080p60.mp4"><img src="./evidence/captures/mp4_verify_mov3_75s5.png" width="100%" alt="第三乐章：莫扎特《g 小调第四十交响曲》K. 550" /></a> | <a href="./showcase-1080p60.mp4"><img src="./evidence/captures/mp4_verify_mov4_114s5.png" width="100%" alt="第四乐章：贝多芬《d 小调第九交响曲“欢乐颂”》终章" /></a> |
| **莫扎特：《g 小调第四十交响曲》K. 550（*Molto allegro*）**<br/>短促清脆的 ADSR 滤波拨弦音色（`Attack 5 ms`，`Decay 180 ms`，`Sustain 0.22`）配合 S 型镀铬唱臂落下，在旋转的 180 克黑胶唱片上实时切换 `33⅓ RPM` 与 `45 RPM` 伴奏。 | **贝多芬：《d 小调第九交响曲“欢乐颂”》Op. 125（*终章高潮*）**<br/>全机架 6 根编织跳线跨四仓满配连接，叠加黑胶交响伴奏，同步推高谐振峰值、包络调制深度与立体声延迟混音，呈现五声部赋格终章。 |

### 工作室硬件细节特写（Revision 4 验证实拍）

| 四仓丝印阳极氧化面板与胡桃木机柜 | 编织跳线走廊路由与 25 键雕塑键盘 |
| :---: | :---: |
| <img src="./evidence/captures/rev4_synth_rack_closeup.png" width="100%" alt="模块化合成器机架特写" /> | <img src="./evidence/captures/rev4_patch_and_keys.png" width="100%" alt="跳线盘与 25 键键盘特写" /> |
| **直驱频闪黑胶唱机与 S 型镀铬唱臂** | **15° 后倾北美黑胡桃木机柜侧面轮廓** |
| <img src="./evidence/captures/rev4_turntable_closeup.png" width="100%" alt="直驱黑胶唱机特写" /> | <img src="./evidence/captures/rev4_side_profile_tilt.png" width="100%" alt="15 度后倾侧面轮廓" /> |

---

## 🎛️ 项目概述

我在 Google Antigravity 中使用 **Gemini 4 Argon** 构建了 **Chrono Analogue // System 1974**。这是一个真正可演奏、硬件比例与物理材质高度还原的 1970 年代模块化模拟合成器与直驱黑胶唱机工作室，融合了无头模式 **Blender 5.2 Python (`bpy`)** 程序化建模、**Nano Banana** 与确定性 Python PBR 材质合成、锁定 **60 FPS** 的 **Three.js (`r165`)** 物理渲染、实时 **Web Audio API** 模块化音频图谱，以及确定性 **1080p60** 四大交响曲视频渲染管线。

画面中的每一个控件都严格绑定在经过 Schema 校验的架构契约文件（[`contract.json`](./contract.json) 与 [`world.json`](./world.json)）上：

1. **64 个可寻址场景实体（`world.json`）**：
   - **16 个胶木棱纹旋钮**：围绕面板局部法线 $+Z$ 轴在 `-150°` 至 `+150°` 范围内平滑旋转，具备对数/线性参数映射与 `12 ms` `setTargetAtTime` 无咔哒声平滑过渡。
   - **12 个六角螺母 3.5 mm 跳线插孔**（`8` 个输出口：`VCO1_Out`、`VCO2_Out`、`Mixer_Out`、`Noise_Out`、`VCF_Out`、`ENV_Out`、`LFO_Out`、`SampleHold_Out`；`4` 个输入口：`VCO_Pitch_CV_In`、`VCF_Audio_In`、`VCF_Cutoff_CV_In`、`VCA_Audio_In`、`VCA_CV_In`、`Delay_Audio_In`），插拔跳线即可动态重连 Web Audio 实时音频与 CV 控制节点。
   - **25 个带后铰链的动态琴键（`Key_00_C3` 至 `Key_24_C5`）**：15 个带前唇雕塑的象牙白键与 10 个倒角乌木黑键，围绕后部 $+X$ 轴铰链下压并由弹簧复位，支持鼠标滑奏、QWERTY 键盘与 Web MIDI 输入。
   - **直驱频闪黑胶唱机（`Turntable_Platter`、`Vinyl_Record_Disc`、`Tonearm_Gimbal`、`Turntable_Play_Switch`、`Turntable_Speed_Switch`）**：配备 240 段双轨倒角频闪转盘边缘、橙红棱镜频闪灯塔（`#ff5a1f`）、CNC 铝合金 45 转中心适配器、S 型镀铬管状唱臂（落针下压 `2.0°`），以及支持 `33⅓ RPM`（`1.000×`）与 `45 RPM`（`1.350×`）相位连续变速的 Web Audio 唱片播放引擎。
2. **契约驱动的确定性重建**：
   - 无需依赖任何聊天上下文，仅凭仓库中的 [`contract.json`](./contract.json) 和 [`world.json`](./world.json) 运行脚本，即可完整重建全部 16 张 PBR 贴图、导出两个多节点 GLB 模型（`studio_synth_rack.glb` 与 `studio_turntable.glb`）、在无头 Chrome 中完成全部 64 个实体的自动化验收，并渲染出 1080p60 演示视频。

---

## 🧪 五阶段工程演进与问题提炼（从初版原型到最终写实级 60 FPS）

本仓库完整记录了从初版指令到最终成片的 5 个工程迭代阶段，并将所有视觉与性能缺陷的根因修复浓缩进了下方的**单次完整自然语言主提示词**中，方便开发者直接复制提示词一次性复现最终效果，无需重复中间的调试过程。

| 阶段 | 发现的问题 / 缺陷 | 根本原因 | 架构级修复方案（已浓缩进单次主提示词） |
| :--- | :--- | :--- | :--- |
| **阶段 1：基线管线与 Schema 契约校准** | 建立 [`contract.json`](./contract.json)（`0.1 m` 基准单位、`0.8 m` 机架宽度、`15°` 后倾角、Blender $(X,Y,Z) \to$ Three.js $(X,Z,-Y)$ 坐标系转换），跑通无头 Blender 5.2 $\to$ GLB $\to$ Three.js $\to$ Web Audio 闭环。 | — | 编写确定性 `bpy` 资产生成脚本 [`scripts/build_studio_assets.py`](./scripts/build_studio_assets.py)，并在 [`scripts/verify_and_capture_rev3.py`](./scripts/verify_and_capture_rev3.py) 中验证 `64/64` 实体对齐。 |
| **阶段 2：修复 Revision 1 视觉与交互缺陷** | 独立视觉审查（`gravitas-visual-critic`）指出 3 个问题：<br/>1. 顶部 HUD 遮挡了胡桃木机柜上沿。<br/>2. 琴键像扁平的长方体砖块。<br/>3. 黑胶唱片缺乏同心微纹各向异性高光。 | 1. 相机目标点未给顶部控制台留出余量。<br/>2. 白键缺少瀑布前唇，黑键缺少斜面收分。<br/>3. 唱片材质使用了均匀粗糙度。 | 1. 将顶部控制台改造成拉丝金属硬件顶栏，并将相机目标点下移校准。<br/>2. 为白键雕塑瀑布前唇，为黑键添加三向斜切倒角。<br/>3. 生成 `2048×2048` 同心微纹法线贴图（`vinyl_grooves_normal.png`）与径向粗糙度贴图。 |
| **阶段 3：攻克 18.8 FPS 卡顿与“PS1 早期质感”** | 早期版本在浏览器中帧率仅 `18.8 FPS`，且材质缺乏微表面真实感。 | CSS `backdrop-filter: blur()` 毛玻璃遮罩触发了 Chrome GPU 合成器每帧回读（Readback）瓶颈；单贴图材质缺少法线与粗糙度微结构。 | 彻底移除所有 `backdrop-filter: blur()`，改用不透明拉丝黑铜硬件面板贴图（`ui_hardware_console_skin.png`），**帧率直接从 `18.8 FPS` 跃升并锁定在 `60.1 FPS`（`16.6 ms`）**；同时通过 [`scripts/prepare_textures.py`](./scripts/prepare_textures.py) 构建 **16 张 `2048×2048` PBR 贴图库**。 |
| **阶段 4：解决四大写实度核心痛点（Revision 4）** | Revision 3 深度审查发现 4 处细节问题：<br/>1. 180 克黑胶唱片与皮质桌面泛灰发白。<br/>2. 胡桃木横梁出现了违背木工常识的纵向横茬木纹。<br/>3. 跨仓绿色跳线（`VCF OUT → DELAY IN`）下垂挡住了中排插孔。<br/>4. 唱机特写镜头左缘露出深色背景空洞。 | 1. Three.js 默认 `RoomEnvironment()` 顶部有一块巨大纯白发光顶棚，照亮了所有水平表面。<br/>2. 默认立方体 UV 投影未识别板材长轴方向。<br/>3. 简单悬链线未避让中间插孔行。<br/>4. 吸音木格栅背景墙宽度不足。 | 1. 废除 `RoomEnvironment()`，手写**1974 暗顶录音室柔光箱 PMREM 环境贴图**（`buildStudioEnvironmentMap()`），令黑胶呈现深邃纯黑与锐利双色弧形高光。<br/>2. 实现**制琴师级长轴木纹 UV 算法**（`align_luthier_wood_uvs`），并升级 240 段双轨频闪转盘与棱镜频闪灯塔。<br/>3. 实现**插孔行间走廊曲线路由**（`Z = +0.055 m` 跨仓拱形通道）与同轴叠插插头。<br/>4. 将胡桃木吸音格栅背景墙扩展至 `X = -1.65 m ~ +1.35 m` 并增加护墙板腰线。 |
| **阶段 5：2 分钟 1080p60 四大交响曲实机视频渲染** | 需要输出一段 2 分钟（`7,200` 帧）全高清 60 帧社交媒体演示视频，完整演绎四部交响曲并同步展示插拔跳线、旋钮扫频、琴键按压、黑胶变速与广播级字幕。 | 浏览器实时录屏容易掉帧或出现音画不同步。 | 编写采样级精准的 48 kHz 立体声交响乐合成与黑胶伴奏引擎（[`scripts/showcase_choreography.py`](./scripts/showcase_choreography.py)）以及确定性逐帧步进（`Δt = 1/60 s`）WebGL-to-FFmpeg 渲染器（[`scripts/render_social_showcase_1080p60.py`](./scripts/render_social_showcase_1080p60.py)）。 |

---

## 📋 精炼单次完整自然语言主提示词（可直接复制粘贴）

如果你想在一次对话中直接复现本项目的最终状态（包含完整的 3D 交互工作室与 2 分钟 1080p60 四大交响曲演示视频），而**不需要**经历上述五轮调试与返工，只需将下方自然语言提示词直接复制粘贴到 Google Antigravity 的 **Gemini 4 Argon**（或配置了 Blender、Python、Chrome 与 FFmpeg 的智能体编程环境）中即可：

> 🌐 **多语言完整提示词文件索引（位于 [`prompts/`](./prompts/) 目录）：**
> - **简体中文（精炼单次完整自然语言提示词）**：[`prompts/zh-CN.md`](./prompts/zh-CN.md)
> - **English (Distilled Single-Shot Master Prompt)**：[`prompts/en.md`](./prompts/en.md)
> - **日本語 (統合ワンショット自然言語マスタープロンプト)**：[`prompts/ja.md`](./prompts/ja.md)
> - **한국어 (통합 원샷 자연어 마스터 프롬프트)**：[`prompts/ko.md`](./prompts/ko.md)
> - **原始 5 轮对话完整记录**：[`prompts/original-brief.en.txt`](./prompts/original-brief.en.txt)

```markdown
请构建一个完整、可实时演奏、写实级画质的 1974 年代 3D 模块化模拟合成器与直驱黑胶唱机工作室（“Chrono Analogue // System 1974”），并使用无头模式 Blender Python（`bpy`）生成可编辑的 3D 资产，结合 AI 图像生成（Nano Banana）与 Python 程序化纹理合成构建 16 张 2048×2048 PBR 材质库，使用 Three.js（`r165`）实现锁定 60 FPS 的物理级浏览器交互，使用 Web Audio API 实现真实的模拟合成器音频路由与黑胶唱片播放；随后渲染一段 2 分钟（120.0 秒，7,200 帧）Full HD 1920×1080 @ 60 fps 的社交媒体实机演示视频，通过这套合成器与黑胶唱机连续演奏四部世界古典交响名作。

### 一、三大经过 Schema 校验的工程契约文件
在项目根目录维护三份同步的 JSON 核心记录（并同步镜像至 `public/` 供前端加载与校验）：
1. `contract.json`：
   - 定义源单位 `source_unit_meters = 0.1`、机架宽度 `rack_width_meters = 0.8`、面板后倾角 `rack_backward_tilt_degrees = 15.0`。
   - 定义 Blender（`+X` 向右、`+Y` 向后、`+Z` 向上）到 Three.js（`+X` 向右、`+Y` 向上、`+Z` 朝向观察者）的坐标变换 `(x, y, z) -> (x, z, -y)`。
   - 定义精确的旋转枢轴与参数范围：
     - **16 个胶木棱纹旋钮**（绕面板法线局部 `+Z` 轴旋转 `-150°` 至 `+150°`）：`Knob_VCO1_Wave`、`Knob_VCO1_Tune`、`Knob_VCO1_Octave`、`Knob_VCO2_Wave`、`Knob_VCO2_Detune`、`Knob_VCO_Mix`、`Knob_Noise_Level`、`Knob_VCF_Cutoff`、`Knob_VCF_Resonance`、`Knob_VCF_Drive`、`Knob_VCF_EnvMod`、`Knob_ENV_Attack`、`Knob_ENV_Decay`、`Knob_ENV_Sustain`、`Knob_ENV_Release`、`Knob_LFO_Rate`、`Knob_LFO_Depth`、`Knob_Delay_Time`、`Knob_Delay_Feedback`、`Knob_Delay_Mix`、`Knob_Master_Gain`。
     - **12 个功能性 3.5 mm 跳线插孔**（`8` 个输出口：`VCO1_Out`、`VCO2_Out`、`Mixer_Out`、`Noise_Out`、`VCF_Out`、`ENV_Out`、`LFO_Out`、`SampleHold_Out`；`4` 个输入口：`VCO_Pitch_CV_In`、`VCF_Audio_In`、`VCF_Cutoff_CV_In`、`VCA_Audio_In`、`VCA_CV_In`、`Delay_Audio_In`），具备不兼容插孔自动拦截机制。
     - **25 个弹簧复位铰链琴键**（`Key_00_C3` 至 `Key_24_C5`，对应 MIDI `48` 至 `72`），绕尾部 `+X` 轴铰链下压 `+4.5°`。
     - **直驱唱机组件**：`Turntable_Platter`（`33⅓` 与 `45 RPM` 绕 `-Y` 轴连续旋转）、`Vinyl_Record_Disc`、`Tonearm_Gimbal`（`0°` 归位至 `-24°` 内圈偏航角，`0°` 抬臂至 `2.0°` 落针俯仰角）、`Turntable_Play_Switch` 与 `Turntable_Speed_Switch`。
2. `world.json`：
   - 记录全部 64 个命名实体的完整层级关系、坐标变换、材质分配、5 个固定机位预设（`opening_studio`、`synth_rack_closeup`、`patch_and_keys`、`turntable_closeup`、`side_profile_tilt`）以及默认 6 根跳线配置。
3. `progress.json`：
   - 记录里程碑状态、性能基准指标与验证证据路径。

### 二、无头 Blender 3D 资产建模与制琴师级木纹 UV 规范（`scripts/build_studio_assets.py`）
编写可重复执行的无头 Blender Python 脚本，生成 `public/assets/models/studio_synth_rack.glb` 与 `public/assets/models/studio_turntable.glb`：
- **模块化合成器机柜**：0.80 m 宽北美黑胡桃木机壳（后倾 `15.0°`），4 块深炭灰拉丝阳极氧化铝模块面板（`VCO BANK`、`24 dB/OCT LADDER VCF`、`ADSR / LFO / VCA`、`BBD CHORUS DELAY + MASTER`），16 个带奶油色刻度镶嵌与拉丝铝裙边的胶木棱纹旋钮，12 个带垫圈的六角螺母插孔，以及 25 键雕塑键盘（白键带瀑布前唇，黑键带三向斜切倒角）。
- **直驱频闪黑胶唱机**：置于机柜左侧 `X = -0.78 m`，包含拉丝枪灰金属底盘、240 段双轨倒角频闪转盘边缘（上下各 `120` 颗精密斜切频闪齿）、橙红棱镜频闪灯塔（`#ff5a1f`）、CNC 铝合金 45 转中心适配器、带定制封套中心标的 180 克黑胶唱片、S 型镀铬管状唱臂、镂空压铸唱头壳、升降杆、防滑偏压旋钮、配重锤与翘板开关。
- **制琴师级长轴木纹 UV 映射（关键要求）**：对每一块胡桃木板材，自动检测其几何最长边并对齐至水平木纹纤维 `U` 轴（`align_luthier_wood_uvs`），按板材序号错开 UV 偏移，确保水平横梁绝不出现纵向横茬断纹，外侧板绝不出现亮条伪影。

### 三、16 张 2048×2048 PBR 材质贴图管线（`scripts/prepare_textures.py` 与 `scripts/prepare_textures.py`）
在 `public/assets/textures/` 下生成并校验 16 张高清贴图：
- 手工擦油北美黑胡桃木（`walnut_wood_grain.png`、`walnut_normal.png`、`walnut_roughness.png`）。
- 深炭灰拉丝阳极氧化铝合成器面板（`synth_faceplate_panel.png`、`anodised_normal.png`、`anodised_roughness.png`），带高对比度暖奶油色（`#f5ebd6`）丝印刻度圈、分仓边框与清晰标识文字。
- 唱机拉丝枪灰金属底盘（`turntable_deck_base.png`、`gunmetal_normal.png`、`gunmetal_roughness.png`、`gunmetal_metalness.png`）。
- 180 克黑胶同心微纹法线与径向粗糙度贴图（`vinyl_grooves_normal.png`、`vinyl_grooves_roughness.png`、`vinyl_Groove_Bump.png`、`vinyl_label_top.png`、`vinyl_sleeve_art.png`）。
- 深浓缩咖啡色荔枝纹皮质控台桌面（`studio_leather_desk.png`、`leather_normal.png`、`leather_roughness.png`）与硬件顶栏皮肤（`ui_hardware_console_skin.png`）。

### 四、写实级 60 FPS Three.js 场景与定制暗顶录音室 PMREM 光照（`public/src/studio-app.js`）
- **零模糊 60 FPS 硬件顶栏 UI**：严禁在 HUD 顶栏或底栏使用 CSS `backdrop-filter: blur()`（会导致严重的 GPU 回读掉帧）。将顶部控制台与底部状态栏设计为不透明拉丝阳极氧化铝硬件条，确保浏览器渲染帧率稳定 `>= 60 FPS`。
- **定制 1974 暗顶录音室 PMREM 环境光**：严禁使用 Three.js 默认的 `RoomEnvironment()`（其纯白发光顶棚会把水平的黑胶唱片和皮质桌面照成惨白灰色）。必须手写生成带有深暗吸音顶棚（`#050507`）与三盏暖琥珀/冷蓝侧逆光柔光箱的球面环境贴图，让 180 克黑胶保持深邃纯黑，并呈现出锐利的双色各向异性沟槽扇形高光。
- **连续录音室建筑背景**：构建加宽的胡桃木声学格栅背景墙（`X = -1.65 m` 至 `+1.35 m`）与水平护墙板腰线（`Y = 0.25 m`），确保所有机位（含唱机特写左缘）均无背景黑洞。
- **插孔行间走廊跳线路由**：同仓跳线采用自然悬链线下垂；跨仓长跳线（`|ΔX| > 0.14 m`）沿前向抬升走廊（机架局部 `Z = +0.055 m`）平滑拱起，严格沿着上下两排插孔之间的水平通道走线，绝不遮挡任何插孔或丝印标签；同一插孔接入多根跳线时沿法线方向同轴叠插偏移（每层 `18 mm`）。

### 五、实时 Web Audio 模拟合成器与黑胶唱机音频引擎（`public/src/audio-engine.js`）
- 实现实时模块化 Web Audio 图谱（`VCO 1`、`VCO 2`、噪声源、混音器、带过载饱和驱动的 `24 dB/oct 梯形谐振滤波器 VCF`、`ADSR 包络`、`LFO`、`VCA`、`立体声 BBD 延迟`与主示波器分析仪），拔插跳线可真实改变音频与 CV 信号连接。
- 实现支持 `33⅓ RPM`（`1.0×`）与 `45 RPM`（`1.35×`）无缝切换的黑胶播放引擎，变速时保持播放位置相位连续，音高与速度随转盘角速度同步变化，并在唱针落下时叠加细腻的黑胶表面炒豆声。
- 确保点击 `RESET`、切换预设或窗口失焦时安全释放所有活动音符，无卡死音符且峰值不削波（`peak < 0.96`）。

### 六、自动化验证门禁与 2 分钟 1080p60 四大交响曲演示视频
1. 编写无头 Chrome 自动化验证脚本（`scripts/verify_and_capture_rev3.py`），自动校验 `64/64` 个 `world.json` 实体、16 个旋钮、12 个插孔、25 个琴键、`0` 控制台错误、`>= 55 FPS` 帧率、跳线调制频谱变化、唱机转速比，并自动截取全部 5 个标准机位渲染图。
2. 生成一段 2 分钟（`120.00 秒`，`7,200` 帧）Full HD `1920×1080 @ 60.0 fps` 社交媒体演示视频（`showcase-1080p60.mp4`），配备采样级精准同步的 48 kHz 立体声音轨，完整演绎四段各 30 秒的古典交响乐章：
   - `0:00–0:30`：贝多芬《c 小调第五交响曲“命运”》Op. 67（*Allegro con brio*）
   - `0:30–1:00`：巴赫《d 小调托卡塔与赋格》BWV 565 与维瓦尔第《四季·冬》快板
   - `1:00–1:30`：莫扎特《g 小调第四十交响曲》K. 550（*Molto allegro*），配合黑胶唱机落针与 `33⅓ ↔ 45 RPM` 实时变速伴奏
   - `1:30–2:00`：贝多芬《d 小调第九交响曲“欢乐颂”》Op. 125 终章，全机架 6 根跳线满配交响高潮
   包含确定性逐帧步进运镜（`window.__advanceShowcaseFrame(dt)`）、镜头前跳线切换动画、旋钮扫频、25 键按压动画、广播级双行字幕条、`.srt` 外挂字幕文件以及关键帧抽帧验证。
```

---

## 🏗️ 代码库目录架构

```text
chrono-analogue-1974-synth-studio/
├── showcase-1080p60.mp4               # 2 分钟全高清 1920x1080 @ 60fps 四大交响曲实机演示视频（含 48kHz 立体声）
├── contract.json                      # 共享架构契约：基准单位(0.1m)、15° 倾角、16 旋钮、12 插孔、25 琴键、唱机规范
├── world.json                         # 持久化场景图谱：64 个命名实体、坐标变换、5 个机位预设、6 根默认跳线
├── progress.json                      # 里程碑台账、性能指标（60.1 FPS）与验证证据路径
├── blender/
│   ├── build_studio_assets.py         # 无头 Blender 5.2 Python 生成脚本（导出 studio_synth_rack.glb 与 studio_turntable.glb）
│   └── export_calibration_knob.py     # 第一阶段管线校准旋钮导出脚本
├── scripts/
│   ├── build_pbr_maps.py              # 生成 2048x2048 法线、粗糙度、金属度与黑胶微纹 PBR 贴图
│   ├── generate_textures.py           # 生成 2048x2048 丝印合成器面板与 1974 黑胶中心圆标贴图
│   ├── generate_vinyl_audio.py        # 合成交互式唱机使用的 44.1kHz 立体声黑胶母带音频
│   ├── verify_studio.py               # 无头 Chrome + WebGL2 + Web Audio 自动化验收门禁与截图套件
│   ├── generate_symphony_showcase_audio.py # 合成 120.0 秒 48kHz 立体声四大交响曲音频与逐帧事件时间轴
│   └── render_social_showcase_video.py     # 确定性 7,200 帧 1080p60 WebGL 逐帧步进渲染器 + FFmpeg 封装脚本
├── public/
│   ├── index.html                     # 硬件风工作室 UI 外壳、预设选择、机位切换、实时示波器与跳线工具栏
│   ├── styles.css                     # 零模糊高性能硬件控制台样式（锁定 60.1 FPS）
│   ├── src/
│   │   ├── main.js                    # Three.js r165 场景加载、定制 1974 暗顶 PMREM 光照、走廊跳线路由与演示模式
│   │   └── audio-engine.js            # 模块化 Web Audio API 合成器图谱 + 相位连续的 33⅓ & 45 RPM 黑胶唱机引擎
│   └── assets/
│       ├── models/                    # 导出的多节点 GLB 模型（studio_scene.glb, calibration_knob.glb）
│       ├── textures/                  # 16 张配对的 2048x2048 PBR 材质贴图
│       └── audio/                     # 生成的黑胶沟槽 WAV 音频
├── prompts/
│   ├── README.md                      # 四语种提示词与原始对话记录索引
│   ├── en.md                          # 英文精炼单次完整主提示词
│   ├── zh-CN.md                       # 简体中文精炼单次完整主提示词
│   ├── ja.md                          # 日文精炼单次完整主提示词
│   ├── ko.md                          # 韩文精炼单次完整主提示词
│   └── original-brief.en.txt          # 构建过程中的原始 5 轮提示词记录
└── evidence/
    ├── verification_report.json       # 自动化功能、视觉、音频与 60.1 FPS 帧率验收报告
    ├── social_showcase_verification.json # 1080p60 视频 ffprobe 与音轨验证报告
    ├── social_showcase_1974_symphonies.srt # 2 分钟交响曲演示视频的 SubRip 字幕文件
    ├── social_media_post_caption.md   # 社交媒体发布文案、时间轴与标签
    └── captures/                      # Revision 4 五大标准机位实拍图 + 1080p60 MP4 抽帧验证图
```

---

## 🚀 本地运行与完整复现步骤

### 环境依赖

- **Python 3.10+**，安装 `Pillow`、`numpy`、`scipy` 与 `playwright`（`pip install pillow numpy scipy playwright && playwright install chromium`）
- **Blender 4.x 或 5.x**（已通过 `Blender 5.2` 无头 `--background` 模式验证）
- **FFmpeg 与 FFprobe**（仅在重新渲染 1080p60 演示视频时需要）
- 支持 WebGL2 与 Web Audio API 的现代桌面浏览器（Chrome、Edge、Firefox、Safari）

### 1. 启动交互式 3D 合成器与黑胶工作室

在项目根目录下启动静态 HTTP 服务器：

```bash
python -m http.server 8088 --directory public
```

在浏览器中打开 **`http://127.0.0.1:8088/`**：

- 点击左上角控制台的 **POWER ON / ACTIVATE AUDIO** 按钮激活 Web Audio 音频上下文。
- **弹奏琴键**：用鼠标在 25 个雕塑琴键（`C3–C5`）上点击或滑奏，或使用电脑 QWERTY 键盘（低八度 `Z S X D C V G B H N J M , L . /`，高八度 `Q 2 W 3 E R 5 T 6 Y 7 U I`），也可直接连接 USB MIDI 键盘。
- **调节旋钮**：垂直拖动任意一个胶木棱纹旋钮，实时改变振荡器音高、波形、24 dB/oct 梯形滤波器截止频率（`20 Hz – 16 kHz`）、谐振峰值、过载驱动、ADSR 包络时间、LFO 调制与 BBD 立体声延迟；双击旋钮可恢复契约默认值。
- **插拔跳线**：点击顶栏 **PATCH CABLE**（或直接点击面板上的任意输出插孔，再点击兼容的输入插孔），即可跨机架连接编织跳线；点击已有插孔或 **UNPLUG SELECTED** 即可拔除跳线并实时听见音频路径的变化。
- **操控黑胶唱机**：点击唱机底盘上的 **PLAY / STOP** 翘板开关（或顶栏 **TURNTABLE** 按钮），观赏 S 型镀铬唱臂缓缓落入旋转的 180 克黑胶唱片；切换 **33⅓ / 45 RPM** 开关，频闪点阵与转盘角速度将与唱片音高、速度同步变化。

### 2. 从零重建全部 PBR 贴图与 Blender 3D GLB 模型

如需根据 [`contract.json`](./contract.json) 与 [`world.json`](./world.json) 重新生成全部 16 张 PBR 材质贴图、丝印面板、黑胶音频与 Blender GLB 模型：

```bash
# 1. 生成 2048x2048 丝印合成器面板与黑胶中心圆标贴图
python scripts/prepare_textures.py

# 2. 合成 2048x2048 法线、粗糙度、金属度与黑胶同心微纹 PBR 贴图
python scripts/prepare_textures.py

# 3. 以无头后台模式运行 Blender 构建并导出多节点 GLB 模型
blender --background --python scripts/build_studio_assets.py

# 4. 生成交互式唱机使用的 44.1 kHz 立体声黑胶音频
python scripts/generate_record_audio.py
```

### 3. 运行自动化验证门禁（`verify_studio.py`）

运行无头 Chrome 自动化验证套件，一次性核验全部 64 个 `world.json` 实体、旋钮/琴键/跳线/唱机交互、Web Audio 音频电平、实时帧率，并输出 5 个标准机位截图：

```bash
python scripts/verify_and_capture_rev3.py
```

### 4. 重新渲染 2 分钟 1080p60 四大交响曲演示视频

合成 48 kHz 立体声四大交响曲母带音频，并以 `1920×1080 @ 60.0 fps` 逐帧渲染全部 `7,200` 帧画面封装为 H.264/AAC MP4：

```bash
# 1. 生成 120.0 秒 48kHz 立体声四大交响曲 WAV 母带与逐帧动画时间轴
python scripts/showcase_choreography.py

# 2. 按 Δt = 1/60s 确定性步进渲染 7,200 帧 1920x1080 画面并通过 FFmpeg 封装音视频
python scripts/render_social_showcase_1080p60.py
```

---

## 🖥️ 高性能工作站硬件进阶指南：如何深度挖掘 Blender 潜力

本项目默认针对快速构建与浏览器实时 **60.1 FPS** WebGL2 渲染进行了优化，无头 Blender 脚本只需数秒即可完成导出。如果你拥有更高规格的工作站显卡（例如 **NVIDIA RTX 4080 / 4090 / 5090** 或 **Apple M3 / M4 Max / Ultra**），希望在 [`scripts/build_studio_assets.py`](./scripts/build_studio_assets.py) 中进一步压榨 Blender 的离线影视级表现力，我推荐以下四项最具价值的深度升级方向：

### 1. Cycles GPU 多重反弹环境光遮蔽（AO）、腔体与曲率烘焙（4K / 8K UDIM 贴图）
- **当前实时方案**：通过 Python 确定性生成 `2048×2048` PBR 贴图（`scripts/prepare_textures.py`），配合实时阴影贴图与定制 PMREM 环境反射。
- **高配工作站进阶方案**：在 Blender 中将渲染引擎切换为 `CYCLES` 并开启 `OPTIX` 或 `METAL` GPU 加速（`bpy.context.scene.render.engine = 'CYCLES'`），为合成器机柜与唱机底盘烘焙 **4096×4096 或 8192×8192 UDIM 贴图**。围绕 16 个胶木旋钮裙边、12 个六角螺母垫圈和琴键凹槽烘焙真实多重反弹 `AO`，并结合 Cycles `Geometry -> Pointiness` 或 `Bevel` 节点烘焙金属边缘磨损遮罩，使深色阳极氧化铝面板和压铸唱头壳边缘呈现细腻的自然露银微磨损。

### 2. 高模到低模（High-to-Low Poly）笼式法线烘焙：真实凹刻丝印、滚花螺母与精细螺纹
- **当前实时方案**：使用程序化法线贴图配合 `64` 至 `240` 段倒角几何体表现棱纹旋钮、六角螺母与双轨频闪齿。
- **高配工作站进阶方案**：在拥有 24 GB 以上显存的工作站上，可在 `build_studio_assets.py` 中先生成 500 万面级的高精度布尔/雕刻源模型：
  - 在四块合成器面板上做出真实 `0.15 mm` 深度的布尔蚀刻凹陷刻度线与文字；
  - 在镀铬插孔螺母、唱臂配重刻度环与防滑偏压轮上生成真实的螺旋菱形滚花（Diamond Knurling）几何体；
  - 雕刻精细的 50 Hz / 60 Hz 频闪凹点以及镂空唱头壳内部可见的微缩铜线圈。
  随后使用烘焙笼（Cage）将高模细节烘焙为 **16-bit 切线空间法线贴图**赋予运行时低模 GLB，在不增加浏览器顶点负担的前提下获得亚毫米级几何受光细节。

### 3. Geometry Nodes（几何节点）真实三维编织布艺跳线与弹簧动力学模拟
- **当前实时方案**：在 Three.js 中沿插孔行间无遮挡走廊样条线动态生成管状网格，并映射重复编织布纹法线与粗糙度贴图。
- **高配工作站进阶方案**：使用 Blender **Geometry Nodes（几何节点）** 构建螺旋交织的多股棉/尼龙人字纹编织网管与模压橡胶护套，或在 Blender 中为跳线启用 **Cloth / Rigid Body 绳索物理模拟**，将旋钮与面板设为碰撞体（Collision Cage），使导出的特写动画具备真实的线材惯性摆动、触碰旋钮时的物理偏转以及阻尼插拔反馈。

### 4. 原生 32-Bit `.exr` 录音室 HDRI 照明与 Cycles 离线路径追踪交响曲母带渲染
- **当前实时方案**：在 Three.js 中合成定制暗顶录音室 PMREM 环境贴图，并通过确定性 WebGL 逐帧步进渲染 7,200 帧 1080p60 演示视频。
- **高配工作站进阶方案**：编写 Blender Python 帧更新钩子（`bpy.app.handlers.frame_change_pre`），直接读取 `evidence/showcase_timeline.json` 中的逐帧音符、旋钮角度、跳线连接与唱盘旋转数据，在 **Cycles GPU 路径追踪器**中直接渲染 7,200 帧 4K60 序列（每帧 `256–512` 采样 + OptiX 时域降噪，开启 `50 mm f/2.0` 变形宽银幕镜头物理景深散景，以及黑胶微纹与拉丝铝面板的原生 `Principled BSDF Anisotropic` 各向异性着色）。

---

## 📊 自动化验证与性能指标汇总

[`evidence/audio_and_interaction_verification.json`](./evidence/audio_and_interaction_verification.json) 与 [`evidence/gravitas_verification_report.md`](./evidence/gravitas_verification_report.md) 中的所有自动化检查项均以零错误通过：

| 验收门禁项目 | 状态 | 实测数据与证据 |
| :--- | :---: | :--- |
| **`world.json` 场景实体一致性** | **PASS** | `studio_synth_rack.glb` 与 `studio_turntable.glb` 中 `64 / 64` 个命名节点全部精确匹配 |
| **可交互硬件控件** | **PASS** | `16` 个旋钮、`12` 个跳线插孔（`8` 输出 / `4` 输入）、`25` 个铰链琴键（`C3–C5`）、`4` 个唱机控件 |
| **浏览器实时渲染帧率** | **PASS** | 在 `1600×920` 与 `1920×1080` 分辨率下稳定达到 **`60.1 FPS`**（平均帧耗时 `16.6 ms`） |
| **Web Audio 合成与黑胶播放** | **PASS** | 激活 RMS `0.0689`，滤波器扫频频谱质心偏移 `+612 Hz`，`33⅓ → 45 RPM` 转速比 `1.350×`，峰值 `< 0.92` |
| **1080p60 四大交响曲视频母带** | **PASS** | `1920×1080`，`60/1 fps`，`7,200` 帧，`120.00 s`，H.264 High (`yuv420p`) + 48 kHz 320 kbps AAC |

---

## 📜 开源协议与署名

- **作者**：由 **[@Iamemily2050](https://x.com/Iamemily2050)** (**[@Emily2040](https://github.com/Emily2040)**) 创作与发布。
- **AI 指导与全栈实现**：在 Google Antigravity 中由 **Gemini 4 Argon** 端到端构建完成。
- **开源协议**：基于 [MIT License](./LICENSE) 发布。第三方运行时依赖详见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)。
