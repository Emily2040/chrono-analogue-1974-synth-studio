"""
Renders the 1920x1080 Full HD @ locked 60.0 fps (7,200 frames, 120.0s) H.264 MP4 social media showcase video
(`evidence/social_showcase_1974_symphonies_1080p60.mp4`) synchronized to the 48 kHz stereo master audio
(`evidence/social_showcase_1974_symphonies_48k.wav`).

Architecture:
- Uses 4 parallel headless Chrome WebGL2 workers (one per 30-second Symphony Movement = 1,800 frames each).
- Each worker loads http://127.0.0.1:8088/, sets the WebGL renderer to 1920x1080, builds the Three.js
  Orthographic Broadcast HUD + Lower-Third Social Media Caption + Live 60fps Green Phosphor Oscilloscope
  overlay pass (`toneMapped: false`), and steps deterministically through its assigned frames using
  `evidence/showcase_timeline.json`.
- Uses WebGL2 Dual Pixel Buffer Objects (`gl.PIXEL_PACK_BUFFER`) + pipelined binary WebSocket streaming
  into FFmpeg (`libx264 -preset fast -crf 17 -pix_fmt yuv420p -r 60`), then losslessly concatenates
  the 4 movements and muxes the sample-accurate 48 kHz stereo WAV audio track.
"""

import argparse
import base64
import hashlib
import json
import math
import os
import socket
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_and_capture_rev3 import CDPClient, wait_for_cdp_target, CHROME_EXE, STUDIO_URL, ROOT

FFMPEG_EXE = r"C:\Users\emily\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"
FFPROBE_EXE = r"C:\Users\emily\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffprobe.exe"

EVIDENCE_DIR = ROOT / "evidence"
CAPTURES_DIR = EVIDENCE_DIR / "captures"
TIMELINE_JSON = EVIDENCE_DIR / "showcase_timeline.json"
WAV_MASTER = EVIDENCE_DIR / "social_showcase_1974_symphonies_48k.wav"
MP4_MASTER = EVIDENCE_DIR / "social_showcase_1974_symphonies_1080p60.mp4"


