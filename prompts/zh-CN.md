# Chrono Analogue // System 1974 — 提炼版单次完整创作提示词（简体中文）

[English](en.md) · [简体中文](zh-CN.md) · [日本語](ja.md) · [한국어](ko.md) · [原始英文任务书](original-brief.en.txt)

本文件收录了在 Google Antigravity 中使用 **Gemini 4 Argon** 一次性构建 **Chrono Analogue // System 1974**（1974 年式可演奏 3D 模块化模拟合成器与 180g 直驱黑胶唱机工作室）并录制 2 分钟全高清（`1920×1080`、`60.0 fps`）四部古典交响曲演示视频的**提炼版自然语言主提示词**。

## 从初始提示词到最终版的五步提炼过程

在实际开发中，我们从最初的 [`original-brief.en.txt`](original-brief.en.txt) 出发，经过五轮验证与针对性修复才达到最终效果。下方的主提示词已经把所有关键工程经验直接写进初始约束中，复制粘贴即可直接复现最终品质，无需重走中间的排错弯路：

1. **阶段一（管线标定与三份共享契约记录）**：先打通无头 Blender 5.2 (`bpy`) 导出 `calibration_knob.glb`、Three.js 拾取与 Web Audio 发声的最小闭环，并以 `contract.json`（`0.1 m` 建模单位、`0.8 m` 机柜宽度、`15°` 面板后倾角、16 个旋钮、12 个插孔、`C3–C5` 25 键铰接键盘）、`world.json`（64 个稳定实体）与 `progress.json` 作为唯一真实数据源。
2. **阶段二（HUD 双层布局、琴键精雕与建筑背景闭合）**：将早期重叠的顶部文字重构为双层硬件状态栏；为 25 个琴键增加瀑布型白键前唇、倒角黑键与暗红呢绒止音条；扩建 `3.80 m × 1.60 m` 浓缩咖啡色皮质控台桌面与 L 型胡桃木声学格栅背景墙，彻底消除所有机位下的黑底虚空。
3. **阶段三（16 张高分辨率 PBR 贴图与零模糊 60 FPS 硬件控制台 UI）**：移除导致浏览器合成器掉帧的 CSS `backdrop-filter: blur()` 和每帧射线检测，改用 Nano Banana 生成的拉丝黑铜硬件面板皮肤（`ui_hardware_console_skin.png`）与 30 Hz 节流悬停拾取；为全部 162 个网格图元启用 3 段式 `bmesh` 实体倒角、平滑法线、切线空间计算、清漆层（Clearcoat）与 16 张高 DPI 反照率/Sobel 法线/粗糙度/金属度贴图。
4. **阶段四（1974 暗房柔光箱环境反射、制琴级木纹长轴 UV 与跳线走廊路由）**：发现 Three.js 默认的 `RoomEnvironment()` 顶部自带高亮白顶棚，会把水平放置的 180g 黑胶唱片和皮质桌面洗成灰白色；因此改用自定义深色吸音顶棚（`0x060709`）配 3200K 暖色主光、冷青辅光与琥珀色轮廓柔光箱的 PMREM 环境贴图，并压低水平金属面的 `specularIntensity`。在 `bmesh` 倒角后按每个板面的最长轴映射 `V` 坐标，使横梁呈水平木纹、侧板与格栅呈垂直木纹；升级 240 段双轨频闪铝盘、棱镜频闪灯塔与镂空镁合金唱头壳；将跨舱长跳线引导至上下插孔行正中间的水平净空走廊（`corridorY`），并为同孔多插头实现沿面板法线 `+0.014 m` 的同轴叠插。
5. **阶段五（2 分钟 1080p60 四大交响曲社交媒体展示视频）**：编写 48 kHz 立体声复音阶梯滤波合成器与和弦跟随黑胶伴奏引擎（`scripts/showcase_choreography.py`），以及带 30 帧预热（Pre-roll Warm-up）的 4 进程并行无头 Chrome WebGL2 双 PBO 渲染器（`scripts/render_social_showcase_1080p60.py`），输出 7,200 帧零掉帧的 `showcase-1080p60.mp4`。

---

## 可直接复制粘贴的单次完整主提示词（中文版）

将下方代码块完整复制到 Google Antigravity 的 **Gemini 4 Argon** 会话中：

