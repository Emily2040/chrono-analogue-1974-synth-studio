<div align="center">

# Chrono Analogue // System 1974

### 演奏可能な 3D 1970年代モジュラー・アナログシンセサイザー、ダイレクトドライブ・アナログターンテーブル・スタジオ ＆ 1080p60 四大交響曲パフォーマンスエンジン

**[English](./README.md)** · **[简体中文](./README.zh-CN.md)** · **[日本語](./README.ja.md)** · **[한국어](./README.ko.md)**

*制作・公開：**[@Iamemily2050](https://x.com/Iamemily2050)** (**[@Emily2040](https://github.com/Emily2040)**) — Google Antigravity 上で **Gemini 4 Argon** が設計・3Dモデリング・音響合成・検証・1080p60映像レンダリングまで一貫して構築。*

</div>

<!-- SHOWCASE_VIDEO -->
<p align="center">
  <a href="https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/download/v1.0.0/showcase-1080p60.mp4">
    <img src="./evidence/captures/showcase_preview.webp" width="100%" alt="Chrono Analogue System 1974 — 1080p60 四大交響曲ショーケース映像プレビュー（クリックして 48 kHz ステレオ音声付き 2分間 1080p60 フル映像を再生・ダウンロード）" />
  </a>
</p>

<p align="center">
  <a href="https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/download/v1.0.0/showcase-1080p60.mp4"><strong>▶ 2分間 1080p60 フルHD映像（音声付き）を再生・ダウンロード (MP4, 62 MB)</strong></a>
  ·
  <a href="https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/download/v1.0.0/social_showcase_1974_symphonies_1080p60.mp4">高ビットレート・マスター (221 MB)</a>
  ·
  <a href="https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/download/v1.0.0/social_showcase_1974_symphonies_48k.wav">48 kHz ステレオ WAV</a>
  ·
  <a href="https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/download/v1.0.0/social_showcase_1974_symphonies.srt">字幕ファイル (.srt)</a>
</p>

---

## 📋 統合ワンショット自然言語マスタープロンプト（コピー＆ペースト用）

> 🌐 **ご希望の言語でマスタープロンプトを閲覧・コピーできます：**
> **[English](./prompts/en.md)** · **[简体中文](./prompts/zh-CN.md)** · **[日本語](./prompts/ja.md)** · **[한국어](./prompts/ko.md)** · **[初期プロンプト＆5段階セッション原文](./prompts/original-brief.en.txt)**

途中の5段階にわたるデバッグやUI・マテリアル改修をやり直すことなく、1回のプロンプト実行で本プロジェクトの最終完成形（3Dインタラクティブ・スタジオと2分間 1080p60 四大交響曲ショーケース映像）をそのまま構築したい場合は、以下の日本語プロンプトを Google Antigravity の **Gemini 4 Argon**（またはヘッドレス Blender・Python・Chrome・FFmpeg が利用可能なエージェント環境）にコピー＆ペーストしてください：

```markdown
ヘッドレス Blender Python（`bpy`）による編集可能な 3D アセット生成、AI 画像生成（Nano Banana）＋Python プロシージャル合成による 16枚の 2048×2048 PBR テクスチャライブラリ、Three.js（`r165`）による 60 FPS 物理ベース・ブラウザインタラクション、Web Audio API によるリアルタイム音響合成とレコード再生を統合し、実際に演奏可能なフォトリアル 3D 1974年製モジュラー・アナログシンセサイザー＆ダイレクトドライブ・ターンテーブル・スタジオ（「Chrono Analogue // System 1974」）を構築してください。さらに、このスタジオを通して4つのクラシック交響曲を演奏する 2分間（120.0秒、7,200フレーム）のフルHD 1920×1080 @ 60 fps ソーシャルメディア向けショーケース映像をレンダリングしてください。

### 1. スキーマ検証済みの3つの共有アーキテクチャ記録
プロジェクトルートに以下の3つの同期された JSON 記録を維持し、フロントエンド検証用に `public/` にもミラーリングしてください：
1. `contract.json`：
   - 基準単位 `source_unit_meters = 0.1`、ラック幅 `rack_width_meters = 0.8`、パネル後傾角 `rack_backward_tilt_degrees = 15.0`。
   - Blender 座標系（`+X` 右、`+Y` 奥、`+Z` 上）から Three.js 座標系（`+X` 右、`+Y` 上、`+Z` 手前）への変換 `(x, y, z) -> (x, z, -y)`。
   - 各コントロールの正確な回転軸とパラメータ範囲：
     - **16個のフルート加工ベークライト・ノブ**（パネル法線ローカル `+Z` 軸周りに `-150°` 〜 `+150°` 回転）：`Knob_VCO1_Wave`、`Knob_VCO1_Tune`、`Knob_VCO1_Octave`、`Knob_VCO2_Wave`、`Knob_VCO2_Detune`、`Knob_VCO_Mix`、`Knob_Noise_Level`、`Knob_VCF_Cutoff`、`Knob_VCF_Resonance`、`Knob_VCF_Drive`、`Knob_VCF_EnvMod`、`Knob_ENV_Attack`、`Knob_ENV_Decay`、`Knob_ENV_Sustain`、`Knob_ENV_Release`、`Knob_LFO_Rate`、`Knob_LFO_Depth`、`Knob_Delay_Time`、`Knob_Delay_Feedback`、`Knob_Delay_Mix`、`Knob_Master_Gain`。
     - **12個の機能的 3.5 mm パッチソケット**（出力 `8` 系統：`VCO1_Out`、`VCO2_Out`、`Mixer_Out`、`Noise_Out`、`VCF_Out`、`ENV_Out`、`LFO_Out`、`SampleHold_Out` ／ 入力 `4` 系統：`VCO_Pitch_CV_In`、`VCF_Audio_In`、`VCF_Cutoff_CV_In`、`VCA_Audio_In`、`VCA_CV_In`、`Delay_Audio_In`）および非互換ソケット接続の拒否ロジック。
     - **25個のスプリング復帰式ヒンジ鍵盤**（`Key_00_C3` 〜 `Key_24_C5`、MIDI `48` 〜 `72`、後端ローカル `+X` 軸ヒンジ周りに `+4.5°` 回転）。
     - **ターンテーブル機構**：`Turntable_Platter`（`33⅓` および `45 RPM` での `-Y` 軸連続回転）、`Vinyl_Record_Disc`、`Tonearm_Gimbal`（レスト位置 `0°` 〜 内周グルーヴ `-24°` ヨー角、キューアップ `0°` 〜 再生降下角 `2.0°`）、`Turntable_Play_Switch`、`Turntable_Speed_Switch`。
2. `world.json`：
   - 全64個の名前付きエンティティ、親子階層、座標変換、マテリアル割り当て、5つのカメラプリセット（`opening_studio`、`synth_rack_closeup`、`patch_and_keys`、`turntable_closeup`、`side_profile_tilt`）、およびデフォルトの6本のパッチケーブル定義。
3. `progress.json`：
   - マイルストーン進捗、パフォーマンス計測値、検証エビデンスのファイルパス。

### 2. ヘッドレス Blender 3D アセット生成＆ルシアー仕様の木目 UV 規則（`scripts/build_studio_assets.py`）
再実行可能なヘッドレス Blender Python スクリプトを作成し、`public/assets/models/studio_scene.glb` と `public/assets/models/calibration_knob.glb` を出力してください：
- **シンセサイザー・ラック**：幅 0.80 m・後傾 `15.0°` のアメリカン・ブラックウォールナット筐体、4枚のダークチャコール・アルマイト加工アルミモジュールパネル（`VCO BANK`、`24 dB/OCT LADDER VCF`、`ADSR / LFO / VCA`、`BBD CHORUS DELAY + MASTER`）、クリーム色のインジケーターインレイとヘアラインアルミスカートを備えた16個のベークライト・ノブ、ワッシャーカラー付き12個の六角ナットソケット、および白鍵のウォーターフォール・リップと黒鍵の3面テーパー面取りを造形した25鍵マニュアル（`C3–C5`）。
- **ダイレクトドライブ・ターンテーブル**：ラック左隣（`X = -0.78 m`）に配置。ヘアライン・ガンメタルデッキプレート、240セグメント・2トラックの面取りストロボプラッターリム（上下各 `120` 個のストロボ歯）、オレンジ色のプリズム・ストロボイルミネーター塔（`#ff5a1f`）、アルミ削り出し 45 RPM センターアダプター、カスタムレーベル付き 180g 黒ビニール LP、S字クローム管トーンアーム、スリット入りダイキャスト・ヘッドシェル、キューイングレバー、アンチスケートダイヤル、カウンターウェイト、ロッカースイッチを造形。
- **ルシアー仕様の長軸木目 UV 整列（重要）**：すべてのウォールナット板材について、幾何学的な最長辺を木目繊維の水平 `U` 軸に自動整列（`align_luthier_wood_uvs`）し、部材ごとに UV オフセットをずらすことで、水平レールに不自然な縦木目が出たり側板に明るい縦筋アーティファクトが出たりするのを防いでください。

### 3. 16枚の 2048×2048 PBR マテリアルライブラリ（`scripts/prepare_textures.py`）
`public/assets/textures/` に以下の16枚のテクスチャを生成・検証してください：
- オイル仕上げアメリカン・ブラックウォールナット（`walnut_wood_grain.png`、`walnut_wood_normal.png`、`walnut_wood_roughness.png`）。
- ダークチャコール・アルマイト加工アルミパネル（`synth_faceplate_albedo.png`、`synth_faceplate_normal.png`、`synth_faceplate_roughness.png`）：ウォームクリーム色（`#f5ebd6`）の高コントラストな目盛り、モジュール枠、太字ラベル付き。
- ターンテーブル用ヘアライン・ガンメタルデッキ（`turntable_deck_albedo.png`、`turntable_deck_normal.png`、`turntable_deck_roughness.png`）。
- 180g レコード盤の同心円マイクログルーヴ法線＆放射状ラフネス（`vinyl_grooves_normal.png`、`vinyl_label_albedo.png`、`vinyl_sleeve_art.png`）。
- ダークエスプレッソ・ペブルグレインレザーのスタジオデスク（`studio_desk_albedo.png`、`studio_desk_normal.png`、`studio_desk_roughness.png`）およびハードウェア HUD スキン（`ui_hardware_console_skin.png`）。

### 4. フォトリアル 60 FPS Three.js スタジオ＆カスタム暗天井 PMREM ライティング（`public/src/studio-app.js`）
- **ブラーなし 60 FPS ハードウェア HUD**：HUD バーには CSS の `backdrop-filter: blur()` を絶対に使用しないでください（GPU リードバックによる深刻なフレームレート低下を防ぐため）。上部コンソールバーと下部ステータスバーは不透明なヘアライン金属ハードウェアストリップとしてスタイリングし、`>= 60 FPS` を維持してください。
- **カスタム 1974年式ダークシーリング・スタジオ PMREM 環境マップ**：Three.js 標準の `RoomEnvironment()` は使用しないでください（真上の白い天井ボックスが水平な黒レコード盤やレザーデスクを白っぽく霞ませるため）。暗い吸音天井（`#050507`）と3つの暖色アンバー／寒色リム・ソフトボックスを備えた独自の正距円筒図法スタジオ PMREM テクスチャを生成し、180g ビニール盤の漆黒のツヤと鋭い2色異方性グルーヴ反射を両立させてください。
- **連続したスタジオ建築背景**：幅広のウォールナット音響スラット背面壁（`X = -1.65 m` 〜 `+1.35 m`）と水平腰壁レール（`Y = 0.25 m`）を構築し、どのカメラプリセットでも端の背景欠けが生じないようにしてください。
- **ソケット列間コリドーを通るパッチケーブル配線**：同一ベイ内のケーブルは自然な懸垂線で垂らし、ベイを跨ぐ長距離ケーブル（`|ΔX| > 0.14 m`）は前方へ持ち上げたコリドー（ラック空間 `Z = +0.055 m`）を通し、上段ソケット列と下段ソケット列の間の水平チャネルに沿って綺麗にアーチを描くことで、ソケット穴やラベルを絶対に塞がないようにしてください。同一ソケットに複数ケーブルが刺さる場合はソケット法線方向に同軸スタック（1段あたり `18 mm`）してください。

### 5. リアルタイム Web Audio シンセサイザー＆ターンテーブル音響エンジン（`public/src/audio-engine.js`）
- モジュラー Web Audio グラフ（`VCO 1`、`VCO 2`、ノイズ、ミキサー、ウェーブシェイパー・サチュレーション付き `24 dB/oct レゾナント・ラダー VCF`、`ADSR エンベロープ`、`LFO`、`VCA`、`ステレオ BBD ディレイ`、`マスターアナライザー`）を実装し、パッチケーブルの着脱が実際のオーディオ／CV ノード接続を動的に変更するようにしてください。
- `33⅓ RPM`（`1.0×`）と `45 RPM`（`1.35×`）の切り替え時に再生位相を維持したままプラッター角速度とピッチ・テンポが連動するターンテーブル再生エンジンと、針先接触時の繊細なビニール・クラックルノイズを実装してください。
- `resetStudio()`、プリセット切り替え、ウィンドウのフォーカス喪失時にすべての発音ボイスを確実に解放し、音の鳴りっぱなしやクリッピング（`peak < 0.96`）を防止してください。

### 6. 自動検証ゲート＆ 2分間 1080p60 四大交響曲ショーケース映像
1. ヘッドレス Chrome 自動検証スイート（`scripts/verify_and_capture_rev3.py` および `scripts/verify_browser_audio_and_interactions.mjs`）を実行し、`world.json` の `64/64` エンティティ一致、16ノブ、12ソケット、25鍵盤、コンソールエラー `0`、`>= 55 FPS`、パッチ変調によるスペクトル変化、ターンテーブル速度比を検証し、全5カメラプリセットのスクリーンショットを保存してください。
2. サンプル精度の 48 kHz ステレオ音声とともに、スタジオを通して4つのクラシック交響曲（各30秒）を演奏する 2分間（`120.00秒`、`7,200` フレーム）フルHD `1920×1080 @ 60.0 fps` ショーケース映像（`showcase-1080p60.mp4`）を生成してください：
   - `0:00–0:30`：ベートーヴェン — 交響曲第5番 ハ短調 Op. 67（*Allegro con brio*）
   - `0:30–1:00`：J.S.バッハ（*トッカータとフーガ ニ短調 BWV 565*）＆ ヴィヴァルディ（*『冬』第1楽章*）
   - `1:00–1:30`：モーツァルト — 交響曲第40番 ト短調 K. 550（*Molto allegro*）＋ `33⅓ ↔ 45 RPM` ライブ・ターンテーブル伴奏
   - `1:30–2:00`：ベートーヴェン — 交響曲第9番 ニ短調 Op. 125（*『歓喜の歌』フィナーレ*）全6ケーブル・フルラック・クライマックス
   決定論的フレームステップ・カメラワーク（`window.__advanceShowcaseFrame(dt)`）、ライブケーブル差し替えアニメーション、ノブスイープ、打鍵アニメーション、放送品質のローワーサード字幕、`.srt` 字幕ファイル、抽出フレーム検証を含めてください。
```

---

## 🎼 1974年製モジュラーシンセとダイレクトドライブ・ターンテーブルによる四大クラシック交響曲の実演（`0:00 – 2:00`）

このショーケース映像では、スタジオ内のポリフォニック・アナログシンセサイザー・グラフとダイレクトドライブ・ターンテーブルを駆使し、4つのクラシック交響曲（各30秒）を連続演奏します。カメラの前で行われるパッチケーブルのリアルタイム抜き差し、ノブによるフィルタースイープ、25鍵キーボードの打鍵アニメーション、そして `33⅓ ↔ 45 RPM` のレコード回転数切り替えをすべて実演しています。

| 第1楽章（`0:00 – 0:30`） | 第2楽章（`0:30 – 1:00`） |
| :---: | :---: |
| <a href="https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/download/v1.0.0/showcase-1080p60.mp4"><img src="./evidence/captures/mp4_verify_mov1_01s4.png" width="100%" alt="第1楽章：ベートーヴェン 交響曲第5番 ハ短調 作品67『運命』" /></a> | <a href="https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/download/v1.0.0/showcase-1080p60.mp4"><img src="./evidence/captures/mp4_verify_mov2_45s0.png" width="100%" alt="第2楽章：J.S.バッハ BWV 565 ＆ ヴィヴァルディ『冬』" /></a> |
| **ベートーヴェン：交響曲第5番 ハ短調 Op. 67『運命』（*Allegro con brio*）**<br/>デチューンしたデュアル・ノコギリ波オシレーター（`VCO 1 + VCO 2 → VCF → VCA`）で「運命の動機」を奏で、`ENV CV OUT → VCF CUTOFF CV` をライブパッチング。24 dB/oct ラダーフィルターを `280 Hz` から `7.4 kHz` までサチュレーション・ドライブとともにスイープします。 | **J.S.バッハ（*BWV 565*）＆ ヴィヴァルディ（『四季』より「冬」*RV 297*）：*バロック・ストーム***<br/>カメラ前でパッチケーブルを切り替え（`LFO CV OUT → VCO PITCH CV` および `VCF OUT → DELAY IN`）、25鍵マニュアル（`C3–C5`）による高速バロック対位法アルペジオと 310 ms BBD ステレオディレイを響かせます。 |
| **第3楽章（`1:00 – 1:30`）** | **第4楽章（`1:30 – 2:00`）** |
| <a href="https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/download/v1.0.0/showcase-1080p60.mp4"><img src="./evidence/captures/mp4_verify_mov3_75s5.png" width="100%" alt="第3楽章：モーツァルト 交響曲第40番 ト短調 K. 550" /></a> | <a href="https://github.com/Emily2040/chrono-analogue-1974-synth-studio/releases/download/v1.0.0/showcase-1080p60.mp4"><img src="./evidence/captures/mp4_verify_mov4_114s5.png" width="100%" alt="第4楽章：ベートーヴェン 交響曲第9番『歓喜の歌』フィナーレ" /></a> |
| **モーツァルト：交響曲第40番 ト短調 K. 550（*Molto allegro*）**<br/>歯切れの良い ADSR フィルター・プラック（`Attack 5 ms`、`Decay 180 ms`、`Sustain 0.22`）を鳴らしながら、S字クローム・トーンアームを回転する 180g 重量盤 LP に降ろし、`33⅓ RPM` と `45 RPM` をリアルタイムに切り替えながらアンサンブルを重ねます。 | **ベートーヴェン：交響曲第9番 ニ短調 Op. 125（*『歓喜の歌』フィナーレ*）**<br/>全4ベイにわたる6本の編組パッチケーブルすべてを接続したフルラック構成にターンテーブル伴奏を重ね、レゾナンス、エンベロープ深さ、ステレオディレイ・ミックスをクライマックスの5声対位法フィナーレへと押し上げます。 |

### スタジオ・ハードウェアのディテール（Revision 4 検証済みキャプチャ）

| モジュラーラック ＆ 4ベイ・シルクスクリーンパネル | 編組パッチケーブル ＆ 25鍵スカルプト・キーボード |
| :---: | :---: |
| <img src="./evidence/captures/rev4_synth_rack_closeup.png" width="100%" alt="モジュラーシンセ・ラック クローズアップ" /> | <img src="./evidence/captures/rev4_patch_and_keys.png" width="100%" alt="パッチベイ＆25鍵キーボード クローズアップ" /> |
| **ダイレクトドライブ・ストロボターンテーブル ＆ S字トーンアーム** | **15° 後傾アメリカン・ブラックウォールナット筐体プロファイル** |
| <img src="./evidence/captures/rev4_turntable_closeup.png" width="100%" alt="ダイレクトドライブ・ターンテーブル クローズアップ" /> | <img src="./evidence/captures/rev4_side_profile_tilt.png" width="100%" alt="15度チルト・サイドプロファイル" /> |

---

## 🎛️ プロジェクト概要

**Chrono Analogue // System 1974** は、Google Antigravity 上で **Gemini 4 Argon** を用いて構築した、実際にブラウザ上で演奏・パッチングできる 1970年代のモジュラー・アナログシンセサイザー＆ダイレクトドライブ・ターンテーブル・スタジオです。ヘッドレス **Blender 5.2 Python (`bpy`)** によるプロシージャル 3D アセット生成、**Nano Banana** と決定論的 Python スクリプトによる 16枚の PBR マテリアル合成、**60 FPS** 固定の **Three.js (`r165`)** 物理ベースレンダリング、リアルタイム **Web Audio API** モジュラー音響グラフ、そして決定論的 **1080p60** 交響曲映像レンダラーを統合しています。

画面上のすべてのコントロールは、スキーマ検証済みの設計契約（[`contract.json`](./contract.json) および [`world.json`](./world.json)）によって厳密に定義されています。

1. **64個のアドレス可能なシーンエンティティ（`world.json`）**：
   - **16個のフルート加工ベークライト・ノブ**：パネル法線ローカル $+Z$ 軸を中心に `-150°` から `+150°` まで滑らかに回転し、指数／線形パラメータマッピングと `12 ms` の `setTargetAtTime` スムージングによりクリックノイズのない音色変化を実現します。
   - **12個の六角ナット付き 3.5 mm パッチソケット**（出力 `8` 系統：`VCO1_Out`、`VCO2_Out`、`Mixer_Out`、`Noise_Out`、`VCF_Out`、`ENV_Out`、`LFO_Out`、`SampleHold_Out` ／ 入力 `4` 系統：`VCO_Pitch_CV_In`、`VCF_Audio_In`、`VCF_Cutoff_CV_In`、`VCA_Audio_In`、`VCA_CV_In`、`Delay_Audio_In`）：パッチケーブルの抜き差しに応じて Web Audio の音声・CV ルーティングをリアルタイムに書き換えます。
   - **25個のヒンジ付き鍵盤メッシュ（`Key_00_C3` 〜 `Key_24_C5`）**：フロントリップを造形した白鍵15個と、テーパー面取りを施した黒檀調の黒鍵10個が後端の $+X$ 軸ヒンジを中心に回転し、スプリング復帰します。マウスドラッグ、QWERTY キーボード（`Z–M` および `Q–I`）、Web MIDI に対応しています。
   - **ダイレクトドライブ・ストロボターンテーブル（`Turntable_Platter`、`Vinyl_Record_Disc`、`Tonearm_Gimbal`、`Turntable_Play_Switch`、`Turntable_Speed_Switch`）**：240セグメント・2トラックの面取りストロボプラッターリム、オレンジ色プリズム・ストロボイルミネーター塔（`#ff5a1f`）、アルミ削り出し 45 RPM アダプターパック、S字クローム・トーンアーム（再生時 `2.0°` 降下）、および `33⅓ RPM`（`1.000×`）と `45 RPM`（`1.350×`）の位相連続ピッチ・テンポ連動再生に対応しています。
2. **契約駆動の決定論的リビルド**：
   - チャット履歴に一切頼ることなく、[`contract.json`](./contract.json) と [`world.json`](./world.json) からパイプラインスクリプトを実行するだけで、全16枚の PBR テクスチャ再生成、マルチノード GLB モデル（`studio_scene.glb` と `calibration_knob.glb`）のエクスポート、ヘッドレス Chrome による全64エンティティの自動検証、および 1080p60 ショーケース映像のレンダリングを完全に再現できます。

---

## 🧪 5段階のエンジニアリング改善プロセス（初期プロトタイプから 60 FPS フォトリアル完成形へ）

本リポジトリでは、初期プロンプトから最終完成形に至るまでに発見されたすべての課題とその解決策を公開し、それらを上記の**統合ワンショット自然言語マスタープロンプト**に凝縮しました。これにより、途中のデバッグ工程を繰り返すことなく、1回のプロンプト入力で最終形（Revision 4）を再現できます。

| ステージ | 発生した課題・視覚／性能上の欠陥 | 根本原因 | 適用したアーキテクチャ解決策（マスタープロンプトに統合済み） |
| :--- | :--- | :--- | :--- |
| **Stage 1：パイプライン構築＆スキーマ契約** | [`contract.json`](./contract.json)（`0.1 m` 単位、`0.8 m` ラック幅、`15°` 後傾、Blender $(X,Y,Z) \to$ Three.js $(X,Z,-Y)$ 変換）を定義し、ヘッドレス Blender 5.2 $\to$ GLB $\to$ Three.js $\to$ Web Audio のループを検証。 | — | 決定論的 `bpy` アセット生成スクリプト [`scripts/build_studio_assets.py`](./scripts/build_studio_assets.py) を構築し、[`scripts/verify_and_capture_rev3.py`](./scripts/verify_and_capture_rev3.py) で `64/64` エンティティの一致を確認。 |
| **Stage 2：Revision 1 の視覚・UX 欠陥の修正** | 独立ビジュアル批評（`gravitas-visual-critic`）で3つの問題が判明：<br/>1. 上部 HUD バーがウォールナット筐体の上端と重なる。<br/>2. 鍵盤が単調な直方体に見える。<br/>3. レコード盤に同心円グルーヴの異方性反射がない。 | 1. カメラターゲットが上部バーの余白を考慮していなかった。<br/>2. 白鍵のフロントリップや黒鍵のテーパー面取りがなかった。<br/>3. レコードが一様なラフネス値だった。 | 1. ハードウェア調のトップコンソールバーを画面上部にドッキングし、カメラ注視点を調整。<br/>2. 白鍵のウォーターフォール・リップと黒鍵の3面テーパー面取りを造形。<br/>3. `2048×2048` の同心円マイクログルーヴ法線マップ（`vinyl_grooves_normal.png`）と放射状ラフネスマップを生成。 |
| **Stage 3：18.8 FPS のボトルネック解消＆「PS1 デモ感」の払拭** | 初期ブラウザ描画は `18.8 FPS` と重く、マテリアルも平坦（「PS1時代のデモのよう」）だった。 | CSS の `backdrop-filter: blur()` によるすりガラス HUD が Chrome の GPU コンポジタで毎フレーム重いリードバックを引き起こしていた。また、単一テクスチャで微細な凹凸が不足していた。 | `backdrop-filter: blur()` を完全撤廃し、不透明なヘアライン黒ブロンズ・ハードウェアスキン（`ui_hardware_console_skin.png`）へ刷新することで、**フレームレートが `18.8 FPS` から `60.1 FPS`（`16.6 ms`）へ劇的に向上**。さらに [`scripts/prepare_textures.py`](./scripts/prepare_textures.py) で **16枚の `2048×2048` PBR テクスチャ群**を合成。 |
| **Stage 4：フォトリアリズムを阻む4大要因の解決（Revision 4）** | Revision 3 の詳細検証で4つの課題を発見：<br/>1. 黒い 180g レコード盤とレザーデスクが白っぽく霞む。<br/>2. ウォールナット横桟の木目が縦方向の板目切れになる。<br/>3. ベイを跨ぐ緑のパッチケーブル（`VCF OUT → DELAY IN`）が中段ソケットを塞ぐ。<br/>4. ターンテーブル接写の左端に背景の隙間が見える。 | 1. Three.js 標準の `RoomEnvironment()` は真上に巨大な白い天井光源を持つため、水平面が白飛びする。<br/>2. 単純な Box UV 投影が板の長手方向を考慮していなかった。<br/>3. 単純な懸垂線がソケット列の干渉を避けていなかった。<br/>4. 背面スラット壁の横幅が不足していた。 | 1. `RoomEnvironment()` を廃止し、**1974年式ダークシーリング・スタジオソフトボックス PMREM 環境マップ**（`buildStudioEnvironmentMap()`）を独自実装し、漆黒のビニール盤と鋭い2色異方性ハイライトを両立。<br/>2. **弦楽器職人（ルシアー）仕様の長軸木目 UV 整列**（`align_luthier_wood_uvs`）と 240セグメント・2トラック・ストロボプラッターを実装。<br/>3. **上下ソケット列間コリドー配線**（`Z = +0.055 m` アーチ）と同軸スタックプラグを導入。<br/>4. ウォールナット音響スラット背面壁を `X = -1.65 m 〜 +1.35 m` に拡張。 |
| **Stage 5：2分間 1080p60 四大交響曲ショーケース映像レンダリング** | 4つの交響曲を演奏しながらケーブル切り替え、ノブ操作、打鍵、レコード回転数変更、字幕表示を行う 2分間（`7,200` フレーム）フルHD 60fps 映像が必要。 | リアルタイム画面録画ではフレーム落ちや音ズレが発生しやすい。 | サンプル精度の 48 kHz ステレオ交響曲シンセ＆レコード音響エンジン（[`scripts/showcase_choreography.py`](./scripts/showcase_choreography.py)）と、`Δt = 1/60 s` 固定ステップ WebGL-to-FFmpeg レンダラー（[`scripts/render_social_showcase_1080p60.py`](./scripts/render_social_showcase_1080p60.py)）を構築。 |

---

## 🏗️ コードベース構成

```text
chrono-analogue-1974-synth-studio/
├── showcase-1080p60.mp4               # 2分間 フルHD 1920x1080 @ 60fps 四大交響曲ショーケース映像（48kHz ステレオ音声付き）
├── contract.json                      # 共有設計契約：基準単位(0.1m)、15°後傾、16ノブ、12ソケット、25鍵盤、ターンテーブル仕様
├── world.json                         # 永続シーングラフ：全64エンティティ、座標変換、5カメラプリセット、デフォルト6パッチケーブル
├── progress.json                      # マイルストーン台帳、ベンチマーク計測値（60.1 FPS）、検証エビデンスパス
├── blender/
│   ├── studio_scene.blend             # 編集可能な Blender 5.2 フルシーンファイル
│   └── calibration_knob.blend         # Stage 1 キャリブレーション用ノブ Blender ソース
├── scripts/
│   ├── build_studio_assets.py         # ヘッドレス Blender 5.2 Python 生成スクリプト（studio_scene.glb & studio_scene.blend）
│   ├── build_calibration_knob.py      # Stage 1 キャリブレーション用ノブ GLB エクスポーター
│   ├── prepare_textures.py            # 全16枚の 2048x2048 アルベド・法線・ラフネス・マイクログルーヴ PBR マップ合成
│   ├── generate_record_audio.py       # インタラクティブ・ターンテーブル再生用 44.1kHz ステレオ WAV 生成
│   ├── verify_and_capture_rev3.py     # ヘッドレス Chrome + WebGL2 自動検証ゲート＆5カメラ・スクリーンショット撮影
│   ├── verify_browser_audio_and_interactions.mjs # Web Audio ＆インタラクション自動検証ランナー
│   ├── showcase_choreography.py       # 120.0秒 48kHz ステレオ四大交響曲 WAV マスター＆イベントタイムライン生成
│   └── render_social_showcase_1080p60.py # 決定論的 7,200フレーム 1080p60 WebGL フレームステッパー＋FFmpeg H.264/AAC マルチプレクサ
├── public/
│   ├── index.html                     # ハードウェア調スタジオ UI シェル、プリセット、カメラ切替、オシロスコープ、パッチツールバー
│   ├── styles.css                     # ブラーなし高速ハードウェアコンソール CSS（60.1 FPS）
│   ├── src/
│   │   ├── studio-app.js              # Three.js r165 シーンローダー、カスタム1974暗天井 PMREM、コリドー配線、ショーケースモード
│   │   └── audio-engine.js            # モジュラー Web Audio API シンセグラフ＋位相連続 33⅓ & 45 RPM ターンテーブルエンジン
│   └── assets/
│       ├── models/                    # エクスポートされたマルチノード GLB（studio_scene.glb, calibration_knob.glb）
│       ├── textures/                  # 16枚の 2048x2048 PBR テクスチャマップ
│       └── audio/                     # 生成されたレコード溝 WAV オーディオ
├── prompts/
│   ├── README.md                      # 4言語マスタープロンプト＆初期セッション履歴インデックス
│   ├── en.md                          # 英語版 統合ワンショット・マスタープロンプト
│   ├── zh-CN.md                       # 簡体字中国語版 統合ワンショット・マスタープロンプト
│   ├── ja.md                          # 日本語版 統合ワンショット・マスタープロンプト
│   ├── ko.md                          # 韓国語版 統合ワンショット・マスタープロンプト
│   └── original-brief.en.txt          # 開発時の5段階プロンプト原文履歴
└── evidence/
    ├── audio_and_interaction_verification.json # 自動機能・視覚・音響・60.1 FPS ベンチマーク検証レポート
    ├── gravitas_verification_report.md # Gravitas 総合検証＆ショーケース監査レポート
    ├── social_showcase_1974_symphonies.srt # 2分間ショーケース映像用 SubRip 字幕ファイル
    ├── social_media_post_caption.md   # ソーシャルメディア投稿用キャプション＆タイムスタンプ
    └── captures/                      # アニメーション WebP プレビュー、検証済み Rev 4 カメラキャプチャ＋MP4 フレーム抽出検証画像
```

---

## 🚀 実行手順と完全再現ガイド

### 必要環境

- **Python 3.10 以上** および `Pillow`、`numpy`、`scipy`（`pip install pillow numpy scipy`）
- **Node.js 20 以上**（`npm install`）
- **Blender 4.x または 5.x**（ヘッドレス `--background` モードの `Blender 5.2` で検証済み）
- **FFmpeg ＆ FFprobe**（1080p60 ショーケース映像を再レンダリングする場合のみ必要）
- WebGL2 および Web Audio API に対応したモダンブラウザ（Chrome、Edge、Firefox、Safari）

### 1. インタラクティブ 3D スタジオをブラウザで起動する

ローカル HTTP サーバーを起動します：

```bash
python scripts/serve.py
```

ブラウザで **`http://127.0.0.1:8088/`** を開きます：

- 左上のコンソールバーにある **POWER ON / ACTIVATE AUDIO** をクリックして Web Audio コンテキストを有効化します。
- **鍵盤を弾く**：25個の鍵盤（`C3–C5`）をマウスドラッグでグリッサンド／打鍵するか、PC の QWERTY キーボード（下段オクターブ：`Z S X D C V G B H N J M , L . /`、上段オクターブ：`Q 2 W 3 E R 5 T 6 Y 7 U I`）または USB MIDI キーボードで演奏できます。
- **ノブを回す**：16個のベークライト・ノブを上下にドラッグすると、オシレーターのチューニング、波形、24 dB/oct ラダーフィルターのカットオフ周波数（`20 Hz – 16 kHz`）、レゾナンス、サチュレーション・ドライブ、ADSR エンベロープ、LFO 変調、ステレオ BBD ディレイをリアルタイムに操作できます。ノブをダブルクリックすると初期値に戻ります。
- **パッチケーブルを繋ぐ**：トップバーの **PATCH CABLE** をクリック（または出力ソケットをクリックしてから互換性のある入力ソケットをクリック）すると、ラック上に編組パッチケーブルを配線できます。既存のソケットまたは **UNPLUG SELECTED** をクリックするとケーブルが外れ、シグナル経路の変化が即座に音に反映されます。
- **ターンテーブルを操作する**：ターンテーブル上の **PLAY / STOP** ロッカースイッチ（またはトップバーの **TURNTABLE** ボタン）をクリックすると、S字クローム・トーンアームが回転する 180g レコード盤に降りて再生が始まります。**33⅓ / 45 RPM** スイッチを切り替えると、ストロボドットとプラッターの回転速度がレコードのピッチ・テンポと完全に同期して変化します。

### 2. 全 PBR テクスチャと Blender 3D GLB モデルをゼロから再ビルドする

[`contract.json`](./contract.json) と [`world.json`](./world.json) から全16枚の PBR マップ、シルクスクリーンパネル、レコード音声、ヘッドレス Blender GLB モデルを再生成するには、以下を実行します：

```bash
# 1. 全16枚の 2048x2048 アルベド・法線・ラフネス・同心円マイクログルーヴ PBR マップを合成
python scripts/prepare_textures.py

# 2. ヘッドレスモードで Blender を実行し、マルチノード GLB アセットをビルド・出力
blender --background --python scripts/build_studio_assets.py

# 3. ステレオ 44.1 kHz レコード再生用オーディオバッファを生成
python scripts/generate_record_audio.py
```

### 3. 自動検証ゲートを実行する

ヘッドレス Chrome 検証スイートを実行し、全64個の `world.json` エンティティ、ノブ／鍵盤／ケーブル／ターンテーブル操作、Web Audio 出力レベル、FPS 計測、および全5カメラアングルのキャプチャを一括検証します：

```bash
python scripts/verify_and_capture_rev3.py
node scripts/verify_browser_audio_and_interactions.mjs
```

### 4. 2分間 1080p60 四大交響曲ショーケース映像を再レンダリングする

48 kHz ステレオの四大交響曲オーディオマスターを合成し、全 `7,200` フレームを `1920×1080 @ 60.0 fps` でレンダリングして H.264/AAC MP4 にパッケージングします：

```bash
# 1. 120.0秒 48kHz ステレオ四大交響曲 WAV マスターとフレーム精度のアニメーションタイムラインを生成
python scripts/showcase_choreography.py

# 2. Δt = 1/60s で決定論的に 7,200フレーム（1920x1080）を描画し FFmpeg で音声と結合
python scripts/render_social_showcase_1080p60.py
```

---

## 🖥️ ハイエンド・ワークステーション向け推奨事項：Blender パイプラインをさらに深化させる方法

本リポジトリのデフォルト構成は、標準的なハードウェア上でヘッドレス Blender ビルド（`scripts/build_studio_assets.py`）が数秒で完了し、ブラウザ上の WebGL2 で **60.1 FPS** にロックして動作するよう設計されています。もし **NVIDIA RTX 4080 / 4090 / 5090** や **Apple M3 / M4 Max / Ultra** などのワークステーション GPU を搭載した環境で、[`scripts/build_studio_assets.py`](./scripts/build_studio_assets.py) をオフライン映画品質まで引き上げたい場合は、以下の4つの拡張が最も効果的です：

### 1. Cycles GPU マルチバウンス AO・キャビティ・曲率ベイク（4K / 8K UDIM テクスチャ）
- **現在のリアルタイム WebGL 構成**：Python（`scripts/prepare_textures.py`）で決定論的な `2048×2048` PBR マップを生成し、リアルタイムシャドウマップおよびカスタム PMREM スタジオ反射と組み合わせています。
- **ワークステーション GPU での拡張**：Blender のレンダーエンジンを `OPTIX` または `METAL` 対応の `CYCLES`（`bpy.context.scene.render.engine = 'CYCLES'`）に切り替え、筐体ごとに **4096×4096 または 8192×8192 の UDIM テクスチャ**をベイクします。16個のベークライト・ノブのスカート周囲、12個の六角ナットカラー、鍵盤ウェルの奥にマルチバウンス環境オクルージョン（`bake_type='AO'`）をベイクし、さらに Cycles の `Pointiness` ／ベベルシェーダー曲率マスクをベイクして、ダークアルマイトパネルやダイキャスト・ヘッドシェルの角に微細な金属エッジ摩耗表現を加えます。

### 2. ハイポリからローポリへのケージ法線ベイク（刻印レタリング・ローレット加工・ネジ山）
- **現在のリアルタイム WebGL 構成**：プロシージャル法線マップと `64`〜`240` セグメントの面取りジオメトリでフルートノブ、六角ナット、2トラック・ストロボプラッター歯を表現しています。
- **ワークステーション GPU での拡張**：24 GB 以上の VRAM を備えた環境では、`build_studio_assets.py` 内で 500万ポリゴン規模のハイポリ・ブーリアン／スカルプトメッシュを生成します：
  - 4枚のシンセパネルに深さ `0.15 mm` の実ジオメトリ凹刻印レタリングと目盛りをブーリアン加工、
  - クローム・ジャックナット、トーンアーム・カウンターウェイトリング、アンチスケートダイヤルに立体的な綾目ローレット（Diamond Knurling）を造形、
  - 50 Hz / 60 Hz ストロボドットや、スリット入りヘッドシェル内部から覗く銅コイル巻線を造形。
  これらをケージベイクによって **16-bit タンジェント空間法線マップ**としてランタイム用ローポリ GLB に焼き付けることで、WebGL の頂点負荷を増やさずにサブミリ単位の光の引っ掛かりを再現できます。

### 3. Geometry Nodes による立体編組クロスケーブル＆スプリング物理シミュレーション
- **現在のリアルタイム WebGL 構成**：Three.js 内でソケット列間コリドー・スプラインに沿ってチューブメッシュを動的生成し、編組クロス PBR 法線・ラフネスマップを反復適用しています。
- **ワークステーション GPU での拡張**：Blender の **Geometry Nodes（ジオメトリノード）**（`ShaderNodeTexWave` ＋ `Curve to Mesh` による螺旋交差ストランド）を用いて実際の 3D ヘリンボーン編みコットン／ナイロンスリーブと成形ストレインリリーフ・ブーツを生成するか、パネル上のノブにコリジョンケージを設定して Blender の **Cloth / Rigid Body Hook シミュレーション**を実行し、ケーブルの揺れやノブ接触時のたわみをベイクしたヒーローアニメーションを出力できます。

### 4. 32-Bit `.exr` スタジオ HDRI 照明＆オフライン Cycles パストレーシングによる 4K60 マスター映像出力
- **現在のリアルタイム WebGL 構成**：Three.js 内でカスタム暗天井スタジオ PMREM 環境を合成し、決定論的 WebGL フレームステッピングで 7,200フレームの 1080p60 ショーケースをレンダリングしています。
- **ワークステーション GPU での拡張**：`evidence/showcase_timeline.json` のキーフレーム台帳（全ノートイベント、ノブ回転角、ケーブル着脱、プラッター角度）を Blender のフレーム変更ハンドラ（`bpy.app.handlers.frame_change_pre`）に直接読み込ませ、**Cycles GPU パストレーシング**（1フレームあたり `256–512 サンプル` ＋ OptiX Temporal Denoising、`50 mm f/2.0` アナモルフィックレンズの物理被写界深度ボケ、およびレコード溝とヘアラインアルミパネルのネイティブ異方性 BSDF シェーディング）で 7,200フレームのシーケンスをオフラインレンダリングできます。

---

## 📊 自動検証サマリー

[`evidence/audio_and_interaction_verification.json`](./evidence/audio_and_interaction_verification.json) および [`evidence/gravitas_verification_report.md`](./evidence/gravitas_verification_report.md) のすべての自動検証項目がエラーゼロで合格しています：

| 検証ゲート項目 | 結果 | 実測エビデンス |
| :--- | :---: | :--- |
| **`world.json` エンティティ整合性** | **PASS** | `studio_scene.glb` と `calibration_knob.glb` 内の全 `64 / 64` 名前付きノードが完全一致 |
| **インタラクティブ・コントロール** | **PASS** | ノブ `16` 個、パッチソケット `12` 個（出力 `8` ／入力 `4`）、ヒンジ鍵盤 `25` 個（`C3–C5`）、ターンテーブル制御 `4` 系統 |
| **リアルタイム・ブラウザ FPS** | **PASS** | `1600×920` および `1920×1080` 解像度で **`60.1 FPS`**（平均フレーム時間 `16.6 ms`）を達成 |
| **Web Audio 合成＆レコード再生** | **PASS** | 発音時 RMS `0.0689`、フィルタースイープ重心変化 `+612 Hz`、`33⅓ → 45 RPM` 速度比 `1.350×`、ピーク `< 0.92` |
| **1080p60 ショーケース映像マスター** | **PASS** | `1920×1080`、`60/1 fps`、`7,200` フレーム、`120.00 s`、H.264 High (`yuv420p`) + 48 kHz 320 kbps AAC |

---

## 📜 ライセンスとクレジット

- **制作・公開**：**[@Iamemily2050](https://x.com/Iamemily2050)** (**[@Emily2040](https://github.com/Emily2040)**)
- **AI ディレクション＆実装**：Google Antigravity 上で **Gemini 4 Argon** によりエンドツーエンド構築。
- **ライセンス**：[MIT License](./LICENSE) の下で公開されています。ランタイム依存ライブラリについては [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) を参照してください。