# JavaScript injected into each headless Chrome worker to set up the 1920x1080 Broadcast HUD,
# 3D knob/socket highlight rings, animated preview cable, and deterministic frame stepper.
INJECT_SHOWCASE_JS = r"""
window.__initShowcaseRenderer = async function(captions) {
    const THREE = await import('./vendor/three/three.module.js');
    const app = window.studioApp;

    // Pause autonomous requestAnimationFrame rendering so we step deterministically
    app._animate = () => {};

    // Resize WebGL renderer to exact 1920x1080 Full HD (pixelRatio = 1)
    app.renderer.setPixelRatio(1);
    app.renderer.setSize(1920, 1080, false);
    app.renderer.autoClear = false;
    app.camera.aspect = 1920 / 1080;
    app.camera.updateProjectionMatrix();

    // Hide HTML DOM overlays so Page.captureScreenshot (if used for still previews) only sees WebGL canvas
    const topDom = document.querySelector('.hud-top-stack');
    const botDom = document.querySelector('.hud-bottom');
    if (topDom) topDom.style.display = 'none';
    if (botDom) botDom.style.display = 'none';

    // Load brushed hardware skin image for authentic 1974 console HUD cards
    const skinImg = new Image();
    skinImg.src = './assets/textures/ui_hardware_console_skin.png';
    await new Promise((res) => { skinImg.onload = res; skinImg.onerror = res; });

    // Create 3D glowing callout rings on the knob crown (z=0.0194) and mid-fluted collar (z=0.0110)
    // so the highlight stays concentric with the 3D knob body from every camera elevation/tilt angle
    const knobHighlightRing = new THREE.Group();
    const knobCrownRing = new THREE.Mesh(
        new THREE.RingGeometry(0.0102, 0.0126, 48),
        new THREE.MeshBasicMaterial({
            color: 0xffb840,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.95,
            toneMapped: false
        })
    );
    knobCrownRing.position.set(0, 0, 0.0194);
    const knobCollarRing = new THREE.Mesh(
        new THREE.RingGeometry(0.0138, 0.0168, 48),
        new THREE.MeshBasicMaterial({
            color: 0xffaa38,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.88,
            toneMapped: false
        })
    );
    knobCollarRing.position.set(0, 0, 0.0110);
    knobHighlightRing.add(knobCrownRing);
    knobHighlightRing.add(knobCollarRing);
    knobHighlightRing.visible = false;
    app.scene.add(knobHighlightRing);

    // Create Orthographic Screen-Space HUD Scene (1920x1080 pixel coordinates: x in [0..1920], y in [0..1080])
    const hudScene = new THREE.Scene();
    const hudCamera = new THREE.OrthographicCamera(0, 1920, 1080, 0, -10, 10);

    // 1. Top Hardware Header Strip Canvas (1920 x 96) -> placed at y = [1080-96 .. 1080]
    const topH = 96;
    const topCanvas = document.createElement('canvas');
    topCanvas.width = 1920;
    topCanvas.height = topH;
    const topCtx = topCanvas.getContext('2d');
    const topTex = new THREE.CanvasTexture(topCanvas);
    topTex.colorSpace = THREE.SRGBColorSpace;
    topTex.minFilter = THREE.LinearFilter;
    topTex.magFilter = THREE.LinearFilter;
    const topQuad = new THREE.Mesh(
        new THREE.PlaneGeometry(1920, topH),
        new THREE.MeshBasicMaterial({ map: topTex, transparent: true, depthTest: false, depthWrite: false, toneMapped: false })
    );
    topQuad.position.set(960, 1080 - topH / 2, 0);
    hudScene.add(topQuad);

    // 2. Bottom Broadcast Lower-Third + 3-Card Hardware Dock Canvas (1920 x 216) -> placed at y = [0 .. 216]
    const botH = 216;
    const botCanvas = document.createElement('canvas');
    botCanvas.width = 1920;
    botCanvas.height = botH;
    const botCtx = botCanvas.getContext('2d');
    const botTex = new THREE.CanvasTexture(botCanvas);
    botTex.colorSpace = THREE.SRGBColorSpace;
    botTex.minFilter = THREE.LinearFilter;
    botTex.magFilter = THREE.LinearFilter;
    const botQuad = new THREE.Mesh(
        new THREE.PlaneGeometry(1920, botH),
        new THREE.MeshBasicMaterial({ map: botTex, transparent: true, depthTest: false, depthWrite: false, toneMapped: false })
    );
    botQuad.position.set(960, botH / 2, 0);
    hudScene.add(botQuad);

    function roundRectPath(ctx, x, y, w, h, r) {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + w - r, y);
        ctx.quadraticCurveTo(x + w, y, x + w, y + r);
        ctx.lineTo(x + w, y + h - r);
        ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
        ctx.lineTo(x + r, y + h);
        ctx.quadraticCurveTo(x, y + h, x, y + h - r);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.closePath();
    }

    function drawHardwarePanel(ctx, x, y, w, h, borderColor = 'rgba(232, 168, 92, 0.34)') {
        ctx.save();
        roundRectPath(ctx, x, y, w, h, 6);
        ctx.clip();
        ctx.fillStyle = '#14161a';
        ctx.fillRect(x, y, w, h);
        if (skinImg && skinImg.complete && skinImg.naturalWidth > 0) {
            ctx.globalAlpha = 0.42;
            for (let px = x; px < x + w; px += 512) {
                ctx.drawImage(skinImg, px, y, 512, h);
            }
            ctx.globalAlpha = 1.0;
        }
        const grad = ctx.createLinearGradient(0, y, 0, y + h);
        grad.addColorStop(0, 'rgba(255, 244, 224, 0.06)');
        grad.addColorStop(1, 'rgba(8, 9, 12, 0.78)');
        ctx.fillStyle = grad;
        ctx.fillRect(x, y, w, h);
        ctx.restore();

        roundRectPath(ctx, x, y, w, h, 6);
        ctx.strokeStyle = borderColor;
        ctx.lineWidth = 1.2;
        ctx.stroke();
    }

    function drawPillButton(ctx, x, y, w, h, text, state = 'normal') {
        roundRectPath(ctx, x, y, w, h, 4);
        if (state === 'green') {
            const g = ctx.createLinearGradient(0, y, 0, y + h);
            g.addColorStop(0, '#1f7a53'); g.addColorStop(1, '#124a32');
            ctx.fillStyle = g;
            ctx.fill();
            ctx.strokeStyle = '#55e6a5';
        } else if (state === 'amber') {
            const g = ctx.createLinearGradient(0, y, 0, y + h);
            g.addColorStop(0, '#5a3b19'); g.addColorStop(1, '#33200c');
            ctx.fillStyle = g;
            ctx.fill();
            ctx.strokeStyle = '#e89b3c';
        } else {
            const g = ctx.createLinearGradient(0, y, 0, y + h);
            g.addColorStop(0, '#292d34'); g.addColorStop(1, '#191c21');
            ctx.fillStyle = g;
            ctx.fill();
            ctx.strokeStyle = 'rgba(242, 233, 216, 0.26)';
        }
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.fillStyle = state === 'amber' ? '#ffdfa8' : (state === 'green' ? '#ebfff6' : '#f2e9d8');
        ctx.font = '700 11px Inter, "Segoe UI", Arial, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, x + w / 2, y + h / 2 + 0.5);
        ctx.textAlign = 'left';
    }

    const CABLE_PALETTE_HEX = ['#d95b26', '#dba02b', '#2a8f9d', '#c8372d', '#6b934c', '#e8dec8'];

    let lastTopKey = '';
    function updateTopHud(frame) {
        const hlSpec = app.knobSpecsById.get(frame.hlKnob);
        const hlVal = frame.knobs[frame.hlKnob];
        const readoutStr = hlSpec
            ? `${hlSpec.label}: ${app._formatKnobValue(hlSpec, hlVal)} [LIVE AUTOMATION]`
            : 'LIVE SYMPHONIC AUTOMATION';
        const movIdx = Math.min(4, Math.floor(frame.t / 30.0) + 1);
        const topKey = `${movIdx}|${frame.cam.presetId}|${frame.status}|${readoutStr}|${frame.cables.length}`;
        if (topKey === lastTopKey) return;
        lastTopKey = topKey;

        topCtx.clearRect(0, 0, 1920, topH);

        // Bar 1: Top Header (y = 8..48)
        drawHardwarePanel(topCtx, 14, 6, 1892, 42, 'rgba(232, 168, 92, 0.32)');
        topCtx.fillStyle = '#f2e9d8';
        topCtx.font = '800 13px Inter, "Segoe UI", Arial, sans-serif';
        topCtx.textBaseline = 'middle';
        topCtx.fillText('CHRONO ANALOGUE // SYSTEM 1974', 28, 20);
        topCtx.fillStyle = '#b6aa96';
        topCtx.font = '500 10.5px Inter, "Segoe UI", Arial, sans-serif';
        topCtx.fillText('Modular Analogue Synthesiser (0.8m / 15° Tilt) & Direct-Drive Turntable', 28, 36);

        // World verified badge
        roundRectPath(topCtx, 430, 15, 226, 24, 4);
        topCtx.fillStyle = '#091510';
        topCtx.fill();
        topCtx.strokeStyle = 'rgba(85, 230, 165, 0.48)';
        topCtx.stroke();
        topCtx.fillStyle = '#55e6a5';
        topCtx.font = '700 10.5px Consolas, monospace';
        topCtx.fillText('WORLD.JSON VERIFIED (64/64 NODES)', 442, 27.5);

        // Right controls on Bar 1
        drawPillButton(topCtx, 680, 13, 218, 28, 'AUDIO ENGINE RUNNING (48.0 kHz)', 'green');

        const presetNames = [
            '01. Beethoven No. 5 — Dual Saw Brass Lead',
            '02. Bach / Vivaldi — Baroque Organ + BBD Delay',
            '03. Mozart No. 40 — Spiccato + 180g Vinyl Deck',
            '04. Beethoven No. 9 — 6-Cable Maximalist Finale'
        ];
        drawPillButton(topCtx, 908, 13, 315, 28, presetNames[movIdx - 1], 'amber');
        drawPillButton(topCtx, 1233, 13, 195, 28, `ACTIVE PATCHES: ${frame.cables.length} CABLES`, 'normal');
        drawPillButton(topCtx, 1438, 13, 160, 28, 'MASTER VOL: 88%', 'normal');
        drawPillButton(topCtx, 1608, 13, 284, 28, 'REC ● 1920x1080 · 60.0 FPS FULL HD', 'amber');

        // Bar 2: Subbar (y = 54..90)
        drawHardwarePanel(topCtx, 14, 52, 1892, 38, 'rgba(242, 233, 216, 0.20)');
        topCtx.fillStyle = frame.preview ? '#ffdf8e' : '#55e6a5';
        topCtx.font = '600 11.5px Inter, "Segoe UI", Arial, sans-serif';
        topCtx.fillText(frame.status, 28, 71);

        // Live Knob/Socket Readout Pill
        const roX = 650;
        roundRectPath(topCtx, roX, 58, 410, 26, 4);
        topCtx.fillStyle = '#0d0e11';
        topCtx.fill();
        topCtx.strokeStyle = 'rgba(232, 155, 60, 0.42)';
        topCtx.stroke();
        topCtx.fillStyle = '#e89b3c';
        topCtx.font = '700 11px Consolas, monospace';
        topCtx.fillText(readoutStr, roX + 12, 71.5);

        // Camera Preset Buttons on right of Subbar
        const camButtons = [
            ['opening_studio', '1. Overview', 112],
            ['synth_rack_closeup', '2. Modular Rack', 132],
            ['patch_and_keys', '3. Patch & Keys', 132],
            ['turntable_closeup', '4. Turntable', 116],
            ['side_profile_tilt', '5. 15° Side Profile', 142]
        ];
        let cx = 1250;
        for (const [cid, clabel, cw] of camButtons) {
            drawPillButton(topCtx, cx, 58, cw, 26, clabel, frame.cam.presetId === cid ? 'amber' : 'normal');
            cx += cw + 8;
        }

        topTex.needsUpdate = true;
    }

    function updateBottomHud(frame, cap) {
        botCtx.clearRect(0, 0, 1920, botH);

        // ----------------------------------------------------------------------
        // ROW A: BROADCAST SOCIAL MEDIA LOWER-THIRD CAPTION BANNER (y = 6 .. 94)
        // ----------------------------------------------------------------------
        const bx = 14, by = 6, bw = 1892, bh = 86;
        drawHardwarePanel(botCtx, bx, by, bw, bh, 'rgba(232, 155, 60, 0.58)');

        // Left glowing vertical accent bar
        roundRectPath(botCtx, bx + 4, by + 4, 7, bh - 8, 3);
        botCtx.fillStyle = frame.preview ? '#55e6a5' : '#e89b3c';
        botCtx.fill();

        // Movement badge pill
        roundRectPath(botCtx, bx + 22, by + 10, 395, 22, 4);
        botCtx.fillStyle = 'rgba(232, 155, 60, 0.16)';
        botCtx.fill();
        botCtx.strokeStyle = 'rgba(232, 155, 60, 0.55)';
        botCtx.stroke();
        botCtx.fillStyle = '#ffcf7d';
        botCtx.font = '800 11px Inter, "Segoe UI", Arial, sans-serif';
        botCtx.textBaseline = 'middle';
        botCtx.fillText(cap.movement, bx + 32, by + 21.5);

        // Action Tag Pill
        roundRectPath(botCtx, bx + 428, by + 10, 185, 22, 4);
        botCtx.fillStyle = '#091812';
        botCtx.fill();
        botCtx.strokeStyle = '#55e6a5';
        botCtx.stroke();
        botCtx.fillStyle = '#55e6a5';
        botCtx.font = '800 10.5px Consolas, monospace';
        botCtx.textAlign = 'center';
        botCtx.fillText(cap.tag, bx + 428 + 92.5, by + 21.5);
        botCtx.textAlign = 'left';

        // Main Symphony Title (Large Broadcast Headline)
        botCtx.fillStyle = '#ffffff';
        botCtx.font = '800 18.5px Inter, "Segoe UI", Arial, sans-serif';
        botCtx.fillText(cap.title, bx + 22, by + 48);

        // Subtitle (Live Cable Patch / Knob Sweep / Turntable Action)
        botCtx.fillStyle = '#55e6a5';
        botCtx.font = '700 13.5px Inter, "Segoe UI", Arial, sans-serif';
        botCtx.fillText(cap.subtitle, bx + 22, by + 73);

        // Right-side Live Telemetry & Timecode Box inside the Broadcast Banner
        const tx = 1365, ty = by + 10, tw = 528, th = bh - 20;
        roundRectPath(botCtx, tx, ty, tw, th, 5);
        botCtx.fillStyle = 'rgba(9, 11, 14, 0.86)';
        botCtx.fill();
        botCtx.strokeStyle = 'rgba(242, 233, 216, 0.22)';
        botCtx.stroke();

        const cutoffHz = Math.round(frame.knobs.knob_vcf_cutoff);
        const resQ = frame.knobs.knob_vcf_resonance.toFixed(1);
        const driveX = frame.knobs.knob_vcf_drive.toFixed(1);
        const envCt = Math.round(frame.knobs.knob_vcf_env_amt);
        const dlyMix = Math.round(frame.knobs.knob_dly_mix * 100);

        botCtx.fillStyle = '#f2e9d8';
        botCtx.font = '700 11.5px Consolas, monospace';
        botCtx.fillText(
            `VCF CUTOFF: ${cutoffHz} Hz | RES: ${resQ} Q | DRIVE: ${driveX}x`,
            tx + 14, ty + 18
        );
        botCtx.fillStyle = '#e89b3c';
        botCtx.fillText(
            `ENV MOD: +${envCt} ct | BBD DELAY: ${dlyMix}% | KEYS: ${frame.keys.length} ACTIVE`,
            tx + 14, ty + 37
        );

        // Progress bar & timecode (floor tenths so 59.95s..59.99s never rounds to :60.0)
        const totalTenths = Math.min(1200, Math.floor(frame.t * 10.0 + 1e-4));
        const mins = Math.floor(totalTenths / 600);
        const secs = ((totalTenths % 600) / 10.0).toFixed(1).padStart(4, '0');
        botCtx.fillStyle = '#55e6a5';
        botCtx.font = '700 11px Consolas, monospace';
        botCtx.fillText(`TIMECODE 0${mins}:${secs} / 02:00.0`, tx + 14, ty + 55);

        const barX = tx + 215, barY = ty + 50, barW = 296, barH = 9;
        roundRectPath(botCtx, barX, barY, barW, barH, 4);
        botCtx.fillStyle = '#1b2026';
        botCtx.fill();
        const fillW = Math.max(6, Math.round(barW * (frame.t / 120.0)));
        roundRectPath(botCtx, barX, barY, fillW, barH, 4);
        botCtx.fillStyle = '#55e6a5';
        botCtx.fill();

        // ----------------------------------------------------------------------
        // ROW B: 3-CARD BOTTOM HARDWARE DOCK (y = 102 .. 208)
        // ----------------------------------------------------------------------
        const dy = 102, dh = 106;

        // Card 1: PATCH MATRIX (x = 14 .. 780)
        drawHardwarePanel(botCtx, 14, dy, 766, dh, 'rgba(232, 168, 92, 0.26)');
        botCtx.fillStyle = '#b6aa96';
        botCtx.font = '700 10.5px Inter, "Segoe UI", Arial, sans-serif';
        botCtx.fillText('PATCH MATRIX (12 SOCKETS · CORRIDOR-ROUTED 3D BRAIDED CABLES)', 28, dy + 18);
        botCtx.fillStyle = '#55e6a5';
        botCtx.fillText(`${frame.cables.length} CONNECTED`, 665, dy + 18);

        let chipX = 28, chipY = dy + 32;
        frame.cables.forEach((pair, idx) => {
            const sSpec = app.socketSpecsById.get(pair[0]);
            const tSpec = app.socketSpecsById.get(pair[1]);
            const label = `${sSpec ? sSpec.label : pair[0]} → ${tSpec ? tSpec.label : pair[1]}`;
            botCtx.font = '600 10.5px Inter, "Segoe UI", Arial, sans-serif';
            const twChip = Math.ceil(botCtx.measureText(label).width) + 28;
            if (chipX + twChip > 766) {
                chipX = 28;
                chipY += 32;
            }
            roundRectPath(botCtx, chipX, chipY, twChip, 24, 4);
            botCtx.fillStyle = 'rgba(255, 255, 255, 0.06)';
            botCtx.fill();
            botCtx.strokeStyle = 'rgba(255, 255, 255, 0.18)';
            botCtx.stroke();

            botCtx.beginPath();
            botCtx.arc(chipX + 11, chipY + 12, 4.2, 0, Math.PI * 2);
            botCtx.fillStyle = CABLE_PALETTE_HEX[idx % CABLE_PALETTE_HEX.length];
            botCtx.fill();

            botCtx.fillStyle = '#f2e9d8';
            botCtx.fillText(label, chipX + 20, chipY + 12.5);
            chipX += twChip + 7;
        });

        // Card 2: CHRONO-DRIVE TURNTABLE (x = 792 .. 1356)
        drawHardwarePanel(botCtx, 792, dy, 564, dh, 'rgba(232, 168, 92, 0.26)');
        botCtx.fillStyle = '#b6aa96';
        botCtx.font = '700 10.5px Inter, "Segoe UI", Arial, sans-serif';
        botCtx.fillText('CHRONO-DRIVE DD-1974 TURNTABLE (180g LP)', 806, dy + 18);

        const is45 = frame.tt.rpm > 40;
        const ttStateStr = `${frame.tt.state.toUpperCase()} · ${is45 ? '45 RPM (1.35x)' : '33⅓ RPM (1.00x)'}`;
        botCtx.fillStyle = frame.tt.motorOn ? '#55e6a5' : '#b6aa96';
        botCtx.font = '700 10.5px Consolas, monospace';
        botCtx.fillText(ttStateStr, 1115, dy + 18);

        drawPillButton(botCtx, 806, dy + 34, 128, 28, frame.tt.motorOn ? 'STOP PLATTER' : 'START PLATTER', frame.tt.motorOn ? 'amber' : 'normal');
        drawPillButton(botCtx, 942, dy + 34, 132, 28, frame.tt.tonearmLowered ? 'LIFT TONEARM' : 'LOWER TONEARM', frame.tt.tonearmLowered ? 'amber' : 'normal');
        drawPillButton(botCtx, 1082, dy + 34, 126, 28, '33⅓ RPM (1.00x)', !is45 ? 'amber' : 'normal');
        drawPillButton(botCtx, 1216, dy + 34, 124, 28, '45 RPM (1.35x)', is45 ? 'green' : 'normal');

        botCtx.fillStyle = '#b6aa96';
        botCtx.font = '500 11px Inter, "Segoe UI", Arial, sans-serif';
        botCtx.fillText(
            frame.tt.tonearmLowered
                ? `Stylus Tracking 180g Groove · Rate ${frame.tt.playbackRate.toFixed(2)}x · Continuous Phase Lock`
                : 'Direct-Drive Platter Cued · Lower S-Shaped Tonearm for Symphonic Vinyl Layer',
            806, dy + 82
        );

        // Card 3: WAVEFORM MONITOR & HEADROOM (x = 1368 .. 1906)
        drawHardwarePanel(botCtx, 1368, dy, 538, dh, 'rgba(232, 168, 92, 0.26)');
        botCtx.fillStyle = '#b6aa96';
        botCtx.font = '700 10.5px Inter, "Segoe UI", Arial, sans-serif';
        botCtx.fillText('WAVEFORM MONITOR & HEADROOM', 1384, dy + 18);
        botCtx.fillStyle = '#e89b3c';
        botCtx.fillText('48.0 kHz STEREO · 24 dB/OCT LADDER', 1685, dy + 18);

        // Green Phosphor Oscilloscope Screen
        const sx = 1384, sy = dy + 32, sw = 248, sh = 60;
        roundRectPath(botCtx, sx, sy, sw, sh, 4);
        botCtx.fillStyle = '#090e0c';
        botCtx.fill();
        botCtx.strokeStyle = 'rgba(85, 230, 165, 0.38)';
        botCtx.lineWidth = 1;
        botCtx.stroke();

        // Scope graticule grid
        botCtx.strokeStyle = 'rgba(82, 196, 138, 0.14)';
        botCtx.beginPath();
        botCtx.moveTo(sx, sy + sh / 2); botCtx.lineTo(sx + sw, sy + sh / 2);
        botCtx.moveTo(sx + sw / 2, sy); botCtx.lineTo(sx + sw / 2, sy + sh);
        botCtx.stroke();

        // Draw actual 48 kHz waveform slice
        const pts = frame.wave.wave || [];
        if (pts.length > 0) {
            botCtx.save();
            botCtx.strokeStyle = '#55e6a5';
            botCtx.lineWidth = 2.1;
            botCtx.shadowColor = 'rgba(85, 230, 165, 0.65)';
            botCtx.shadowBlur = 5;
            botCtx.beginPath();
            for (let i = 0; i < pts.length; i++) {
                const px = sx + 4 + (i / (pts.length - 1)) * (sw - 8);
                const py = sy + sh * (0.5 - pts[i] * 0.44);
                if (i === 0) botCtx.moveTo(px, py);
                else botCtx.lineTo(px, py);
            }
            botCtx.stroke();
            botCtx.restore();
        }

        // Peak / RMS Telemetry Readout
        botCtx.fillStyle = '#55e6a5';
        botCtx.font = '700 12px Consolas, monospace';
        botCtx.fillText(
            `PEAK ${frame.wave.peak.toFixed(3)} · RMS ${frame.wave.rms.toFixed(3)}`,
            sx + sw + 14, sy + 16
        );
        botCtx.fillStyle = '#f2e9d8';
        botCtx.font = '600 11px Inter, "Segoe UI", Arial, sans-serif';
        botCtx.fillText('HEADROOM: -1.1 dBFS (ZERO CLIP)', sx + sw + 14, sy + 35);
        botCtx.fillStyle = '#b6aa96';
        botCtx.font = '500 10.5px Inter, "Segoe UI", Arial, sans-serif';
        botCtx.fillText('25-Key Manual: C3–C5 Active', sx + sw + 14, sy + 52);

        botTex.needsUpdate = true;
    }

    let prevCablesSig = '';
    const dt = 1.0 / 60.0;

    window.__renderShowcaseFrame = function(frame) {
        const cap = captions[frame.capIdx] || captions[0];

        // 1. Update Camera Pose
        app.camera.position.set(...frame.cam.pos);
        app.controls.target.set(...frame.cam.target);
        app.camera.fov = frame.cam.fov;
        app.camera.updateProjectionMatrix();
        app.controls.update();

        // 2. Update Patch Cables if changed
        const cablesSig = frame.cables.map(p => p[0] + '->' + p[1]).join('|');
        if (cablesSig !== prevCablesSig) {
            prevCablesSig = cablesSig;
            app.audio.cables = frame.cables.map((pair, idx) => ({
                id: `cable_${pair[0]}__${pair[1]}`,
                fromSocketId: pair[0],
                toSocketId: pair[1],
                color: CABLE_PALETTE_HEX[idx % CABLE_PALETTE_HEX.length]
            }));
            app._rebuildCableMeshes();
        }

        // 3. Update Animated Preview Patch Cable & Socket Highlight Rings
        if (frame.preview) {
            app.pendingPatchSocketId = frame.preview.from_id;
            const sSpec = app.socketSpecsById.get(frame.preview.from_id);
            const tSpec = app.socketSpecsById.get(frame.preview.to_id);
            const sNode = sSpec ? app.nodesByName.get(sSpec.node_name) : null;
            const tNode = tSpec ? app.nodesByName.get(tSpec.node_name) : null;
            if (sNode && tNode) {
                const pStart = new THREE.Vector3();
                const pEnd = new THREE.Vector3();
                sNode.getWorldPosition(pStart);
                tNode.getWorldPosition(pEnd);
                const prog = frame.preview.progress;
                const curPt = new THREE.Vector3().lerpVectors(pStart, pEnd, prog);
                // Add a natural hand-guided arc lift during live cable patching
                curPt.y += Math.sin(Math.PI * prog) * 0.045;
                curPt.z += Math.sin(Math.PI * prog) * 0.040;
                app._updatePreviewCable(curPt);
            }
        } else {
            if (app.pendingPatchSocketId) {
                app.pendingPatchSocketId = null;
                app._removePreviewCable();
            }
        }
        app._updateSocketRingHighlights();
        if (frame.preview && app.socketRings) {
            for (const sid of [frame.preview.from_id, frame.preview.to_id]) {
                const ring = app.socketRings.get(sid);
                if (ring) {
                    ring.visible = true;
                    ring.material.color.setHex(0x48f08b);
                    ring.material.opacity = 0.95;
                    ring.scale.setScalar(1.22);
                }
            }
        }

        // 4. Update all 16 Knobs & Position 3D Active Knob Callout Halo Ring
        for (const [kId, kVal] of Object.entries(frame.knobs)) {
            app.knobValues.set(kId, kVal);
            app._applyKnobAngle(kId, kVal);
        }
        const hlSpec = app.knobSpecsById.get(frame.hlKnob);
        const hlNode = hlSpec ? app.nodesByName.get(hlSpec.node_name) : null;
        if (hlNode && !frame.preview) {
            if (knobHighlightRing.parent !== hlNode) {
                hlNode.add(knobHighlightRing);
            }
            knobHighlightRing.position.set(0, 0, 0);
            knobHighlightRing.rotation.set(0, 0, 0);
            const pulse = 1.0 + 0.055 * Math.sin(frame.t * 10.0);
            knobHighlightRing.scale.set(pulse, pulse, 1.0);
            knobHighlightRing.visible = true;
        } else {
            knobHighlightRing.visible = false;
        }

        // 5. Update 25-Key Manual Depression Angles (Spring-Return Hinge)
        const pressedSet = new Set(frame.keys);
        const travelRad = THREE.MathUtils.degToRad(4.8);
        for (const keySpec of app.contract.keyboard.keys) {
            const targetAngle = pressedSet.has(keySpec.midi_note) ? travelRad : 0.0;
            const curAngle = app.keyAngles.get(keySpec.midi_note) || 0.0;
            const nextAngle = curAngle + (targetAngle - curAngle) * 0.55;
            app.keyAngles.set(keySpec.midi_note, nextAngle);
            const kNode = app.nodesByName.get(keySpec.node_name);
            if (kNode) kNode.rotation.x = nextAngle;
        }

        // 6. Update Direct-Drive Turntable Platter, Speed Switch & S-Shaped Tonearm
        const platterNode = app.nodesByName.get('Turntable_Platter');
        const gimbalNode = app.nodesByName.get('Tonearm_Gimbal');
        const swNode = app.nodesByName.get('Turntable_SpeedSwitch');

        if (platterNode && frame.tt.motorOn) {
            const omega = (frame.tt.rpm * 2.0 * Math.PI) / 60.0;
            app.platterAngleRad -= omega * dt;
            platterNode.rotation.y = app.platterAngleRad;
        }
        if (swNode) {
            swNode.rotation.y = frame.tt.rpm > 40 ? -0.55 : 0.0;
        }
        if (gimbalNode) {
            const ttSpec = app.contract.turntable.tonearm_gimbal_node;
            const progress = frame.tt.tonearmLowered
                ? Math.min(1.0, Math.max(0.0, (frame.t - 61.6) / 58.4))
                : 0.0;
            const targetYawDeg = frame.tt.tonearmLowered
                ? THREE.MathUtils.lerp(ttSpec.outer_groove_yaw_deg, ttSpec.inner_groove_yaw_deg, progress)
                : ttSpec.rest_yaw_deg;
            const targetPitchDeg = frame.tt.tonearmLowered
                ? ttSpec.lowered_pitch_deg
                : ttSpec.raised_pitch_deg;
            app.currentTonearmYawDeg = THREE.MathUtils.lerp(app.currentTonearmYawDeg, targetYawDeg, 0.22);
            app.currentTonearmPitchDeg = THREE.MathUtils.lerp(app.currentTonearmPitchDeg, targetPitchDeg, 0.25);
            gimbalNode.rotation.y = THREE.MathUtils.degToRad(app.currentTonearmYawDeg);
            gimbalNode.rotation.x = THREE.MathUtils.degToRad(app.currentTonearmPitchDeg);
        }

        // 7. Update Top & Bottom Broadcast HUD Textures
        updateTopHud(frame);
        updateBottomHud(frame, cap);

        // 8. Render 3D Studio Scene + Orthographic Broadcast HUD Overlay
        app.renderer.clear();
        app.renderer.render(app.scene, app.camera);
        app.renderer.clearDepth();
        app.renderer.render(hudScene, hudCamera);
    };

    return true;
};
"""


