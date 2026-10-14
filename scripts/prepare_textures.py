import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
BRAIN_DIR = Path(r"C:\Users\emily\.gemini\antigravity\brain\a0a136be-abbc-4bec-809e-83ca43e0edbb")
TEX_DIR = ROOT / "public" / "assets" / "textures"
CAP_DIR = ROOT / "evidence" / "captures"


def load_font(size: int, bold: bool = False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\consolab.ttf" if bold else r"C:\Windows\Fonts\consola.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size=size)
    return ImageFont.load_default()


def height_to_normal_map(height_field: np.ndarray, strength: float = 3.0) -> Image.Image:
    """
    Derives a tangent-space normal map strictly from a continuous 2D heightfield [0..1].
    """
    gy, gx = np.gradient(height_field.astype(np.float32))
    nx = -gx * strength
    ny = gy * strength  # OpenGL / glTF +Y up tangent space
    nz = np.ones_like(nx)
    norm = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx /= norm
    ny /= norm
    nz /= norm
    rgb = np.stack([
        np.clip((nx * 0.5 + 0.5) * 255.0, 0, 255),
        np.clip((ny * 0.5 + 0.5) * 255.0, 0, 255),
        np.clip((nz * 0.5 + 0.5) * 255.0, 0, 255),
    ], axis=-1).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB")


def process_nano_banana_assets():
    TEX_DIR.mkdir(parents=True, exist_ok=True)
    CAP_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copy concept exploration images to evidence/captures
    c1 = BRAIN_DIR / "concept_direction_1_walnut_anodised_1791948874934.jpg"
    c2 = BRAIN_DIR / "concept_direction_2_teak_silver_broadcast_1791948897140.jpg"
    if c1.exists():
        Image.open(c1).convert("RGB").save(CAP_DIR / "concept_direction_1_walnut_anodised.png")
    if c2.exists():
        Image.open(c2).convert("RGB").save(CAP_DIR / "concept_direction_2_teak_silver_broadcast.png")

    # 2. Process American black walnut wood grain texture, normal map, and roughness map
    walnut_src = BRAIN_DIR / "walnut_wood_grain_1791948921976.jpg"
    img_walnut = Image.open(walnut_src).convert("RGB").resize((1024, 1024), Image.Resampling.LANCZOS)
    arr_w = np.asarray(img_walnut, dtype=np.float32) / 255.0
    # Flatten any low-frequency lighting gradient while preserving rich wood grain contrast
    blur_w = np.asarray(img_walnut.filter(ImageFilter.GaussianBlur(radius=64)), dtype=np.float32) / 255.0
    mean_color = np.mean(arr_w, axis=(0, 1), keepdims=True)
    even_w = np.clip((arr_w - blur_w + mean_color) * 1.06, 0.02, 1.0)
    # Rich hand-rubbed oiled American black walnut curve (deep chocolate-amber tone)
    even_w = np.power(even_w, 1.18) * np.array([0.92, 0.84, 0.76], dtype=np.float32).reshape((1, 1, 3))
    even_w = np.clip(even_w, 0.03, 0.88)
    img_walnut_even = Image.fromarray((even_w * 255.0).astype(np.uint8), mode="RGB")
    img_walnut_even.save(TEX_DIR / "walnut_wood_grain.png")

    luma = 0.299 * even_w[:, :, 0] + 0.587 * even_w[:, :, 1] + 0.114 * even_w[:, :, 2]
    blurred = np.asarray(img_walnut_even.convert("L").filter(ImageFilter.GaussianBlur(radius=10)), dtype=np.float32) / 255.0
    pore_height = np.clip(0.5 + (luma - blurred) * 2.4, 0.0, 1.0)
    walnut_normal = height_to_normal_map(pore_height, strength=2.6)
    walnut_normal.save(TEX_DIR / "walnut_wood_normal.png")

    # Wood pores have higher roughness (0.52), smooth satin grain flats have lower roughness (0.28)
    walnut_rough = np.clip((0.38 - (luma - blurred) * 0.45) * 255.0, 62, 165).astype(np.uint8)
    Image.fromarray(walnut_rough, mode="L").save(TEX_DIR / "walnut_wood_roughness.png")

    # 3. Process 1974 LP Sleeve Artwork (crop inner border so jacket has no white outer frame)
    sleeve_src = BRAIN_DIR / "vinyl_sleeve_art_1791948951607.jpg"
    img_sleeve = Image.open(sleeve_src).convert("RGB")
    w, h = img_sleeve.size
    margin_x = int(w * 0.045)
    margin_y = int(h * 0.045)
    img_sleeve_cropped = img_sleeve.crop((margin_x, margin_y, w - margin_x, h - margin_y)).resize((1024, 1024), Image.Resampling.LANCZOS)
    img_sleeve_cropped.save(TEX_DIR / "vinyl_sleeve_art.png")

    # 4. Process Nano Banana UI Hardware Console Skin
    ui_skin_src = BRAIN_DIR / "ui_hardware_console_skin_png_1791957150724.jpg"
    if ui_skin_src.exists():
        img_ui = Image.open(ui_skin_src).convert("RGB").resize((1024, 512), Image.Resampling.LANCZOS)
        img_ui.save(TEX_DIR / "ui_hardware_console_skin.png")