```text
构建一个照片级真实感的可演奏 3D 1974 年式模块化模拟合成器与 180g 直驱黑胶唱机工作室（“CHRONO ANALOGUE // SYSTEM 1974”），并渲染一段 2 分钟（120.00 秒，7,200 帧）Full HD 1920x1080 @ 60.0 fps 的社交媒体展示视频，完整演奏四部世界经典交响曲片段。使用 Gemini 4 Argon 负责总体导演与集成，使用无头 Blender 5.2 Python (bpy) 生成可编辑的倒角 3D 资产，使用 Nano Banana (image-generator) 配合确定性 Python Sobel/PBR 算法生成 16 张高分辨率材质贴图，使用 Three.js (r169 MeshPhysicalMaterial) 实现 60 FPS 交互，使用 Web Audio API 实现真实合成器与黑胶发声，并使用 FFmpeg 完成 1080p60 H.264/AAC 封装。

1. 三份模式校验共享记录与管线标定
在项目根目录维护三份通过 JSON Schema 校验的记录（并同步至 public/ 供运行时自检）：
- contract.json：定义 0.1 m 建模源单位（导出 glTF 为 1.0 m）、0.8 m 机架宽度（4 个 0.2 m 模块舱：VCO BANK、VCF 24 dB/OCT LADDER FILTER、CONTOUR ADSR/VCA、MODULATION LFO & BBD DELAY）、15.0 度面板后倾角、Blender（+X 右、-Y 前、+Z 上）到 Three.js（+X 右、+Y 上、+Z 前）坐标转换、16 个标定旋钮（绕局部 Z 轴 -135 度至 +135 度）、12 个 3.5mm 插孔（上排 6 个 [OUT]：VCO 1 OUT、VCO 2 OUT、VCF OUT、ENV CV OUT、LFO CV OUT、PHONO OUT；下排 6 个 [IN]：VCO PITCH CV、VCF AUDIO IN、VCF CUTOFF CV、VCA AUDIO IN、VCA GAIN CV、DELAY IN）、C3 至 C5 共 25 个铰接琴键（MIDI 48-72，绕后部局部 +X 轴旋转 +4.5 度），以及 Turntable_Platter、Tonearm_Gimbal、Tonearm_Headshell、Turntable_SpeedSwitch、Turntable_StartStop 节点契约。
- world.json：记录全部 64 个稳定实体 ID、父子层级、带坐标系标记的变换、16 张贴图资产路径、5 个预设机位（opening_studio、synth_rack_closeup、patch_and_keys、turntable_closeup、side_profile_tilt）及视觉决策。
- progress.json：记录当前里程碑、角色分工、已完成事项与验证证据路径。
在大规模构建前，先用无头 Blender 导出 blender/calibration_knob.blend 至 public/assets/models/calibration_knob.glb，验证 Three.js 拾取与 Web Audio 音频激活闭环。

2. 制琴级胡桃木 UV、倒角建模与 16 张 PBR 材质贴图
- 调用 Nano Banana 生成油润北美黑胡桃木纹、深枪灰拉丝铝唱机面板、1974 前卫电子黑胶封套插画、深浓缩咖啡色荔枝纹皮质桌面与拉丝黑铜硬件 UI 面板底纹，并通过 scripts/prepare_textures.py 合成 16 张高 DPI PBR 贴图（反照率、Sobel 高度转法线、微粗糙度、金属度及黑胶径向微纹法线贴图）。
- 在 scripts/build_studio_assets.py 中，所有矩形木板、底座、琴键和格栅必须先执行 3 段式 bmesh 实体倒角，再沿每个面最长的几何轴向映射 V 坐标，确保水平横梁与底座边沿呈水平顺纹、垂直侧腮板与声学格栅呈垂直顺纹。
- 将合成器主面板（synth_faceplate_albedo.png）加深为 #101215 深炭黑阳极氧化铝，配高对比暖奶油色丝印刻度（#faf2e0）、琥珀/青色分舱标题、雕刻舱缝、四角螺钉以及 16 个旋钮底部的金属电位器轴套垫圈。严格区分 mat_anodised_panel（带丝印的主面板）与 mat_anodised_trim（无丝印溢出的哑光黑铜琴床框架）。
- 精细建模 56 段纵向坑纹黑胶木旋钮（配旋压铝顶盖与奶油色指针嵌条）、32 段六角螺母 3.5mm 插孔、25 个带瀑布前唇与暗红呢绒止音条的象牙白/乌木黑琴键、240 段双轨频闪铸铝转盘（独立 33 1/3 与 45 RPM 频闪点轨与黑色凹槽）、带琥珀色发光透镜的棱镜频闪灯塔、内嵌式 45 转适配器圆盘、液压升降杆、36 段 S 型镀铬管状唱臂、镂空压铸镁合金唱头壳与彩色引线、双折页 12 英寸黑胶封套立架，以及带圆润胡桃木牛鼻前缘与连续 L 型胡桃木声学格栅墙（slat_i 从 -32 到 32，配护墙横梁消除一切背景缝隙）的 3.80 m x 1.60 m 录音室控台桌面。

3. 1974 暗房柔光箱 PMREM 环境光与零模糊 60 FPS 硬件控制台 UI
- 严禁使用 Three.js 默认的白顶棚 RoomEnvironment()（会把水平黑胶与桌面反射成灰白色）。构建自定义深色吸音顶棚（0x060709）的 1974 录音室柔光箱 PMREM 环境贴图（含 3200K 暖色掠射主光、冷青控制室玻璃辅光、暖琥珀后侧轮廓柔光箱），并在唱机频闪塔处布置局部霓虹琥珀色点光源（0xff5e14）。
- 将所有网格升级为计算切线空间（computeTangents）与最大各向异性过滤的 MeshPhysicalMaterial：180g 黑胶唱片（mat_vinyl_record）设为深邃纯黑（0x050507，clearcoat: 0.92，anisotropy: 0.90）以呈现锐利的冷暖蝴蝶结微纹高光；水平金属表面（mat_turntable_deck、mat_anodised_trim）压低镜面反射（roughness: 0.58-0.78，specularIntensity: 0.15-0.32），杜绝掠射角橙光过曝。
- 彻底移除 CSS backdrop-filter: blur()。使用拉丝黑铜硬件皮肤（ui_hardware_console_skin.png）渲染上下状态栏，将非拖拽悬停射线检测与 2D 荧光示波器刷新节流至 30 Hz，并使用 THREE.PCFShadowMap，确保在 1440x900 与 1920x1080 下稳定达到 60 FPS，且零控制台错误、零弃用警告。

4. WEB AUDIO 模拟合成器、直驱唱机与跳线净空走廊路由
- 实现真实的 Web Audio API 声音引擎：双振荡器（连续波形渐变与低八度方波副振荡器）、带过载驱动的 24 dB/oct 四极点阶梯低通滤波器、ADSR 包络、LFO 调制、立体声 BBD 桶链延迟，以及支持 33 1/3 RPM（1.00x）与 45 RPM（1.35x）无断音实时变速（保持唱片播放位置连续）的 180g 黑胶唱机。
- 跨模块舱长跳线（horizDist > 0.26 m）必须穿过上下两排插孔正中间的水平净空走廊（corridorY = (p0.y + p1.y) * 0.5 - 0.005），并按走廊通道分配独立的前后深度与高度偏移，严禁遮挡中间插孔（ENV CV OUT、LFO CV OUT、VCA AUDIO IN、VCA GAIN CV）或丝印标签。共用同一插孔的多个插头须沿面板法线同轴叠插（每个插头外移 +0.014 m），消除模型穿插闪烁。
- 运行 scripts/verify_and_capture_rev3.py 验证全部 64 个 GLB 节点、红转绿自检故障注入（G_SELF_TEST）、C3-C5 零误差音准（0.000 Hz 误差）、5 项非法跳线拦截规则、失焦防卡音及 60 FPS 遥测。

5. 2 分钟 FULL HD 1080p60 四大交响曲社交媒体演示视频
- 编写 scripts/showcase_choreography.py 与 scripts/render_social_showcase_1080p60.py，生成精确同步的 120.00 秒（60.0 fps 共 7,200 帧，1920x1080）展示视频（showcase-1080p60.mp4）、48 kHz 立体声母带（evidence/social_showcase_1974_symphonies_48k.wav）、.srt 字幕与社交媒体文案：
  - 0:00-0:30（第一乐章：贝多芬《c 小调第五交响曲“命运”》Op. 67）：镜头特写实时插接跳线（VCO 1 + VCO 2 -> VCF、ENV CV -> VCF CUTOFF，共 4 根跳线），演奏命运动机与降 E 大调圆号主题，同时大幅扫频 CUTOFF FREQ（280 Hz -> 7,400 Hz）与 LADDER DRIVE（3.8x）。
  - 0:30-1:00（第二乐章：巴赫《d 小调托卡塔与赋格》BWV 565 / 维瓦尔第《四季·冬》第一乐章）：镜头前实时切换跳线（LFO CV -> VCO PITCH CV、VCF OUT -> DELAY IN，共 5 根跳线），切换簧管/管风琴音色，在 25 键键盘上演绎高速巴洛克十六分音符复调与 BBD 立体声回声。
  - 1:00-1:30（第三乐章：莫扎特《g 小调第四十交响曲》K. 550 + 180g 黑胶混音）：插接 PHONO OUT -> VCF AUDIO IN（5 根跳线），放下 S 型镀铬唱臂以 33 1/3 RPM 播放跟随和弦进行的黑胶伴奏，在 1:14.0 实时拨动转速开关切至 45 RPM（1.35 倍音高与速度）演绎曼海姆火箭琶音桥段，并在 1:24.0 切回 33 1/3 RPM 收束。
  - 1:30-2:00（第四乐章：贝多芬《d 小调第九交响曲“欢乐颂”》Op. 125 终曲）：全机架满配跳线（全部 6 个 [OUT] 插孔同时连接横跨 4 个模块舱 + 黑胶弦乐合唱铺底），从低音提琴圣咏逐步推进至双声部赋格变奏与 Prestissimo 辉煌终曲（CUTOFF 扫频至 11.5 kHz，DRIVE 4.2x）。
- 为当前扫频旋钮配置无视差 3D 双层高亮冠环，在实时插线时同时高亮源插孔与目标插孔，确保所有摄影机预设在顶部 96 px 与底部 216 px 广播字幕栏之间完整构图，并在 4 个并行 Chrome 渲染进程边界执行 30 帧预热以保证琴键行程、唱臂角度与时间码（向下取整至 0.1 秒）在全部 7,200 帧中无缝衔接。
```