def render_preview_stills(timeline: dict):
    """Renders 5 representative 1920x1080 frames to PNG so we can visually inspect quality before full encode."""
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    ud = EVIDENCE_DIR / "chrome_preview_profile"
    ud.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen(
        [
            CHROME_EXE,
            "--headless=new",
            "--remote-debugging-port=9240",
            "--remote-allow-origins=*",
            f"--user-data-dir={ud}",
            "--window-size=1920,1080",
            "--device-scale-factor=1",
            "--autoplay-policy=no-user-gesture-required",
            "--enable-webgl",
            "--ignore-gpu-blocklist",
            "--use-angle=d3d11",
            "--no-first-run",
            "--no-default-browser-check",
            STUDIO_URL,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        ws = wait_for_cdp_target(9240, timeout_s=15.0)
        cdp = CDPClient(ws)
        cdp.call("Page.enable")
        cdp.call("Runtime.enable")
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1920, "height": 1080, "deviceScaleFactor": 1, "mobile": False},
        )
        while not cdp.evaluate(
            "Boolean(window.studioApp && window.studioApp.worldVerification && window.studioApp.worldVerification.pass)",
            await_promise=False,
        ):
            time.sleep(0.2)

        cdp.evaluate(INJECT_SHOWCASE_JS, await_promise=False)
        cdp.evaluate(
            f"window.__initShowcaseRenderer({json.dumps(timeline['captions'])})",
            await_promise=True,
        )

        sample_frames = [
            (84, "showcase_preview_mov1_patching.png"),       # t = 1.4s: Mov I live cable patching
            (720, "showcase_preview_mov1_keys_sweep.png"),    # t = 12.0s: Mov I Beethoven 5th keys & filter sweep (patch_and_keys)
            (1080, "showcase_preview_mov1_side_tilt.png"),    # t = 18.0s: Mov I side_profile_tilt camera check
            (1926, "showcase_preview_mov2_bach_delay.png"),   # t = 32.1s: Mov II Bach live BBD delay patching
            (4530, "showcase_preview_mov3_mozart_45rpm.png"), # t = 75.5s: Mov III Mozart 45 RPM turntable closeup
            (6870, "showcase_preview_mov4_ode_finale.png"),   # t = 114.5s: Mov IV Beethoven 9th 6-cable finale
        ]

        frames = timeline["frames"]
        for f_idx, fname in sample_frames:
            warmup_start = max(0, f_idx - 30)
            init_platter = 0.0
            for f_prev in range(warmup_start):
                tt_prev = frames[f_prev]["tt"]
                if tt_prev["motorOn"]:
                    init_platter -= ((tt_prev["rpm"] * 2.0 * math.pi) / 60.0) * (1.0 / 60.0)
            cdp.evaluate(f"window.studioApp.platterAngleRad = {init_platter:.6f};", await_promise=False)
            # Step 30 preceding frames so key angles, platter angle, and tonearm lerp settle naturally
            for step_f in range(warmup_start, f_idx + 1):
                cdp.evaluate(
                    f"window.__renderShowcaseFrame({json.dumps(frames[step_f])})",
                    await_promise=False,
                )
            out_p = CAPTURES_DIR / fname
            sz = cdp.capture_png(out_p)
            print(f"Captured 1920x1080 preview still: {out_p} ({sz:,} bytes)")

        cdp.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