def draw_screw_head(draw, draw_r, height_arr, cx, cy, radius=10):
    """Draws a realistic recessed machined stainless rack screw with slot."""
    draw.ellipse([cx - radius - 2, cy - radius - 2, cx + radius + 2, cy + radius + 2], fill=(16, 18, 22))
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(92, 98, 108), outline=(38, 42, 48), width=2)
    draw.line([(cx - radius + 3, cy - 2), (cx + radius - 3, cy + 2)], fill=(28, 30, 35), width=2)
    draw_r.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=62)
    y0, y1 = max(0, cy - radius - 2), min(height_arr.shape[0], cy + radius + 3)
    x0, x1 = max(0, cx - radius - 2), min(height_arr.shape[1], cx + radius + 3)
    for py in range(y0, y1):
        for px in range(x0, x1):
            d = math.hypot(px - cx, py - cy)
            if d <= radius:
                height_arr[py, px] = 0.38
            elif d <= radius + 2:
                height_arr[py, px] = 0.25


def build_synth_faceplate_textures(contract: dict):
    """
    Builds 2048x1024 albedo, roughness, and height-derived normal maps for the 0.80 m x 0.34 m tilted faceplate.
    Integrates Nano Banana brushed black-bronze anodised aluminium texture with razor-sharp silk-screen scales.
    """
    W, H = 2048, 1024
    rng = np.random.default_rng(197401)

    ui_skin_src = BRAIN_DIR / "ui_hardware_console_skin_png_1791957150724.jpg"
    if ui_skin_src.exists():
        skin_img = Image.open(ui_skin_src).convert("L").resize((1024, 1024), Image.Resampling.LANCZOS)
        skin_tile = np.tile(np.asarray(skin_img, dtype=np.float32), (1, 2))
        skin_blur = np.tile(
            np.asarray(skin_img.filter(ImageFilter.GaussianBlur(radius=32)), dtype=np.float32),
            (1, 2)
        )
        grain_detail = (skin_tile - skin_blur) * 0.85
    else:
        grain_detail = np.zeros((H, W), dtype=np.float32)

    # Deep charcoal-black brushed anodised aluminium base (#101215)
    base_rgb = np.zeros((H, W, 3), dtype=np.float32)
    base_rgb[:, :, 0] = 15.0
    base_rgb[:, :, 1] = 17.0
    base_rgb[:, :, 2] = 21.0

    row_noise = rng.normal(0.0, 1.1, size=(H, 1))
    streak = rng.normal(0.0, 1.4, size=(H, W // 8))
    streak_full = np.repeat(streak, 8, axis=1)
    brush = row_noise + streak_full + grain_detail * 0.65
    for c in range(3):
        base_rgb[:, :, c] = np.clip(base_rgb[:, :, c] + brush, 8, 36)

    # Continuous heightfield for normal map (0.5 = flat panel surface)
    height_arr = np.clip(0.5 + brush * 0.007, 0.43, 0.57).astype(np.float32)

    img_albedo = Image.fromarray(base_rgb.astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(img_albedo)

    # Roughness map: base brushed anodised = 122 (~0.48), silk-screen ink = 68 (~0.27)
    rough_arr = np.clip(122.0 - brush * 2.2, 92, 158).astype(np.uint8)
    img_rough = Image.fromarray(rough_arr, mode="L")
    draw_r = ImageDraw.Draw(img_rough)

    # Height mask for silk-screen raised ink & engraved module seams
    ink_mask = Image.new("L", (W, H), 0)
    draw_ink = ImageDraw.Draw(ink_mask)

    cream = (250, 242, 224)
    cream_dim = (214, 204, 184)
    amber_accent = (244, 174, 86)
    cyan_accent = (128, 204, 228)

    font_header = load_font(25, bold=True)
    font_sub = load_font(16, bold=True)
    font_label = load_font(17, bold=True)
    font_tick = load_font(13, bold=True)
    font_jack = load_font(15, bold=True)

    def world_to_px(x_m: float, y_m: float):
        u = (x_m + 0.40) / 0.80
        v = (y_m + 0.17) / 0.34
        return int(round(u * W)), int(round((1.0 - v) * H))

    pad = 18
    draw.rectangle([pad, pad, W - pad, H - pad], outline=cream, width=3)
    draw_r.rectangle([pad, pad, W - pad, H - pad], outline=68, width=3)
    draw_ink.rectangle([pad, pad, W - pad, H - pad], outline=180, width=3)

    _, py_sep = world_to_px(0.0, -0.042)

    module_bounds = [
        (-0.40, -0.20, "VCO BANK • DUAL OSCILLATOR"),
        (-0.20,  0.00, "VCF • 24 dB/OCT LADDER FILTER"),
        ( 0.00,  0.20, "CONTOUR • ADSR ENVELOPE / VCA"),
        ( 0.20,  0.40, "MODULATION LFO & BBD DELAY"),
    ]
    for x0, x1, title in module_bounds:
        px0, _ = world_to_px(x0, 0.0)
        px1, _ = world_to_px(x1, 0.0)
        if x0 > -0.39:
            # Engraved dark seam + cream silk-screen divider line
            draw.line([(px0 - 2, pad), (px0 - 2, H - pad)], fill=(6, 8, 10), width=2)
            draw.line([(px0, pad), (px0, py_sep)], fill=cream, width=3)
            draw_r.line([(px0, pad), (px0, py_sep)], fill=68, width=3)
            draw_ink.line([(px0, pad), (px0, py_sep)], fill=200, width=3)
            height_arr[:, max(0, px0 - 3):min(W, px0 - 1)] = 0.28

        # Corner rack-mount screws for each 1970s Euro/Moog-style module bay
        for sx_px in (px0 + 34, px1 - 34):
            for sy_px in (36, H - 34):
                draw_screw_head(draw, draw_r, height_arr, sx_px, sy_px, radius=9)

        cx = (px0 + px1) // 2
        draw.line([(px0 + 22, 62), (px1 - 22, 62)], fill=cream_dim, width=2)
        draw.text((cx, 38), title, fill=cream, font=font_header, anchor="mm")
        draw_r.text((cx, 38), title, fill=68, font=font_header, anchor="mm")
        draw_ink.text((cx, 38), title, fill=220, font=font_header, anchor="mm")

    draw.line([(pad, py_sep), (W - pad, py_sep)], fill=amber_accent, width=3)
    draw_r.line([(pad, py_sep), (W - pad, py_sep)], fill=68, width=3)
    draw_ink.line([(pad, py_sep), (W - pad, py_sep)], fill=210, width=3)
    draw.rectangle([W // 2 - 275, py_sep - 26, W // 2 + 275, py_sep - 2], fill=(14, 16, 20), outline=amber_accent, width=1)
    draw.text((W // 2, py_sep - 14), "PATCH BAY • HIGH-IMPEDANCE CV & AUDIO MATRIX (3.5mm)", fill=amber_accent, font=font_sub, anchor="mm")
    draw_ink.text((W // 2, py_sep - 14), "PATCH BAY • HIGH-IMPEDANCE CV & AUDIO MATRIX (3.5mm)", fill=210, font=font_sub, anchor="mm")

    # Radial calibration dials, potentiometer shaft washers, and labels for all 16 knobs
    r_inner = 42
    r_tick_maj = 58
    r_tick_min = 51
    for k in contract["knobs"]:
        kx, ky, _ = k["panel_local_pos_m"]
        cx, cy = world_to_px(kx, ky)

        # Machined potentiometer shaft collar washer & dark skirt recess
        draw.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(10, 12, 15), outline=(126, 132, 144), width=3)
        draw.ellipse([cx - 35, cy - 35, cx + 35, cy + 35], outline=(62, 68, 78), width=2)
        draw_r.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=135, outline=54, width=3)

        # Precision arc line connecting ticks
        draw.arc([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], start=135, end=45, fill=cream_dim, width=2)

        num_ticks = 21
        for t_idx in range(num_ticks):
            frac = t_idx / (num_ticks - 1)
            ang_deg = -135.0 + frac * 270.0
            ang_rad = math.radians(ang_deg)
            sx = math.sin(ang_rad)
            sy = -math.cos(ang_rad)
            is_major = (t_idx % 2 == 0)
            r1 = r_inner
            r2 = r_tick_maj if is_major else r_tick_min
            w_line = 3 if is_major else 2
            col = cream if is_major else cream_dim
            draw.line([(cx + sx * r1, cy + sy * r1), (cx + sx * r2, cy + sy * r2)], fill=col, width=w_line)
            draw_r.line([(cx + sx * r1, cy + sy * r1), (cx + sx * r2, cy + sy * r2)], fill=68, width=w_line)
            draw_ink.line([(cx + sx * r1, cy + sy * r1), (cx + sx * r2, cy + sy * r2)], fill=215, width=w_line)

        draw.text((cx - 44, cy + 48), "MIN", fill=cream_dim, font=font_tick, anchor="mm")
        draw.text((cx + 44, cy + 48), "MAX", fill=cream_dim, font=font_tick, anchor="mm")
        draw.text((cx, cy + 72), k["label"], fill=cream, font=font_label, anchor="mm")
        draw_r.text((cx, cy + 72), k["label"], fill=68, font=font_label, anchor="mm")
        draw_ink.text((cx, cy + 72), k["label"], fill=235, font=font_label, anchor="mm")

    # Silk-screened rings & labels for all 12 patch sockets
    for s in contract["patch_sockets"]:
        sx_m, sy_m, _ = s["panel_local_pos_m"]
        cx, cy = world_to_px(sx_m, sy_m)
        is_out = (s["direction"] == "output")
        is_cv = ("cv" in s["port_type"])
        ring_col = cyan_accent if is_cv else (amber_accent if is_out else cream)

        r_ring = 28
        draw.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring], fill=(12, 14, 18), outline=ring_col, width=3)
        draw_r.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring], outline=68, width=3)
        draw_ink.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring], outline=210, width=3)

        badge = "OUT" if is_out else "IN"
        if is_out:
            lbl_y = cy - 42
            badge_y = cy - 62
        else:
            lbl_y = cy + 42
            badge_y = cy + 62
        draw.text((cx, lbl_y), s["label"], fill=cream, font=font_jack, anchor="mm")
        draw.text((cx, badge_y), f"[{badge}]", fill=ring_col, font=font_tick, anchor="mm")
        draw_r.text((cx, lbl_y), s["label"], fill=68, font=font_jack, anchor="mm")
        draw_ink.text((cx, lbl_y), s["label"], fill=225, font=font_jack, anchor="mm")

    ink_arr = np.asarray(ink_mask, dtype=np.float32) / 255.0
    height_arr = np.clip(height_arr + ink_arr * 0.16, 0.0, 1.0)
    normal_img = height_to_normal_map(height_arr, strength=2.4)

    img_albedo.save(TEX_DIR / "synth_faceplate_albedo.png")
    img_rough.save(TEX_DIR / "synth_faceplate_roughness.png")
    normal_img.save(TEX_DIR / "synth_faceplate_normal.png")


def build_turntable_deck_textures(contract: dict):
    """
    Builds 2048x2048 albedo, roughness, and height-derived normal maps for the 0.39 m x 0.32 m
    direct-drive brushed gunmetal aluminium turntable top deck plate.
    """
    W, H = 2048, 2048
    deck_src = BRAIN_DIR / "turntable_deck_base_png_1791957092478.jpg"
    if deck_src.exists():
        raw = Image.open(deck_src).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
        arr = np.asarray(raw, dtype=np.float32) / 255.0
        # Remove low-frequency radial vignette while preserving 100% of brushed metal micro-grain
        blur = np.asarray(raw.filter(ImageFilter.GaussianBlur(radius=96)), dtype=np.float32) / 255.0
        target_base = np.array([0.125, 0.135, 0.155], dtype=np.float32).reshape((1, 1, 3))
        delit = np.clip(target_base + (arr - blur) * 1.15, 0.05, 0.45)
    else:
        rng = np.random.default_rng(197402)
        delit = np.full((H, W, 3), 0.14, dtype=np.float32) + rng.normal(0, 0.015, (H, W, 1))

    luma = 0.299 * delit[:, :, 0] + 0.587 * delit[:, :, 1] + 0.114 * delit[:, :, 2]
    height_arr = np.clip(0.5 + (luma - np.mean(luma)) * 1.3, 0.25, 0.75).astype(np.float32)

    img_albedo = Image.fromarray((delit * 255.0).astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(img_albedo)

    rough_base = np.clip((0.36 - (luma - np.mean(luma)) * 0.55) * 255.0, 58, 138).astype(np.uint8)
    img_rough = Image.fromarray(rough_base, mode="L")
    draw_r = ImageDraw.Draw(img_rough)

    ink_mask = Image.new("L", (W, H), 0)
    draw_ink = ImageDraw.Draw(ink_mask)

    # Deck dimensions in Three.js local Turntable_Root space:
    # X in [-0.195, +0.195] (width 0.39 m), Z_threejs in [-0.160, +0.160] (depth 0.32 m)
    # UV mapping on top face (+Z in Blender): u = (x + 0.195) / 0.39, v = (z_threejs + 0.160) / 0.32
    def deck_to_px(x_m: float, z_three_m: float):
        u = (x_m + 0.195) / 0.39
        v = (z_three_m + 0.160) / 0.32
        return int(round(u * W)), int(round(v * H))

    cream = (248, 240, 220)
    amber = (242, 172, 84)
    dark_well = (14, 16, 20)
    silver_line = (165, 172, 184)

    f_brand = load_font(30, bold=True)
    f_sub = load_font(18, bold=True)
    f_ctrl = load_font(20, bold=True)
    f_small = load_font(16, bold=True)

    # Outer machined bevel hairline border & 4 corner hex screws
    pad = 28
    draw.rectangle([pad, pad, W - pad, H - pad], outline=silver_line, width=3)
    draw_ink.rectangle([pad, pad, W - pad, H - pad], outline=180, width=3)
    for sx in (pad + 36, W - pad - 36):
        for sy in (pad + 36, H - pad - 36):
            draw_screw_head(draw, draw_r, height_arr, sx, sy, radius=14)

    # 1. Recessed circular platter well under Turntable_Platter at [-0.035, 0.0, 0.0]
    px_platter, py_platter = deck_to_px(-0.035, 0.0)
    rx_well = int(round((0.156 / 0.39) * W))
    ry_well = int(round((0.156 / 0.32) * H))
    draw.ellipse(
        [px_platter - rx_well, py_platter - ry_well, px_platter + rx_well, py_platter + ry_well],
        fill=dark_well, outline=silver_line, width=5
    )
    draw_r.ellipse(
        [px_platter - rx_well, py_platter - ry_well, px_platter + rx_well, py_platter + ry_well],
        fill=145, outline=55, width=5
    )

    # 2. Start/Stop button callout ring & label at [-0.145, +0.125]
    px_st, py_st = deck_to_px(-0.145, 0.125)
    draw.ellipse([px_st - 86, py_st - 102, px_st + 86, py_st + 102], outline=cream, width=4)
    draw.text((px_st, py_st + 128), "START / STOP", fill=cream, font=f_ctrl, anchor="mm")
    draw_ink.text((px_st, py_st + 128), "START / STOP", fill=230, font=f_ctrl, anchor="mm")

    # 3. 33 1/3 & 45 RPM speed switch calibration arc & badges at [-0.092, +0.125]
    px_sw, py_sw = deck_to_px(-0.092, 0.125)
    draw.ellipse([px_sw - 74, py_sw - 88, px_sw + 74, py_sw + 88], outline=amber, width=4)
    draw.text((px_sw - 78, py_sw - 82), "33⅓", fill=cream, font=f_ctrl, anchor="mm")
    draw.text((px_sw + 78, py_sw - 82), "45", fill=amber, font=f_ctrl, anchor="mm")
    draw.text((px_sw, py_sw + 128), "SPEED (RPM)", fill=cream, font=f_ctrl, anchor="mm")
    draw_ink.text((px_sw - 78, py_sw - 82), "33⅓", fill=230, font=f_ctrl, anchor="mm")
    draw_ink.text((px_sw + 78, py_sw - 82), "45", fill=230, font=f_ctrl, anchor="mm")
    draw_ink.text((px_sw, py_sw + 128), "SPEED (RPM)", fill=230, font=f_ctrl, anchor="mm")

    # 4. Strobe illuminator callout at [-0.155, +0.075]
    px_stb, py_stb = deck_to_px(-0.155, 0.052)
    draw.text((px_stb, py_stb), "STROBE", fill=amber, font=f_small, anchor="mm")
    draw.text((px_stb, py_stb + 22), "50 / 60 Hz", fill=cream, font=f_small, anchor="mm")

    # 5. Brand & model silk-screened plaque on front-right of deck
    px_br, py_br = deck_to_px(0.088, 0.128)
    draw.rectangle([px_br - 265, py_br - 46, px_br + 265, py_br + 46], fill=(14, 16, 20), outline=amber, width=3)
    draw.text((px_br, py_br - 13), "CHRONO-DRIVE DD-1974", fill=cream, font=f_brand, anchor="mm")
    draw.text((px_br, py_br + 18), "QUARTZ DIRECT-DRIVE TRANSCRIPTION SYSTEM", fill=amber, font=f_sub, anchor="mm")
    draw_ink.rectangle([px_br - 265, py_br - 46, px_br + 265, py_br + 46], outline=220, width=3)
    draw_ink.text((px_br, py_br - 13), "CHRONO-DRIVE DD-1974", fill=230, font=f_brand, anchor="mm")

    # 6. Tonearm gimbal base calibration ring at [+0.135, -0.095]
    px_arm, py_arm = deck_to_px(0.135, -0.095)
    draw.ellipse([px_arm - 145, py_arm - 175, px_arm + 145, py_arm + 175], fill=(16, 18, 22), outline=silver_line, width=4)
    draw.ellipse([px_arm - 115, py_arm - 138, px_arm + 115, py_arm + 138], outline=amber, width=3)
    draw.text((px_arm, py_arm - 200), "GIMBAL SUSPENSION • ANTI-SKATE", fill=cream, font=f_small, anchor="mm")

    ink_arr = np.asarray(ink_mask, dtype=np.float32) / 255.0
    height_arr = np.clip(height_arr + ink_arr * 0.15, 0.0, 1.0)
    normal_img = height_to_normal_map(height_arr, strength=2.2)

    img_albedo.save(TEX_DIR / "turntable_deck_albedo.png")
    img_rough.save(TEX_DIR / "turntable_deck_roughness.png")
    normal_img.save(TEX_DIR / "turntable_deck_normal.png")


def build_studio_desk_textures():
    """
    Builds a 1024x1024 pebble-grain studio console leatherette blotter texture set
    (albedo, roughness, normal) with deep espresso-charcoal absorption so the tabletop
    anchors the walnut instruments without washing out into pale grey.
    """
    N = 1024
    rng = np.random.default_rng(197409)
    n1 = rng.normal(0.0, 1.0, (N // 4, N // 4))
    n1_img = Image.fromarray(((n1 * 0.25 + 0.5) * 255).clip(0, 255).astype(np.uint8), mode="L").resize((N, N), Image.Resampling.BICUBIC)
    n2 = rng.normal(0.0, 1.0, (N // 2, N // 2))
    n2_img = Image.fromarray(((n2 * 0.25 + 0.5) * 255).clip(0, 255).astype(np.uint8), mode="L").resize((N, N), Image.Resampling.BILINEAR)

    h1 = np.asarray(n1_img, dtype=np.float32) / 255.0
    h2 = np.asarray(n2_img, dtype=np.float32) / 255.0
    pebble = np.clip(0.5 + (h1 - 0.5) * 0.8 + (h2 - 0.5) * 0.45, 0.0, 1.0)

    # Deep rich espresso-charcoal studio leatherette (#110e0d)
    rgb = np.zeros((N, N, 3), dtype=np.float32)
    rgb[:, :, 0] = 17.0 + (pebble - 0.5) * 11.0
    rgb[:, :, 1] = 14.0 + (pebble - 0.5) * 9.0
    rgb[:, :, 2] = 13.0 + (pebble - 0.5) * 8.0

    Image.fromarray(np.clip(rgb, 6, 34).astype(np.uint8), mode="RGB").save(TEX_DIR / "studio_desk_albedo.png")
    rough = np.clip((0.72 - (pebble - 0.5) * 0.24) * 255.0, 148, 218).astype(np.uint8)
    Image.fromarray(rough, mode="L").save(TEX_DIR / "studio_desk_roughness.png")
    height_to_normal_map(pebble, strength=2.4).save(TEX_DIR / "studio_desk_normal.png")


def build_vinyl_textures():
    """
    Builds height-derived concentric groove normal map (1024x1024) and jet-black 180g vinyl
    disc + center label albedo (1024x1024).
    """
    N = 1024
    y, x = np.ogrid[-1.0:1.0:N*1j, -1.0:1.0:N*1j]
    r = np.sqrt(x * x + y * y)

    in_groove = (r >= 0.34) & (r <= 0.96)
    groove_wave = (
        0.55 * np.sin(r * 680.0 * math.pi)
        + 0.30 * np.sin(r * 240.0 * math.pi)
        + 0.15 * np.cos(r * 95.0 * math.pi)
    )
    track_lands = (
        np.exp(-((r - 0.50) / 0.007) ** 2)
        + np.exp(-((r - 0.66) / 0.007) ** 2)
        + np.exp(-((r - 0.81) / 0.007) ** 2)
    )
    modulation = np.clip(1.0 - 0.85 * track_lands, 0.08, 1.0)
    height = np.where(in_groove, 0.5 + 0.44 * groove_wave * modulation, 0.5)
    normal_img = height_to_normal_map(height, strength=3.6)
    normal_img.save(TEX_DIR / "vinyl_grooves_normal.png")

    disc_img = Image.new("RGB", (N, N), (4, 4, 6))
    draw = ImageDraw.Draw(disc_img)
    cx, cy = N // 2, N // 2

    for r_px in range(int(N * 0.175), int(N * 0.48), 2):
        c_val = 5 + int(3 * math.sin(r_px * 0.35))
        draw.ellipse([cx - r_px, cy - r_px, cx + r_px, cy + r_px], outline=(c_val, c_val, c_val + 2), width=1)

    r_lbl = 170
    draw.ellipse([cx - r_lbl, cy - r_lbl, cx + r_lbl, cy + r_lbl], fill=(240, 226, 194), outline=(202, 136, 52), width=6)
    draw.ellipse([cx - 142, cy - 142, cx + 142, cy + 142], outline=(32, 78, 86), width=3)
    draw.ellipse([cx - 110, cy - 110, cx + 110, cy + 110], outline=(202, 136, 52), width=2)

    f_title = load_font(20, bold=True)
    f_meta = load_font(14, bold=True)
    f_small = load_font(12, bold=False)

    draw.text((cx, cy - 82), "CHRONO ANALOGUE", fill=(24, 58, 66), font=f_title, anchor="mm")
    draw.text((cx, cy - 58), "LABORATORIES • 1974", fill=(182, 96, 32), font=f_meta, anchor="mm")
    draw.text((cx - 72, cy), "SIDE A", fill=(24, 28, 32), font=f_meta, anchor="mm")
    draw.text((cx + 72, cy), "33⅓ RPM", fill=(24, 28, 32), font=f_meta, anchor="mm")
    draw.text((cx, cy + 56), "KOSMISCHE ETUDE NO. 4", fill=(24, 58, 66), font=f_meta, anchor="mm")
    draw.text((cx, cy + 80), "STEREO • CAL-1974-A", fill=(80, 72, 60), font=f_small, anchor="mm")

    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(200, 205, 212), outline=(40, 40, 45), width=2)
    disc_img.save(TEX_DIR / "vinyl_label_albedo.png")


def main():
    contract = json.loads((ROOT / "contract.json").read_text(encoding="utf-8"))
    process_nano_banana_assets()
    build_synth_faceplate_textures(contract)
    build_turntable_deck_textures(contract)
    build_studio_desk_textures()
    build_vinyl_textures()
    for p in sorted(TEX_DIR.glob("*.png")):
        print(f"TEXTURE READY: {p.name} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