def run_segment_worker(worker_id: int, start_frame: int, end_frame: int, timeline: dict, out_mp4: Path, errors: list):
    """
    Renders frames [start_frame .. end_frame - 1] in a dedicated headless Chrome instance at 1920x1080
    and streams raw RGBA frames via Dual WebGL2 PBO + localhost WebSocket into FFmpeg.
    """
    cdp_port = 9241 + worker_id
    ws_port = 9251 + worker_id
    ud = EVIDENCE_DIR / f"chrome_worker_{worker_id}"
    ud.mkdir(parents=True, exist_ok=True)
    num_frames = end_frame - start_frame

    # 1. Start WebSocket -> FFmpeg receiver thread
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16 * 1024 * 1024)
    srv.settimeout(60.0)
    srv.bind(("127.0.0.1", ws_port))
    srv.listen(1)

    receiver_done = threading.Event()

    def ws_receiver():
        try:
            conn, _ = srv.accept()
            conn.settimeout(300.0)
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16 * 1024 * 1024)
            req = b""
            while b"\r\n\r\n" not in req:
                req += conn.recv(4096)
            key = [
                line.split(": ")[1]
                for line in req.decode().split("\r\n")
                if line.lower().startswith("sec-websocket-key:")
            ][0]
            accept = base64.b64encode(
                hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
            ).decode()
            conn.sendall(
                (
                    "HTTP/1.1 101 Switching Protocols\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
                ).encode()
            )

            ff = subprocess.Popen(
                [
                    FFMPEG_EXE,
                    "-y",
                    "-f", "rawvideo",
                    "-pix_fmt", "rgba",
                    "-s", "1920x1080",
                    "-r", "60",
                    "-i", "-",
                    "-vf", "vflip",
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-crf", "16",
                    "-pix_fmt", "yuv420p",
                    "-r", "60",
                    str(out_mp4),
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            frame_bytes = 1920 * 1080 * 4
            scratch = bytearray(frame_bytes + 65536)
            scratch_mv = memoryview(scratch)
            hdr_buf = bytearray(16)
            hdr_mv = memoryview(hdr_buf)

            def recv_into_mv(mv, n):
                pos = 0
                while pos < n:
                    r = conn.recv_into(mv[pos:n], n - pos)
                    if not r:
                        return False
                    pos += r
                return True

            rcvd = 0
            t_start = time.time()
            closed = False
            while rcvd < num_frames and not closed:
                msg_pos = 0
                while True:
                    if not recv_into_mv(hdr_mv, 2):
                        closed = True
                        break
                    fin = (hdr_buf[0] & 0x80) != 0
                    opcode = hdr_buf[0] & 0x0F
                    if opcode == 0x8:
                        closed = True
                        break
                    length = hdr_buf[1] & 0x7F
                    if length == 126:
                        if not recv_into_mv(hdr_mv, 2):
                            closed = True
                            break
                        length = struct.unpack("!H", hdr_mv[:2])[0]
                    elif length == 127:
                        if not recv_into_mv(hdr_mv, 8):
                            closed = True
                            break
                        length = struct.unpack("!Q", hdr_mv[:8])[0]
                    if not recv_into_mv(hdr_mv, 4):
                        closed = True
                        break
                    mask_bytes = bytes(hdr_mv[:4])
                    chunk_mv = scratch_mv[msg_pos : msg_pos + length]
                    if not recv_into_mv(chunk_mv, length):
                        closed = True
                        break
                    rem = length & 3
                    n4 = length - rem
                    if n4 > 0:
                        arr = np.frombuffer(chunk_mv[:n4], dtype=np.uint32)
                        m32 = np.frombuffer(mask_bytes, dtype=np.uint32)[0]
                        arr ^= m32
                    for b_i in range(n4, length):
                        chunk_mv[b_i] ^= mask_bytes[b_i & 3]
                    msg_pos += length
                    if fin:
                        break
                if closed or msg_pos < frame_bytes:
                    break
                ff.stdin.write(scratch_mv[:frame_bytes])
                rcvd += 1
                conn.sendall(b"\x81\x02ok")
                if rcvd % 300 == 0 or rcvd == num_frames:
                    el = time.time() - t_start
                    print(f"[Worker {worker_id}] Encoded {rcvd}/{num_frames} frames ({el:.1f}s)", flush=True)

            ff.stdin.close()
            ff.wait()
            conn.close()
        except Exception as e:
            errors.append(f"Worker {worker_id} receiver error: {e}")
        finally:
            srv.close()
            receiver_done.set()

    t_recv = threading.Thread(target=ws_receiver, daemon=True)
    t_recv.start()

    # 2. Launch Headless Chrome Worker
    proc = subprocess.Popen(
        [
            CHROME_EXE,
            "--headless=new",
            f"--remote-debugging-port={cdp_port}",
            "--remote-allow-origins=*",
            f"--user-data-dir={ud}",
            "--window-size=1920,1080",
            "--device-scale-factor=1",
            "--autoplay-policy=no-user-gesture-required",
            "--enable-webgl",
            "--ignore-gpu-blocklist",
            "--use-angle=d3d11",
            "--no-first-run",
            "--no-default-browser-check",
            STUDIO_URL,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        ws_url = wait_for_cdp_target(cdp_port, timeout_s=20.0)
        cdp = CDPClient(ws_url)
        cdp.sock.settimeout(3600.0)
        cdp.call("Page.enable")
        cdp.call("Runtime.enable")
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1920, "height": 1080, "deviceScaleFactor": 1, "mobile": False},
        )
        while not cdp.evaluate(
            "Boolean(window.studioApp && window.studioApp.worldVerification && window.studioApp.worldVerification.pass)",
            await_promise=False,
        ):
            time.sleep(0.25)

        cdp.evaluate(INJECT_SHOWCASE_JS, await_promise=False)
        cdp.evaluate(
            f"window.__initShowcaseRenderer({json.dumps(timeline['captions'])})",
            await_promise=True,
        )

        # Upload this worker's slice of frames + 30-frame pre-roll to the browser
        warmup_start = max(0, start_frame - 30)
        warmup_frames = timeline["frames"][warmup_start:start_frame]
        segment_frames = timeline["frames"][start_frame:end_frame]
        cdp.evaluate(
            f"window.__warmupFrames = {json.dumps(warmup_frames)}; window.__segmentFrames = {json.dumps(segment_frames)}; true;",
            await_promise=False,
        )

        # Set initial platter angle at warmup_start and run pre-roll so keyAngles, tonearm yaw/pitch, and platterAngleRad match seamlessly at start_frame
        init_platter = 0.0
        for f_prev in range(warmup_start):
            tt_prev = timeline["frames"][f_prev]["tt"]
            if tt_prev["motorOn"]:
                init_platter -= ((tt_prev["rpm"] * 2.0 * math.pi) / 60.0) * (1.0 / 60.0)

        cdp.evaluate(
            f"""(() => {{
                window.studioApp.platterAngleRad = {init_platter:.6f};
                for (const wf of window.__warmupFrames) {{
                    window.__renderShowcaseFrame(wf);
                }}
                return true;
            }})()""",
            await_promise=False,
        )

        # Run Dual-PBO + Pipelined WebSocket render loop inside Chrome
        cdp.evaluate(
            f"""(async () => {{
                const app = window.studioApp;
                const gl = app.renderer.getContext();
                const byteLen = 1920 * 1080 * 4;
                const pbo0 = gl.createBuffer();
                const pbo1 = gl.createBuffer();
                for (const p of [pbo0, pbo1]) {{
                    gl.bindBuffer(gl.PIXEL_PACK_BUFFER, p);
                    gl.bufferData(gl.PIXEL_PACK_BUFFER, byteLen, gl.STREAM_READ);
                }}
                gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
                const pbos = [pbo0, pbo1];
                const buf = new Uint8Array(byteLen);

                const sock = new WebSocket('ws://127.0.0.1:{ws_port}');
                sock.binaryType = 'arraybuffer';
                await new Promise((r, rej) => {{ sock.onopen = r; sock.onerror = rej; }});

                let inFlight = 0;
                let resolveWait = null;
                sock.onmessage = () => {{
                    inFlight--;
                    if (resolveWait && inFlight < 2) {{
                        const r = resolveWait;
                        resolveWait = null;
                        r();
                    }}
                }};

                const frames = window.__segmentFrames;
                const n = frames.length;
                for (let i = 0; i <= n; i++) {{
                    if (i < n) {{
                        window.__renderShowcaseFrame(frames[i]);
                        gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pbos[i % 2]);
                        gl.readPixels(0, 0, 1920, 1080, gl.RGBA, gl.UNSIGNED_BYTE, 0);
                    }}
                    if (i > 0) {{
                        gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pbos[(i - 1) % 2]);
                        gl.getBufferSubData(gl.PIXEL_PACK_BUFFER, 0, buf);
                        gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
                        if (inFlight >= 2) {{
                            await new Promise(r => {{ resolveWait = r; }});
                        }}
                        inFlight++;
                        sock.send(buf);
                    }} else {{
                        gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
                    }}
                }}
                while (inFlight > 0) {{
                    await new Promise(r => {{ resolveWait = r; }});
                }}
                sock.close();
                return true;
            }})()""",
            await_promise=True,
        )
        receiver_done.wait(timeout=3600.0)
        cdp.close()
    except Exception as e:
        errors.append(f"Worker {worker_id} error: {e}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


def mux_final_mp4(seg_files: list):
    concat_list = EVIDENCE_DIR / "segments_concat.txt"
    lines = [f"file '{p.name}'" for p in seg_files]
    concat_list.write_text("\n".join(lines), encoding="utf-8")

    cmd = [
        FFMPEG_EXE,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-i", str(WAV_MASTER),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-ac", "2",
        "-movflags", "+faststart",
        "-shortest",
        str(MP4_MASTER),
    ]
    print("Muxing 4 video movements + 48 kHz stereo WAV into master 1080p60 MP4...")
    subprocess.run(cmd, check=True, cwd=str(EVIDENCE_DIR))
    concat_list.unlink(missing_ok=True)
    for p in seg_files:
        p.unlink(missing_ok=True)

    # Probe final MP4 with ffprobe
    probe_cmd = [
        FFPROBE_EXE,
        "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=index,codec_name,codec_type,width,height,r_frame_rate,avg_frame_rate,nb_frames,sample_rate,channels",
        "-of", "json",
        str(MP4_MASTER),
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    info = json.loads(res.stdout)
    print("FFPROBE VERIFICATION OF MASTER MP4:")
    print(json.dumps(info, indent=2))
    return info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview-only", action="store_true")
    parser.add_argument("--skip-previews", action="store_true")
    parser.add_argument("--only-worker", type=int, default=None)
    args = parser.parse_args()

    timeline = json.loads(TIMELINE_JSON.read_text(encoding="utf-8"))

    if args.preview_only:
        render_preview_stills(timeline)
        return

    t0 = time.time()
    if not args.skip_previews and args.only_worker is None:
        render_preview_stills(timeline)

    print("Launching headless Chrome worker(s) to render 7,200 frames (120.0s @ 60.0 fps, 1920x1080)...", flush=True)
    seg_ranges = [
        (0, 0, 1800),
        (1, 1800, 3600),
        (2, 3600, 5400),
        (3, 5400, 7200),
    ]
    seg_files = []
    threads = []
    errors = []

    for w_id, s_f, e_f in seg_ranges:
        seg_mp4 = EVIDENCE_DIR / f"seg_mov_{w_id + 1}.mp4"
        seg_files.append(seg_mp4)
        if args.only_worker is not None and w_id != args.only_worker:
            continue
        th = threading.Thread(
            target=run_segment_worker,
            args=(w_id, s_f, e_f, timeline, seg_mp4, errors),
        )
        threads.append(th)
        th.start()
        time.sleep(1.0)  # Stagger Chrome startups slightly

    for th in threads:
        th.join()

    if errors:
        raise RuntimeError(f"Worker errors occurred: {errors}")

    info = mux_final_mp4(seg_files)
    elapsed = time.time() - t0
    print(f"COMPLETED 1080p60 MASTER VIDEO SHOWCASE IN {elapsed:.1f}s -> {MP4_MASTER} ({MP4_MASTER.stat().st_size:,} bytes)", flush=True)


if __name__ == "__main__":
    main()
