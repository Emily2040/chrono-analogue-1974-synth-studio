import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { StudioAudioEngine } from './audio-engine.js';

const CABLE_PALETTE = [
  { name: 'Burnt Orange', hex: 0xd95b26 },
  { name: 'Ochre Gold', hex: 0xdba02b },
  { name: 'Teal Cyan', hex: 0x2a8f9d },
  { name: 'Crimson Red', hex: 0xc8372d },
  { name: 'Sage Olive', hex: 0x6b934c },
  { name: 'Warm Cream', hex: 0xe8dec8 }
];

export class ModularStudioApp {
  constructor() {
    this.contract = null;
    this.world = null;
    this.audio = null;

    this.canvas = document.getElementById('studio-canvas');
    this.scopeCanvas = document.getElementById('scope-canvas');
    this.scopeCtx = this.scopeCanvas ? this.scopeCanvas.getContext('2d') : null;

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.lastFrameTimeMs = performance.now();

    // Scene lookups
    this.nodesByName = new Map();
    this.entityById = new Map();
    this.knobSpecsById = new Map();
    this.knobSpecsByNode = new Map();
    this.socketSpecsById = new Map();
    this.socketSpecsByNode = new Map();
    this.keySpecsById = new Map();
    this.keySpecsByNode = new Map();
    this.keySpecsByQwerty = new Map();
    this.keySpecsByMidi = new Map();

    // Runtime state
    this.knobValues = new Map();
    this.knobMeshes = [];
    this.socketMeshes = [];
    this.keyMeshes = [];
    this.turntableMeshes = [];
    this.cableGroup = new THREE.Group();
    this.cableGroup.name = 'Runtime_Patch_Cables';
    this.cableMeshes = new Map();
    this.socketRings = new Map();

    // Key animation state
    this.pressedKeys = new Set(); // midi notes
    this.keyAngles = new Map(); // midi_note -> current rad
    this.pointerActiveKeyMidi = null;

    // Interaction state
    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2();
    this.activeDrag = null;
    this.pendingPatchSocketId = null;
    this.previewCableMesh = null;

    // Input mode ('qwerty' | 'midi')
    this.inputMode = 'qwerty';
    this.midiAccess = null;
    this.midiStatusText = 'QWERTY Active (Z–M / Q–I)';

    // Camera transition state
    this.cameraTransition = null;
    this.activeCameraPresetId = 'opening_studio';
    this.currentPresetId = 'signature_patched_lead';

    // Turntable visual state
    this.platterAngleRad = 0;
    this.currentTonearmYawDeg = 0;
    this.currentTonearmPitchDeg = 5.5;

    // Verification & performance telemetry
    this.worldVerification = {
      pass: false,
      checkedCount: 0,
      mismatches: []
    };
    this.frameStats = {
      fps: 60,
      frameCount: 0,
      lastSampleTime: performance.now(),
      avgFrameTimeMs: 16.6
    };
  }

  async init() {
    this._setStatus('Loading contract.json & world.json records...', 'info');
    const [contractRes, worldRes] = await Promise.all([
      fetch('./contract.json'),
      fetch('./world.json')
    ]);
    this.contract = await contractRes.json();
    this.world = await worldRes.json();

    this._indexContractAndWorld();
    this.audio = new StudioAudioEngine(this.contract);

    this._initThreeScene();
    await this._loadStudioGLB();
    this._verifyWorldAgainstGLB();
    this._setupSocketCalloutRings();
    this._bindUIEvents();
    this._bindViewportEvents();
    this._bindKeyboardEvents();

    // Initialize default preset: 01. Signature 1974 Ladder Lead
    this.loadPreset('signature_patched_lead', { silentStatus: true });
    this._updateTurntableUI();
    this._setStatus(
      'Studio Ready — Click "ACTIVATE STUDIO AUDIO", turn VCF CUTOFF, press keys (Z–M / Q–I), patch sockets, or lower the tonearm.',
      'ok'
    );

    this.lastFrameTimeMs = performance.now();
    this._animate();
    window.studioApp = this;
    window.studioState = {
      ready: true,
      worldVerification: this.worldVerification
    };
  }

  _indexContractAndWorld() {
    for (const entity of this.world.entities) {
      this.entityById.set(entity.entity_id, entity);
    }
    for (const k of this.contract.knobs) {
      this.knobSpecsById.set(k.id, k);
      this.knobSpecsByNode.set(k.node_name, k);
      this.knobValues.set(k.id, k.default);
    }
    for (const s of this.contract.patch_sockets) {
      this.socketSpecsById.set(s.id, s);
      this.socketSpecsByNode.set(s.node_name, s);
    }
    for (const key of this.contract.keyboard.keys) {
      this.keySpecsById.set(key.id, key);
      this.keySpecsByNode.set(key.node_name, key);
      this.keySpecsByQwerty.set(key.qwerty_binding.toUpperCase(), key);
      this.keySpecsByMidi.set(key.midi_note, key);
      this.keyAngles.set(key.midi_note, 0);
    }
  }

  _initThreeScene() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0d0b0a);

    const w = this.canvas.clientWidth || window.innerWidth;
    const h = this.canvas.clientHeight || window.innerHeight;

    this.camera = new THREE.PerspectiveCamera(38, w / h, 0.02, 20.0);
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      powerPreference: 'high-performance',
      preserveDrawingBuffer: true
    });
    this.renderer.setSize(w, h, false);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.12;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFShadowMap;

    const pmrem = new THREE.PMREMGenerator(this.renderer);
    this.scene.environment = this._buildStudioEnvironmentMap(pmrem);
    this.scene.environmentIntensity = 1.15;

    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.09;
    this.controls.maxPolarAngle = Math.PI * 0.49;
    this.controls.minDistance = 0.22;
    this.controls.maxDistance = 2.2;

    this._setupStudioLights();
    this.scene.add(this.cableGroup);

    // Set opening camera from world.json
    this.setCameraPreset('opening_studio', true);
  }

  _buildStudioEnvironmentMap(pmrem) {
    // Custom 1974 dark-room recording studio environment:
    // Dark acoustic overhead ceiling so horizontal 180g vinyl & espresso leatherette stay deep black/espresso,
    // paired with grazing 3200K warm key, cool cyan fill, and amber rim softbox strips for sharp anisotropic highlights.
    const envScene = new THREE.Scene();
    envScene.background = new THREE.Color(0x060709);

    const addSoftbox = (w, h, colorHex, intensity, pos, look) => {
      const mat = new THREE.MeshBasicMaterial({
        color: new THREE.Color(colorHex).multiplyScalar(intensity),
        side: THREE.DoubleSide
      });
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat);
      mesh.position.set(...pos);
      mesh.lookAt(...look);
      envScene.add(mesh);
    };

    // Grazing warm 3200K key softbox (front-left, 32 deg elevation)
    addSoftbox(3.2, 1.4, 0xffd4a3, 5.2, [-3.0, 1.65, 2.4], [0, 0.1, 0]);
    // Grazing cool studio monitor/control-room glass reflection strip (front-right)
    addSoftbox(2.6, 1.2, 0x8ec0f0, 3.4, [2.9, 1.45, 2.1], [0.1, 0.1, 0]);
    // Grazing warm amber rim softbox (rear-right, highlights vinyl grooves & S-shaped chrome tonearm)
    addSoftbox(3.0, 1.3, 0xff9e3d, 4.8, [2.7, 1.30, -2.3], [0.2, 0.05, 0]);
    // Subtle warm rear-left accent strip for synth walnut cheek & chrome jack nuts
    addSoftbox(2.4, 1.1, 0xffb870, 2.8, [-2.5, 1.35, -2.0], [-0.2, 0.15, 0]);
    // Low warm wood bounce card
    addSoftbox(4.0, 1.5, 0x4a2c18, 1.1, [0.0, -1.5, 2.5], [0, 0.1, 0]);

    const tex = pmrem.fromScene(envScene, 0.03).texture;
    envScene.traverse((o) => {
      if (o.geometry) o.geometry.dispose();
      if (o.material) o.material.dispose();
    });
    return tex;
  }

  _setupStudioLights() {
    const hemi = new THREE.HemisphereLight(0xffe2c4, 0x120e0c, 0.34);
    this.scene.add(hemi);

    const keyLight = new THREE.DirectionalLight(0xffd8ad, 3.05);
    keyLight.name = 'Light_Key_Warm_Side';
    keyLight.position.set(-0.86, 0.92, 0.78);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 2048;
    keyLight.shadow.mapSize.height = 2048;
    keyLight.shadow.camera.near = 0.1;
    keyLight.shadow.camera.far = 3.5;
    const d = 0.95;
    keyLight.shadow.camera.left = -d;
    keyLight.shadow.camera.right = d;
    keyLight.shadow.camera.top = d;
    keyLight.shadow.camera.bottom = -d;
    keyLight.shadow.bias = -0.00035;
    keyLight.shadow.normalBias = 0.008;
    this.scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xb8d4f2, 0.85);
    fillLight.name = 'Light_Fill_Cool_Top';
    fillLight.position.set(0.74, 0.96, 0.78);
    this.scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0xff9c3b, 1.65);
    rimLight.name = 'Light_Rim_Turntable_Amber';
    rimLight.position.set(0.86, 0.56, -0.62);
    this.scene.add(rimLight);

    // Local neon-amber strobe prism light illuminating the spinning platter strobe dots
    const strobeLight = new THREE.PointLight(0xff5e14, 0.42, 0.24, 1.6);
    strobeLight.name = 'Light_Strobe_Prism_Neon';
    strobeLight.position.set(0.295, 0.066, 0.142);
    this.scene.add(strobeLight);
  }

  _upgradeMaterialsToPhysical(root) {
    const maxAniso = this.renderer.capabilities.getMaxAnisotropy();
    const upgradedBySource = new Map();

    root.traverse((obj) => {
      if (!obj.isMesh) return;
      obj.castShadow = true;
      obj.receiveShadow = true;

      if (obj.geometry && !obj.geometry.attributes.tangent && obj.geometry.attributes.uv && obj.geometry.index) {
        try {
          obj.geometry.computeTangents();
        } catch (_) {}
      }

      const boostTextures = (mat) => {
        for (const prop of ['map', 'normalMap', 'roughnessMap', 'metalnessMap']) {
          if (mat[prop]) {
            mat[prop].anisotropy = maxAniso;
            mat[prop].needsUpdate = true;
          }
        }
      };

      const upgradeOne = (srcMat) => {
        if (!srcMat) return srcMat;
        if (upgradedBySource.has(srcMat)) return upgradedBySource.get(srcMat);

        boostTextures(srcMat);
        const mName = srcMat.name || '';
        const phys = new THREE.MeshPhysicalMaterial({
          name: mName,
          color: srcMat.color ? srcMat.color.clone() : new THREE.Color(0xffffff),
          map: srcMat.map || null,
          normalMap: srcMat.normalMap || null,
          roughnessMap: srcMat.roughnessMap || null,
          metalnessMap: srcMat.metalnessMap || null,
          roughness: srcMat.roughness ?? 0.4,
          metalness: srcMat.metalness ?? 0.0,
          emissive: srcMat.emissive ? srcMat.emissive.clone() : new THREE.Color(0x000000),
          emissiveIntensity: srcMat.emissiveIntensity ?? 1.0
        });

        if (mName.includes('mat_vinyl_record')) {
          phys.color.setHex(0x050507);
          phys.roughness = 0.16;
          phys.metalness = 0.08;
          phys.clearcoat = 0.92;
          phys.clearcoatRoughness = 0.08;
          phys.anisotropy = 0.90;
          phys.normalScale = new THREE.Vector2(1.55, 1.55);
          phys.envMapIntensity = 1.48;
        } else if (mName.includes('mat_walnut_cabinet')) {
          phys.color.setHex(0xe2b288);
          phys.roughness = 0.34;
          phys.metalness = 0.0;
          phys.clearcoat = 0.48;
          phys.clearcoatRoughness = 0.20;
          phys.normalScale = new THREE.Vector2(1.25, 1.25);
          phys.envMapIntensity = 1.35;
        } else if (mName.includes('mat_turntable_deck')) {
          phys.roughnessMap = null;
          phys.metalnessMap = null;
          phys.color.setHex(0x181a1f);
          phys.roughness = 0.58;
          phys.metalness = 0.32;
          phys.specularIntensity = 0.32;
          phys.clearcoat = 0.04;
          phys.clearcoatRoughness = 0.45;
          phys.normalScale = new THREE.Vector2(0.35, 0.35);
          phys.envMapIntensity = 0.42;
        } else if (mName.includes('mat_anodised_panel')) {
          phys.roughness = 0.38;
          phys.metalness = 0.50;
          phys.clearcoat = 0.16;
          phys.clearcoatRoughness = 0.26;
          phys.normalScale = new THREE.Vector2(0.22, 0.22);
          phys.envMapIntensity = 1.22;
        } else if (mName.includes('mat_anodised_trim')) {
          phys.normalMap = null;
          phys.roughnessMap = null;
          phys.metalnessMap = null;
          phys.color.setHex(0x0f1114);
          phys.roughness = 0.78;
          phys.metalness = 0.12;
          phys.specularIntensity = 0.15;
          phys.clearcoat = 0.0;
          phys.envMapIntensity = 0.22;
        } else if (mName.includes('mat_chrome_fitting') || mName.includes('mat_spun_alum_cap')) {
          phys.normalMap = null;
          phys.roughness = 0.08;
          phys.metalness = 0.97;
          phys.clearcoat = 0.38;
          phys.clearcoatRoughness = 0.06;
          phys.envMapIntensity = 1.65;
        } else if (mName.includes('mat_bakelite_knob') || mName.includes('mat_ebony_key')) {
          phys.color.setHex(0x070709);
          phys.roughness = 0.18;
          phys.metalness = 0.04;
          phys.clearcoat = 0.72;
          phys.clearcoatRoughness = 0.12;
          phys.envMapIntensity = 1.40;
        } else if (mName.includes('mat_ivory_key')) {
          phys.roughness = 0.15;
          phys.metalness = 0.0;
          phys.clearcoat = 0.82;
          phys.clearcoatRoughness = 0.09;
          phys.envMapIntensity = 1.22;
        } else if (mName.includes('mat_studio_slate_desk')) {
          for (const prop of ['map', 'normalMap', 'roughnessMap']) {
            if (phys[prop]) {
              phys[prop].wrapS = THREE.RepeatWrapping;
              phys[prop].wrapT = THREE.RepeatWrapping;
              phys[prop].repeat.set(6, 4);
              phys[prop].needsUpdate = true;
            }
          }
          phys.color.setHex(0x161210);
          phys.roughness = 0.74;
          phys.metalness = 0.02;
          phys.clearcoat = 0.06;
          phys.clearcoatRoughness = 0.45;
          phys.normalScale = new THREE.Vector2(0.34, 0.34);
          phys.envMapIntensity = 0.55;
        }

        upgradedBySource.set(srcMat, phys);
        return phys;
      };

      if (Array.isArray(obj.material)) {
        obj.material = obj.material.map(upgradeOne);
      } else if (obj.material) {
        obj.material = upgradeOne(obj.material);
      }
    });
  }

  async _loadStudioGLB() {
    const loader = new GLTFLoader();
    const gltf = await new Promise((resolve, reject) => {
      loader.load('./assets/models/studio_scene.glb', resolve, undefined, reject);
    });

    this.studioRoot = gltf.scene;
    this.scene.add(this.studioRoot);

    this.studioRoot.traverse((obj) => {
      if (obj.name) {
        this.nodesByName.set(obj.name, obj);
      }
    });
    this._upgradeMaterialsToPhysical(this.studioRoot);

    for (const k of this.contract.knobs) {
      const node = this.nodesByName.get(k.node_name);
      if (node) {
        node.userData.interactionType = 'knob';
        node.userData.knobSpec = k;
        this.knobMeshes.push(node);
        this._applyKnobAngle(k.id, k.default);
      }
    }

    for (const s of this.contract.patch_sockets) {
      const node = this.nodesByName.get(s.node_name);
      if (node) {
        node.userData.interactionType = 'socket';
        node.userData.socketSpec = s;
        this.socketMeshes.push(node);
      }
    }

    for (const key of this.contract.keyboard.keys) {
      const node = this.nodesByName.get(key.node_name);
      if (node) {
        node.userData.interactionType = 'key';
        node.userData.keySpec = key;
        this.keyMeshes.push(node);
      }
    }

    const ttNodes = [
      'Turntable_Platter',
      'Tonearm_Gimbal',
      'Tonearm_Headshell',
      'Turntable_SpeedSwitch',
      'Turntable_StartStop'
    ];
    for (const name of ttNodes) {
      const node = this.nodesByName.get(name);
      if (node) {
        node.userData.interactionType = 'turntable';
        node.userData.turntablePart = name;
        this.turntableMeshes.push(node);
      }
    }
  }

  _verifyWorldAgainstGLB() {
    const mismatches = [];
    let checked = 0;

    for (const entity of this.world.entities) {
      checked++;
      const node = this.nodesByName.get(entity.node_name);
      if (!node) {
        mismatches.push(`Missing node ${entity.node_name} (${entity.entity_id})`);
        continue;
      }

      if (entity.parent_id) {
        const expectedParent = this.entityById.get(entity.parent_id);
        const actualParentName = node.parent ? node.parent.name : null;
        if (!expectedParent || actualParentName !== expectedParent.node_name) {
          mismatches.push(
            `Parent mismatch on ${entity.node_name}: expected ${expectedParent?.node_name}, got ${actualParentName}`
          );
        }
      }

      const [ex, ey, ez] = entity.position_m;
      const dx = Math.abs(node.position.x - ex);
      const dy = Math.abs(node.position.y - ey);
      const dz = Math.abs(node.position.z - ez);
      if (Math.max(dx, dy, dz) > 0.0025) {
        mismatches.push(
          `Position drift on ${entity.node_name}: expected [${ex}, ${ey}, ${ez}], got [${node.position.x.toFixed(4)}, ${node.position.y.toFixed(4)}, ${node.position.z.toFixed(4)}]`
        );
      }
    }

    this.worldVerification = {
      pass: mismatches.length === 0,
      checkedCount: checked,
      mismatches
    };

    const badge = document.getElementById('world-verify-badge');
    if (badge) {
      badge.textContent = this.worldVerification.pass
        ? `WORLD.JSON VERIFIED (${checked}/64 NODES)`
        : `WORLD VERIFY ERR (${mismatches.length})`;
      badge.classList.toggle('badge-ok', this.worldVerification.pass);
    }
  }

  _setupSocketCalloutRings() {
    const ringGeo = new THREE.RingGeometry(0.0076, 0.0094, 24);
    for (const s of this.contract.patch_sockets) {
      const node = this.nodesByName.get(s.node_name);
      if (!node) continue;
      const isOut = s.direction === 'output';
      const ringMat = new THREE.MeshBasicMaterial({
        color: isOut ? 0xf0a948 : 0x5ab0d8,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.25
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.position.set(0, 0, 0.0018);
      node.add(ring);
      this.socketRings.set(s.id, ring);
    }
  }

  _hasCable(fromId, toId) {
    return this.audio.cables.some(
      (c) => c.fromSocketId === fromId && c.toSocketId === toId
    );
  }

  _updateSocketRingHighlights() {
    const vco1Patched = this._hasCable('socket_vco1_out', 'socket_vcf_in');
    const pulse = 0.5 + 0.5 * Math.sin(performance.now() * 0.006);

    for (const s of this.contract.patch_sockets) {
      const ring = this.socketRings.get(s.id);
      if (!ring) continue;

      if (this.pendingPatchSocketId === s.id) {
        ring.material.color.setHex(0x48f08b);
        ring.material.opacity = 0.95;
        ring.scale.setScalar(1.22);
      } else if (
        !vco1Patched &&
        (s.id === 'socket_vco1_out' || s.id === 'socket_vcf_in')
      ) {
        ring.material.color.setHex(0xffb84d);
        ring.material.opacity = 0.45 + 0.45 * pulse;
        ring.scale.setScalar(1.06 + 0.10 * pulse);
      } else {
        const isOut = s.direction === 'output';
        ring.material.color.setHex(isOut ? 0xf0a948 : 0x5ab0d8);
        ring.material.opacity = 0.22;
        ring.scale.setScalar(1.0);
      }
    }
  }

  // ============================================================================
  // CAMERA PRESETS
  // ============================================================================
  setCameraPreset(presetId, immediate = false) {
    const preset = this.world.camera_presets.find((p) => p.preset_id === presetId);
    if (!preset) return false;

    this.activeCameraPresetId = presetId;
    document.querySelectorAll('[data-camera-preset]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.cameraPreset === presetId);
    });

    const targetPos = new THREE.Vector3(...preset.position_m);
    const targetLook = new THREE.Vector3(...preset.target_m);

    if (immediate) {
      const prevDamping = this.controls.enableDamping;
      this.controls.enableDamping = false;
      this.camera.position.copy(targetPos);
      this.camera.fov = preset.fov_deg;
      this.camera.updateProjectionMatrix();
      this.controls.target.copy(targetLook);
      this.controls.update();
      this.controls.enableDamping = prevDamping;
      this.cameraTransition = null;
      return true;
    }

    this.cameraTransition = {
      startPos: this.camera.position.clone(),
      endPos: targetPos,
      startTarget: this.controls.target.clone(),
      endTarget: targetLook,
      startFov: this.camera.fov,
      endFov: preset.fov_deg,
      elapsed: 0,
      duration: 0.42
    };
    return true;
  }

  // ============================================================================
  // KNOB VALUE <-> ANGLE MAPPING
  // ============================================================================
  _valueToNormalized(spec, value) {
    const clamped = Math.max(spec.min, Math.min(spec.max, value));
    if (spec.scale === 'log' && spec.min > 0) {
      return Math.log(clamped / spec.min) / Math.log(spec.max / spec.min);
    }
    return (clamped - spec.min) / (spec.max - spec.min);
  }

  _normalizedToValue(spec, norm) {
    const t = Math.max(0, Math.min(1, norm));
    if (spec.scale === 'log' && spec.min > 0) {
      return spec.min * Math.pow(spec.max / spec.min, t);
    }
    return spec.min + t * (spec.max - spec.min);
  }

  _applyKnobAngle(knobId, value) {
    const spec = this.knobSpecsById.get(knobId);
    if (!spec) return;
    const node = this.nodesByName.get(spec.node_name);
    if (!node) return;

    const norm = this._valueToNormalized(spec, value);
    const angleDeg =
      spec.angle_min_deg + norm * (spec.angle_max_deg - spec.angle_min_deg);
    node.rotation.z = -THREE.MathUtils.degToRad(angleDeg);
  }

  setKnobValue(knobId, value, { announce = false, immediate = false } = {}) {
    const spec = this.knobSpecsById.get(knobId);
    if (!spec) return null;
    const clamped = this.audio.setKnobValue(knobId, Number(value), immediate);
    this.knobValues.set(knobId, clamped);
    this._applyKnobAngle(knobId, clamped);

    if (announce) {
      this._updateReadout(
        `${spec.label}: ${this._formatKnobValue(spec, clamped)}`
      );
    }
    return clamped;
  }

  _formatKnobValue(spec, val) {
    if (spec.unit === 'Hz') {
      return val >= 100 ? `${val.toFixed(0)} Hz` : `${val.toFixed(2)} Hz`;
    }
    if (spec.unit === 's') {
      return val < 0.1 ? `${(val * 1000).toFixed(0)} ms` : `${val.toFixed(2)} s`;
    }
    if (spec.unit === 'st' || spec.unit === 'ct') {
      const sign = val > 0 ? '+' : '';
      return `${sign}${val.toFixed(1)} ${spec.unit}`;
    }
    return `${val.toFixed(2)} ${spec.unit}`;
  }

  // ============================================================================
  // PATCH CABLES (3D DROOPING CATENARY WITH RACK CLEARANCE)
  // ============================================================================
  patchSockets(sourceSocketId, targetSocketId) {
    const sSpec = this.socketSpecsById.get(sourceSocketId);
    const tSpec = this.socketSpecsById.get(targetSocketId);
    if (!sSpec || !tSpec) {
      return { valid: false, code: 'unknown_socket', message: 'Unknown socket ID.' };
    }

    const outId = sSpec.direction === 'output' ? sourceSocketId : targetSocketId;
    const inId = sSpec.direction === 'input' ? sourceSocketId : targetSocketId;
    if (
      sSpec.direction !== tSpec.direction &&
      this._hasCable(outId, inId)
    ) {
      this.disconnectCable(outId, inId);
      const msg = `Disconnected patch cable: ${sSpec.label} ✕ ${tSpec.label}`;
      this._setStatus(msg, 'info');
      return { valid: true, action: 'disconnected', message: msg };
    }

    const res = this.audio.addPatchCable(sourceSocketId, targetSocketId);
    if (!res.valid) {
      this._setStatus(`Patch Rejected (${res.code}): ${res.message}`, 'warn');
      return res;
    }

    this._rebuildCableMeshes();
    this._renderPatchListUI();
    this._updateSocketRingHighlights();

    this._setStatus(res.message, 'ok');
    return res;
  }

  disconnectCable(fromSocketId, toSocketId) {
    const cableId = `cable_${fromSocketId}__${toSocketId}`;
    const removed = this.audio.removePatchCable(cableId);
    if (removed) {
      this._rebuildCableMeshes();
      this._renderPatchListUI();
      this._updateSocketRingHighlights();
    }
    return removed;
  }

  clearCables() {
    this.audio.clearAllCables();
    this.pendingPatchSocketId = null;
    this._removePreviewCable();
    this._rebuildCableMeshes();
    this._renderPatchListUI();
    this._updateSocketRingHighlights();
    this._setStatus(
      'Cleared all patch cables. Click VCO 1 OUT → VCF AUDIO IN to patch the oscillator into the filter.',
      'info'
    );
  }

  _buildCatenaryCurvePoints(startWorld, endWorld, faceplateNormal, cableIdx = 0, srcStackIdx = 0, dstStackIdx = 0) {
    const p0 = startWorld.clone().addScaledVector(faceplateNormal, 0.022 + srcStackIdx * 0.014);
    const p1 = endWorld.clone().addScaledVector(faceplateNormal, 0.022 + dstStackIdx * 0.014);

    const dist = p0.distanceTo(p1);
    const horizDist = Math.abs(p1.x - p0.x);
    // Long cross-bay cables travel through the clear horizontal channel halfway between the upper [OUT]
    // and lower [IN] socket rows so intermediate upper sockets (ENV CV OUT, LFO CV OUT) and lower sockets
    // (VCA AUDIO IN, VCA GAIN CV) and their labels remain completely unobstructed.
    const isLongCrossBay = horizDist > 0.26;
    const laneOffset = (cableIdx % 5 - 2.0) * 0.0022;
    const corridorY = (p0.y + p1.y) * 0.5 - 0.005 + laneOffset;
    const verticalOffset = -Math.min(0.014, Math.max(0.008, dist * 0.08));
    const forwardClearance = 0.038 + Math.min(0.034, dist * 0.10) + cableIdx * 0.0052;

    const points = [];
    const segments = 28;
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const pt = new THREE.Vector3().lerpVectors(p0, p1, t);
      const weight = Math.sin(Math.PI * t);
      if (isLongCrossBay) {
        const plateau = Math.pow(weight, 0.52);
        pt.y = THREE.MathUtils.lerp(pt.y, corridorY, plateau * 0.88);
      } else {
        const archWeight = 4 * t * (1 - t);
        pt.y += verticalOffset * archWeight;
      }
      pt.addScaledVector(faceplateNormal, forwardClearance * weight);
      points.push(pt);
    }
    return points;
  }

  _getCableBraidNormalMap() {
    if (this._cableBraidNormal) return this._cableBraidNormal;
    const size = 64;
    const data = new Uint8Array(size * size * 4);
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const u = (x / size) * Math.PI * 8;
        const v = (y / size) * Math.PI * 8;
        const nx = Math.cos(u + v) * 0.35;
        const ny = Math.sin(u - v) * 0.35;
        const idx = (y * size + x) * 4;
        data[idx] = Math.round((nx * 0.5 + 0.5) * 255);
        data[idx + 1] = Math.round((ny * 0.5 + 0.5) * 255);
        data[idx + 2] = 235;
        data[idx + 3] = 255;
      }
    }
    const tex = new THREE.DataTexture(data, size, size, THREE.RGBAFormat);
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(24, 3);
    tex.needsUpdate = true;
    this._cableBraidNormal = tex;
    return tex;
  }

  _createCableObject(sourceNode, targetNode, colorHex, cableIdx = 0, srcStackIdx = 0, dstStackIdx = 0) {
    const group = new THREE.Group();

    const startWorld = new THREE.Vector3();
    const endWorld = new THREE.Vector3();
    sourceNode.getWorldPosition(startWorld);
    targetNode.getWorldPosition(endWorld);

    const tiltRad = THREE.MathUtils.degToRad(
      this.contract.units.rack_backward_tilt_deg || 15.0
    );
    const faceplateNormal = new THREE.Vector3(
      0,
      Math.sin(tiltRad),
      Math.cos(tiltRad)
    ).normalize();

    const points = this._buildCatenaryCurvePoints(
      startWorld,
      endWorld,
      faceplateNormal,
      cableIdx,
      srcStackIdx,
      dstStackIdx
    );
    const curve = new THREE.CatmullRomCurve3(points);
    const tubeGeo = new THREE.TubeGeometry(curve, 32, 0.0038, 12, false);
    const tubeMat = new THREE.MeshPhysicalMaterial({
      color: colorHex,
      roughness: 0.52,
      metalness: 0.04,
      sheen: 0.55,
      sheenRoughness: 0.45,
      normalMap: this._getCableBraidNormalMap(),
      normalScale: new THREE.Vector2(0.45, 0.45)
    });
    const tubeMesh = new THREE.Mesh(tubeGeo, tubeMat);
    tubeMesh.castShadow = true;
    group.add(tubeMesh);

    const barrelGeo = new THREE.CylinderGeometry(0.0056, 0.0056, 0.015, 20);
    barrelGeo.rotateX(Math.PI / 2);
    const barrelMat = new THREE.MeshPhysicalMaterial({
      color: 0xdce2ea,
      roughness: 0.14,
      metalness: 0.94,
      clearcoat: 0.3
    });

    const bootGeo = new THREE.CylinderGeometry(0.0044, 0.0054, 0.011, 16);
    bootGeo.rotateX(Math.PI / 2);
    const bootMat = new THREE.MeshPhysicalMaterial({
      color: colorHex,
      roughness: 0.34,
      metalness: 0.05,
      clearcoat: 0.35
    });

    for (const [anchor, stackIdx] of [[startWorld, srcStackIdx], [endWorld, dstStackIdx]]) {
      const stackShift = stackIdx * 0.014;
      const barrel = new THREE.Mesh(barrelGeo, barrelMat);
      barrel.position.copy(anchor).addScaledVector(faceplateNormal, 0.009 + stackShift);
      barrel.lookAt(barrel.position.clone().add(faceplateNormal));
      group.add(barrel);

      const boot = new THREE.Mesh(bootGeo, bootMat);
      boot.position.copy(anchor).addScaledVector(faceplateNormal, 0.019 + stackShift);
      boot.lookAt(boot.position.clone().add(faceplateNormal));
      group.add(boot);
    }

    return group;
  }

  _rebuildCableMeshes() {
    while (this.cableGroup.children.length > 0) {
      const child = this.cableGroup.children.pop();
      child.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) obj.material.dispose();
      });
    }
    this.cableMeshes.clear();

    const socketStackCounts = new Map();
    let colorIdx = 0;
    for (const cable of this.audio.cables) {
      const sSpec = this.socketSpecsById.get(cable.fromSocketId);
      const tSpec = this.socketSpecsById.get(cable.toSocketId);
      if (!sSpec || !tSpec) continue;

      const sNode = this.nodesByName.get(sSpec.node_name);
      const tNode = this.nodesByName.get(tSpec.node_name);
      if (!sNode || !tNode) continue;

      const srcStackIdx = socketStackCounts.get(cable.fromSocketId) || 0;
      socketStackCounts.set(cable.fromSocketId, srcStackIdx + 1);
      const dstStackIdx = socketStackCounts.get(cable.toSocketId) || 0;
      socketStackCounts.set(cable.toSocketId, dstStackIdx + 1);

      const palette = CABLE_PALETTE[colorIdx % CABLE_PALETTE.length];
      const curIdx = colorIdx;
      colorIdx++;

      const cableObj = this._createCableObject(sNode, tNode, palette.hex, curIdx, srcStackIdx, dstStackIdx);
      cableObj.name = `Cable_${cable.fromSocketId}_${cable.toSocketId}`;
      this.cableGroup.add(cableObj);
      this.cableMeshes.set(cable.id, {
        mesh: cableObj,
        color: palette,
        sourceSpec: sSpec,
        targetSpec: tSpec
      });
    }
  }

  _updatePreviewCable(cursorWorldPoint) {
    this._removePreviewCable();
    if (!this.pendingPatchSocketId || !cursorWorldPoint) return;

    const sSpec = this.socketSpecsById.get(this.pendingPatchSocketId);
    const sNode = sSpec ? this.nodesByName.get(sSpec.node_name) : null;
    if (!sNode) return;

    const startWorld = new THREE.Vector3();
    sNode.getWorldPosition(startWorld);

    const tiltRad = THREE.MathUtils.degToRad(15.0);
    const faceplateNormal = new THREE.Vector3(
      0,
      Math.sin(tiltRad),
      Math.cos(tiltRad)
    ).normalize();

    const points = this._buildCatenaryCurvePoints(
      startWorld,
      cursorWorldPoint,
      faceplateNormal
    );
    const curve = new THREE.CatmullRomCurve3(points);
    const geo = new THREE.TubeGeometry(curve, 20, 0.0032, 8, false);
    const mat = new THREE.MeshBasicMaterial({
      color: 0x48f08b,
      transparent: true,
      opacity: 0.78
    });
    this.previewCableMesh = new THREE.Mesh(geo, mat);
    this.scene.add(this.previewCableMesh);
  }

  _removePreviewCable() {
    if (this.previewCableMesh) {
      this.scene.remove(this.previewCableMesh);
      this.previewCableMesh.geometry.dispose();
      this.previewCableMesh.material.dispose();
      this.previewCableMesh = null;
    }
  }

  // ============================================================================
  // PRESETS & STUDIO RESET
  // ============================================================================
  loadPreset(presetId, { silentStatus = false } = {}) {
    const presetSpec = this.contract.audio_graph.presets.find(
      (p) => p.id === presetId
    );
    const ok = this.audio.loadPreset(presetId);
    if (!ok || !presetSpec) return false;

    this.currentPresetId = presetId;
    for (const k of this.contract.knobs) {
      const val = this.audio.knobValues[k.id];
      this.knobValues.set(k.id, val);
      this._applyKnobAngle(k.id, val);
    }

    this.pendingPatchSocketId = null;
    this._removePreviewCable();
    this._rebuildCableMeshes();
    this._renderPatchListUI();
    this._updateSocketRingHighlights();

    const sel = document.getElementById('preset-select');
    if (sel && sel.value !== presetId) {
      sel.value = presetId;
    }

    if (presetId === 'phono_through_filter') {
      this.setTurntablePower(true);
      this.setTonearmLowered(true);
    }

    if (!silentStatus) {
      this._setStatus(`Loaded Preset: ${presetSpec.name}`, 'ok');
    }
    return true;
  }

  resetStudio() {
    this.pressedKeys.clear();
    this.pointerActiveKeyMidi = null;
    this.pendingPatchSocketId = null;
    this._removePreviewCable();

    this.audio.resetAllSound();
    this.loadPreset('signature_unpatched', { silentStatus: true });
    this._updateTurntableUI();
    this._setStatus(
      'Studio Reset: All active notes and turntable playback stopped and released.',
      'info'
    );
  }

  // ============================================================================
  // KEYBOARD NOTE ON / OFF
  // ============================================================================
  async noteOn(midiNote, source = 'pointer') {
    const keySpec = this.keySpecsByMidi.get(Number(midiNote));
    if (!keySpec) return;

    if (!this.audio.isActivated) {
      await this.activateAudio();
    }

    this.pressedKeys.add(keySpec.midi_note);
    this.audio.noteOn(keySpec.midi_note, source);
    this._updateReadout(
      `KEY ${keySpec.note_name} (${keySpec.frequency_hz.toFixed(1)} Hz) — MIDI ${keySpec.midi_note}`
    );
  }

  noteOff(midiNote, source = 'pointer') {
    const midi = Number(midiNote);
    this.audio.noteOff(midi, source);
    if (!this.audio.activeNotes.has(midi)) {
      this.pressedKeys.delete(midi);
    }
  }

  releaseAllNotes() {
    this.pressedKeys.clear();
    this.pointerActiveKeyMidi = null;
    if (this.audio) {
      this.audio.releaseAllNotes();
    }
  }

  // ============================================================================
  // TURNTABLE CONTROLS
  // ============================================================================
  async setTurntablePower(motorOn) {
    if (motorOn && !this.audio.isActivated) {
      await this.activateAudio();
    }
    this.audio.setTurntableMotor(motorOn);
    this._updateTurntableUI();
    const rpmLabel = this.audio.rpm > 40 ? '45' : '33⅓';
    this._setStatus(
      this.audio.motorOn
        ? `Turntable Platter Spinning (${rpmLabel} RPM) — ${this.audio.tonearmLowered ? 'Playing Record' : 'Lower Tonearm to Play'}`
        : 'Turntable Motor Stopped.',
      'info'
    );
    return this.audio.turntableState;
  }

  async setTonearmLowered(lowered) {
    if (lowered && !this.audio.isActivated) {
      await this.activateAudio();
    }
    this.audio.setTonearmLowered(lowered);
    this._updateTurntableUI();
    const rpmLabel = this.audio.rpm > 40 ? '45' : '33⅓';
    this._setStatus(
      this.audio.tonearmLowered
        ? `Tonearm Stylus Lowered onto Record (${rpmLabel} RPM, rate=${this.audio.getPlaybackRate().toFixed(2)}x)`
        : 'Tonearm Raised & Cued.',
      'ok'
    );
    return this.audio.turntableState;
  }

  setTurntableSpeed(rpmKey) {
    this.audio.setTurntableRpm(rpmKey);
    const swNode = this.nodesByName.get('Turntable_SpeedSwitch');
    if (swNode) {
      swNode.rotation.y = Number(rpmKey) > 40 ? -0.55 : 0.0;
    }
    this._updateTurntableUI();
    const is45 = this.audio.rpm > 40;
    this._setStatus(
      `Turntable Speed: ${is45 ? '45 RPM (1.35x pitch/speed)' : '33⅓ RPM (1.00x native)'} — Position preserved at ${this.audio.getTurntablePlaybackPositionSec().toFixed(2)}s`,
      'ok'
    );
    return this.audio.turntableState;
  }

  _updateTurntableUI() {
    const powerBtn = document.getElementById('btn-tt-power');
    const armBtn = document.getElementById('btn-tt-tonearm');
    const rpm33Btn = document.getElementById('btn-tt-33');
    const rpm45Btn = document.getElementById('btn-tt-45');
    const stateEl = document.getElementById('tt-state-readout');
    const is45 = this.audio.rpm > 40;

    if (powerBtn) {
      powerBtn.textContent = this.audio.motorOn ? 'STOP PLATTER' : 'START PLATTER';
      powerBtn.classList.toggle('active', this.audio.motorOn);
    }
    if (armBtn) {
      armBtn.textContent = this.audio.tonearmLowered ? 'LIFT TONEARM' : 'LOWER TONEARM';
      armBtn.classList.toggle('active', this.audio.tonearmLowered);
    }
    if (rpm33Btn) rpm33Btn.classList.toggle('active', !is45);
    if (rpm45Btn) rpm45Btn.classList.toggle('active', is45);
    if (stateEl) {
      stateEl.textContent = `${this.audio.turntableState.toUpperCase()} · ${is45 ? '45' : '33⅓'} RPM`;
    }
  }

  // ============================================================================
  // AUDIO ACTIVATION & MIDI INPUT
  // ============================================================================
  async activateAudio() {
    await this.audio.initAndResume();
    const btn = document.getElementById('btn-activate-audio');
    if (btn) {
      btn.textContent = 'AUDIO ENGINE RUNNING (44.1 kHz)';
      btn.classList.add('activated');
    }
    return this.audio.isActivated;
  }

  async setInputMode(mode) {
    this.releaseAllNotes();
    this.inputMode = mode;

    const btnQwerty = document.getElementById('btn-input-qwerty');
    const btnMidi = document.getElementById('btn-input-midi');
    const statusEl = document.getElementById('input-mode-status');

    if (btnQwerty) btnQwerty.classList.toggle('active', mode === 'qwerty');
    if (btnMidi) btnMidi.classList.toggle('active', mode === 'midi');

    if (mode === 'qwerty') {
      this.midiStatusText = 'QWERTY Active (Keys Z–M = C3–B3, Q–I = C4–C5)';
      if (statusEl) statusEl.textContent = this.midiStatusText;
      return { mode: 'qwerty', available: true, status: this.midiStatusText };
    }

    if (!navigator.requestMIDIAccess) {
      this.midiStatusText = 'MIDI UNAVAILABLE: Browser does not support Web MIDI API (QWERTY fallback active)';
      if (statusEl) statusEl.textContent = this.midiStatusText;
      this._setStatus(this.midiStatusText, 'warn');
      return { mode: 'midi', available: false, status: this.midiStatusText };
    }

    try {
      this.midiAccess = await navigator.requestMIDIAccess();
      const inputs = Array.from(this.midiAccess.inputs.values());
      if (inputs.length === 0) {
        this.midiStatusText = 'MIDI UNAVAILABLE: 0 hardware MIDI inputs connected (QWERTY still active)';
        if (statusEl) statusEl.textContent = this.midiStatusText;
        this._setStatus(this.midiStatusText, 'warn');
        return { mode: 'midi', available: false, inputs: 0, status: this.midiStatusText };
      }

      for (const input of inputs) {
        input.onmidimessage = (evt) => this._onMidiMessage(evt);
      }
      this.midiStatusText = `MIDI Active (${inputs.length} device: ${inputs[0].name || 'MIDI In'})`;
      if (statusEl) statusEl.textContent = this.midiStatusText;
      this._setStatus(this.midiStatusText, 'ok');
      return { mode: 'midi', available: true, inputs: inputs.length, status: this.midiStatusText };
    } catch (err) {
      this.midiStatusText = `MIDI UNAVAILABLE: Permission denied or blocked (${err.message})`;
      if (statusEl) statusEl.textContent = this.midiStatusText;
      this._setStatus(this.midiStatusText, 'warn');
      return { mode: 'midi', available: false, status: this.midiStatusText };
    }
  }

  _onMidiMessage(event) {
    const [status, data1, data2] = event.data;
    const cmd = status & 0xf0;
    if (cmd === 0x90 && data2 > 0) {
      this.noteOn(data1, `midi:${data1}`);
    } else if (cmd === 0x80 || (cmd === 0x90 && data2 === 0)) {
      this.noteOff(data1, `midi:${data1}`);
    }
  }

  // ============================================================================
  // UI & VIEWPORT EVENTS
  // ============================================================================
  _bindUIEvents() {
    document
      .getElementById('btn-activate-audio')
      ?.addEventListener('click', () => this.activateAudio());

    document
      .getElementById('preset-select')
      ?.addEventListener('change', (e) => this.loadPreset(e.target.value));

    document
      .getElementById('btn-signature-patch')
      ?.addEventListener('click', async () => {
        if (!this.audio.isActivated) await this.activateAudio();
        if (!this._hasCable('socket_vco1_out', 'socket_vcf_in')) {
          this.patchSockets('socket_vco1_out', 'socket_vcf_in');
        } else {
          this._setStatus(
            'VCO 1 OUT → VCF AUDIO IN is connected! Press any key (Z–M / Q–I) and turn VCF CUTOFF.',
            'ok'
          );
        }
      });

    document
      .getElementById('btn-clear-cables')
      ?.addEventListener('click', () => this.clearCables());

    document
      .getElementById('btn-reset-studio')
      ?.addEventListener('click', () => this.resetStudio());

    document
      .getElementById('slider-master-vol')
      ?.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        this.audio.setMasterVolume(val);
        const lbl = document.getElementById('val-master-vol');
        if (lbl) lbl.textContent = `${Math.round(val * 100)}%`;
      });

    document.getElementById('btn-mute')?.addEventListener('click', (e) => {
      const muted = !this.audio.isMuted;
      this.audio.setMuted(muted);
      e.currentTarget.textContent = muted ? 'UNMUTE' : 'MUTE';
      e.currentTarget.classList.toggle('danger', muted);
    });

    document.querySelectorAll('[data-camera-preset]').forEach((btn) => {
      btn.addEventListener('click', () =>
        this.setCameraPreset(btn.dataset.cameraPreset)
      );
    });

    document
      .getElementById('btn-tt-power')
      ?.addEventListener('click', () =>
        this.setTurntablePower(!this.audio.motorOn)
      );
    document
      .getElementById('btn-tt-tonearm')
      ?.addEventListener('click', () =>
        this.setTonearmLowered(!this.audio.tonearmLowered)
      );
    document
      .getElementById('btn-tt-33')
      ?.addEventListener('click', () => this.setTurntableSpeed('33'));
    document
      .getElementById('btn-tt-45')
      ?.addEventListener('click', () => this.setTurntableSpeed('45'));

    document
      .getElementById('btn-input-qwerty')
      ?.addEventListener('click', () => this.setInputMode('qwerty'));
    document
      .getElementById('btn-input-midi')
      ?.addEventListener('click', () => this.setInputMode('midi'));
  }

  _bindKeyboardEvents() {
    window.addEventListener('keydown', (e) => {
      if (e.repeat || e.ctrlKey || e.metaKey || e.altKey) return;
      if (
        document.activeElement &&
        ['INPUT', 'SELECT', 'TEXTAREA'].includes(document.activeElement.tagName)
      ) {
        return;
      }
      const keyChar = e.key.toUpperCase();
      const spec = this.keySpecsByQwerty.get(keyChar);
      if (spec) {
        e.preventDefault();
        this.noteOn(spec.midi_note, `qwerty:${keyChar}`);
      }
    });

    window.addEventListener('keyup', (e) => {
      const keyChar = e.key.toUpperCase();
      const spec = this.keySpecsByQwerty.get(keyChar);
      if (spec) {
        this.noteOff(spec.midi_note, `qwerty:${keyChar}`);
      }
    });

    window.addEventListener('blur', () => this.releaseAllNotes());
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) this.releaseAllNotes();
    });
  }

  _updatePointerCoords(event) {
    const rect = this.canvas.getBoundingClientRect();
    this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  }

  _findInteractiveHit(event) {
    this._updatePointerCoords(event);
    this.raycaster.setFromCamera(this.pointer, this.camera);

    const targets = [
      ...this.knobMeshes,
      ...this.socketMeshes,
      ...this.keyMeshes,
      ...this.turntableMeshes
    ];
    const intersects = this.raycaster.intersectObjects(targets, true);
    if (intersects.length === 0) return null;

    for (const hit of intersects) {
      let cur = hit.object;
      while (cur && !cur.userData?.interactionType) {
        cur = cur.parent;
      }
      if (cur && cur.userData?.interactionType) {
        return { rootNode: cur, point: hit.point };
      }
    }
    return null;
  }

  _bindViewportEvents() {
    this.canvas.addEventListener('pointerdown', async (e) => {
      if (e.button !== 0) return;
      const hit = this._findInteractiveHit(e);

      if (!hit) {
        if (this.pendingPatchSocketId) {
          this.pendingPatchSocketId = null;
          this._removePreviewCable();
          this._updateSocketRingHighlights();
          this._setStatus('Cancelled pending cable patch.', 'info');
        }
        return;
      }

      const { rootNode } = hit;
      const type = rootNode.userData.interactionType;

      if (type === 'knob') {
        const spec = rootNode.userData.knobSpec;
        this.controls.enabled = false;
        this.activeDrag = {
          type: 'knob',
          spec,
          startY: e.clientY,
          startX: e.clientX,
          startNorm: this._valueToNormalized(
            spec,
            this.knobValues.get(spec.id)
          )
        };
        this.canvas.setPointerCapture(e.pointerId);
        this._updateReadout(
          `${spec.label}: ${this._formatKnobValue(spec, this.knobValues.get(spec.id))}`
        );
      } else if (type === 'socket') {
        const spec = rootNode.userData.socketSpec;
        if (!this.pendingPatchSocketId) {
          this.pendingPatchSocketId = spec.id;
          this._updateSocketRingHighlights();
          this._setStatus(
            `Patching from ${spec.label} (${spec.port_type}) — Click destination socket to connect...`,
            'info'
          );
        } else {
          const fromId = this.pendingPatchSocketId;
          this.pendingPatchSocketId = null;
          this._removePreviewCable();
          this.patchSockets(fromId, spec.id);
        }
      } else if (type === 'key') {
        const spec = rootNode.userData.keySpec;
        this.controls.enabled = false;
        this.activeDrag = { type: 'key', pointerId: e.pointerId };
        this.pointerActiveKeyMidi = spec.midi_note;
        this.canvas.setPointerCapture(e.pointerId);
        await this.noteOn(spec.midi_note, 'pointer');
      } else if (type === 'turntable') {
        const part = rootNode.userData.turntablePart;
        if (part === 'Turntable_StartStop') {
          await this.setTurntablePower(!this.audio.motorOn);
        } else if (part === 'Turntable_SpeedSwitch') {
          const nextRpm = this.audio.rpm > 40 ? '33' : '45';
          this.setTurntableSpeed(nextRpm);
        } else if (part === 'Tonearm_Gimbal' || part === 'Tonearm_Headshell') {
          await this.setTonearmLowered(!this.audio.tonearmLowered);
        } else if (part === 'Turntable_Platter') {
          if (!this.audio.motorOn) {
            await this.setTurntablePower(true);
          } else {
            await this.setTonearmLowered(!this.audio.tonearmLowered);
          }
        }
      }
    });

    this.canvas.addEventListener('pointermove', (e) => {
      if (this.activeDrag?.type === 'knob') {
        const { spec, startY, startX, startNorm } = this.activeDrag;
        const dy = (startY - e.clientY) / 150;
        const dx = (e.clientX - startX) / 220;
        const nextNorm = Math.max(0, Math.min(1, startNorm + dy + dx));
        const nextVal = this._normalizedToValue(spec, nextNorm);
        this.setKnobValue(spec.id, nextVal, { announce: true });
        return;
      }

      if (this.activeDrag?.type === 'key') {
        const hit = this._findInteractiveHit(e);
        const hoveredMidi =
          hit?.rootNode?.userData?.interactionType === 'key'
            ? hit.rootNode.userData.keySpec.midi_note
            : null;
        if (hoveredMidi !== this.pointerActiveKeyMidi) {
          if (this.pointerActiveKeyMidi !== null) {
            this.noteOff(this.pointerActiveKeyMidi, 'pointer');
          }
          this.pointerActiveKeyMidi = hoveredMidi;
          if (hoveredMidi !== null) {
            this.noteOn(hoveredMidi, 'pointer');
          }
        }
        return;
      }

      // Throttle non-drag hover raycasting to ~30Hz so high-rate mouse movement never blocks the UI thread
      const nowMs = performance.now();
      if (!this.pendingPatchSocketId && nowMs - (this._lastHoverRaycastMs || 0) < 32) {
        return;
      }
      this._lastHoverRaycastMs = nowMs;

      const hit = this._findInteractiveHit(e);
      if (this.pendingPatchSocketId && hit?.point) {
        this._updatePreviewCable(hit.point);
      }

      if (hit) {
        const { rootNode } = hit;
        const t = rootNode.userData.interactionType;
        if (this._lastCursor !== 'pointer') {
          this.canvas.style.cursor = 'pointer';
          this._lastCursor = 'pointer';
        }
        if (t === 'knob') {
          const s = rootNode.userData.knobSpec;
          this._updateReadout(
            `${s.label}: ${this._formatKnobValue(s, this.knobValues.get(s.id))} (Drag to turn)`
          );
        } else if (t === 'socket') {
          const s = rootNode.userData.socketSpec;
          this._updateReadout(
            `${s.label} [${s.port_type.toUpperCase()}] — Click to patch`
          );
        } else if (t === 'key') {
          const s = rootNode.userData.keySpec;
          this._updateReadout(
            `Key ${s.note_name} (${s.frequency_hz.toFixed(1)} Hz) · QWERTY [${s.qwerty_binding}]`
          );
        } else if (t === 'turntable') {
          this._updateReadout(
            `Turntable ${rootNode.userData.turntablePart.replace('Turntable_', '').replace('_', ' ')} — Click to operate`
          );
        }
      } else if (this._lastCursor !== 'grab') {
        this.canvas.style.cursor = 'grab';
        this._lastCursor = 'grab';
      }
    });

    const endDrag = (e) => {
      if (this.activeDrag) {
        if (
          this.activeDrag.type === 'key' &&
          this.pointerActiveKeyMidi !== null
        ) {
          this.noteOff(this.pointerActiveKeyMidi, 'pointer');
          this.pointerActiveKeyMidi = null;
        }
        this.activeDrag = null;
        this.controls.enabled = true;
        try {
          this.canvas.releasePointerCapture(e.pointerId);
        } catch (_) {}
      }
    };

    this.canvas.addEventListener('pointerup', endDrag);
    this.canvas.addEventListener('pointercancel', endDrag);

    this.canvas.addEventListener('dblclick', (e) => {
      const hit = this._findInteractiveHit(e);
      if (hit?.rootNode?.userData?.interactionType === 'knob') {
        const spec = hit.rootNode.userData.knobSpec;
        this.setKnobValue(spec.id, spec.default, { announce: true });
        this._setStatus(`Reset ${spec.label} to default (${this._formatKnobValue(spec, spec.default)})`, 'info');
      }
    });

    window.addEventListener('resize', () => {
      const w = this.canvas.clientWidth || window.innerWidth;
      const h = this.canvas.clientHeight || window.innerHeight;
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h, false);
    });
  }

  _renderPatchListUI() {
    const listEl = document.getElementById('patch-cables-list');
    if (!listEl) return;

    listEl.innerHTML = '';
    if (this.cableMeshes.size === 0) {
      const empty = document.createElement('div');
      empty.className = 'patch-empty';
      empty.textContent = 'No active cables — Click any socket on the rack to patch.';
      listEl.appendChild(empty);
      return;
    }

    for (const info of this.cableMeshes.values()) {
      const chip = document.createElement('button');
      chip.className = 'patch-chip';
      chip.title = 'Click to disconnect this patch cable';
      const dot = document.createElement('span');
      dot.className = 'patch-dot';
      dot.style.backgroundColor = `#${info.color.hex.toString(16).padStart(6, '0')}`;
      const text = document.createElement('span');
      text.textContent = `${info.sourceSpec.label} → ${info.targetSpec.label} ✕`;
      chip.appendChild(dot);
      chip.appendChild(text);
      chip.addEventListener('click', () => {
        this.disconnectCable(info.sourceSpec.id, info.targetSpec.id);
      });
      listEl.appendChild(chip);
    }
  }

  _setStatus(message, level = 'info') {
    const el = document.getElementById('status-banner');
    if (el && this._lastStatusText !== message) {
      el.textContent = message;
      el.dataset.level = level;
      this._lastStatusText = message;
    }
  }

  _updateReadout(text) {
    if (this._lastReadoutText === text) return;
    this._lastReadoutText = text;
    const el = document.getElementById('hover-readout');
    if (el) el.textContent = text;
  }

  // ============================================================================
  // ANIMATION LOOP (KEYS, PLATTER, TONEARM, CAMERA, OSCILLOSCOPE)
  // ============================================================================
  _animate() {
    requestAnimationFrame(() => this._animate());

    const now = performance.now();
    const dt = Math.min((now - this.lastFrameTimeMs) / 1000.0, 0.1);
    this.lastFrameTimeMs = now;

    this.frameStats.frameCount++;
    if (now - this.frameStats.lastSampleTime >= 500) {
      const elapsed = now - this.frameStats.lastSampleTime;
      this.frameStats.fps = Math.round(
        (this.frameStats.frameCount * 1000) / elapsed
      );
      this.frameStats.avgFrameTimeMs = +(
        elapsed / this.frameStats.frameCount
      ).toFixed(2);
      this.frameStats.frameCount = 0;
      this.frameStats.lastSampleTime = now;
    }

    if (this.cameraTransition) {
      const tr = this.cameraTransition;
      tr.elapsed += dt;
      const rawT = Math.min(1, tr.elapsed / tr.duration);
      const ease = 1 - Math.pow(1 - rawT, 3);
      this.camera.position.lerpVectors(tr.startPos, tr.endPos, ease);
      this.controls.target.lerpVectors(tr.startTarget, tr.endTarget, ease);
      this.camera.fov = THREE.MathUtils.lerp(tr.startFov, tr.endFov, ease);
      this.camera.updateProjectionMatrix();
      if (rawT >= 1) this.cameraTransition = null;
    }

    this.controls.update();

    // Spring-return hinged keyboard animation
    const travelRad = THREE.MathUtils.degToRad(
      this.contract.keyboard.travel_angle_deg || 4.5
    );
    const springRate = Math.min(
      1,
      dt / (this.contract.keyboard.spring_return_time_s || 0.025)
    );

    for (const keySpec of this.contract.keyboard.keys) {
      const targetAngle = this.pressedKeys.has(keySpec.midi_note)
        ? travelRad
        : 0;
      const curAngle = this.keyAngles.get(keySpec.midi_note) || 0;
      if (Math.abs(targetAngle - curAngle) > 0.0002) {
        const nextAngle = curAngle + (targetAngle - curAngle) * Math.min(1, springRate * 2.5);
        this.keyAngles.set(keySpec.midi_note, nextAngle);
        const node = this.nodesByName.get(keySpec.node_name);
        if (node) {
          node.rotation.x = nextAngle;
        }
      }
    }

    // Turntable platter & tonearm groove tracking
    const platterNode = this.nodesByName.get('Turntable_Platter');
    const gimbalNode = this.nodesByName.get('Tonearm_Gimbal');

    if (platterNode && this.audio.motorOn) {
      const omega = this.audio.getPlatterAngularVelocityRadS();
      this.platterAngleRad -= omega * dt;
      platterNode.rotation.y = this.platterAngleRad;
    }

    if (gimbalNode) {
      const ttSpec = this.contract.turntable.tonearm_gimbal_node;
      const dur = this.audio.recordBuffer ? this.audio.recordBuffer.duration : 16.0;
      const progress = Math.min(1.0, this.audio.getTurntablePlaybackPositionSec() / dur);
      const targetYawDeg = this.audio.tonearmLowered
        ? THREE.MathUtils.lerp(
            ttSpec.outer_groove_yaw_deg,
            ttSpec.inner_groove_yaw_deg,
            progress
          )
        : ttSpec.rest_yaw_deg;
      const targetPitchDeg = this.audio.tonearmLowered
        ? ttSpec.lowered_pitch_deg
        : ttSpec.raised_pitch_deg;

      this.currentTonearmYawDeg = THREE.MathUtils.lerp(
        this.currentTonearmYawDeg,
        targetYawDeg,
        Math.min(1, dt * 8)
      );
      this.currentTonearmPitchDeg = THREE.MathUtils.lerp(
        this.currentTonearmPitchDeg,
        targetPitchDeg,
        Math.min(1, dt * 10)
      );

      gimbalNode.rotation.y = THREE.MathUtils.degToRad(this.currentTonearmYawDeg);
      gimbalNode.rotation.x = THREE.MathUtils.degToRad(this.currentTonearmPitchDeg);
    }

    if (now - (this._lastScopeDrawMs || 0) >= 32) {
      this._lastScopeDrawMs = now;
      this._updateSocketRingHighlights();
      this._drawWaveformMonitor();
    }
    this.renderer.render(this.scene, this.camera);
  }

  _drawWaveformMonitor() {
    if (!this.scopeCtx || !this.scopeCanvas) return;
    const ctx = this.scopeCtx;
    const w = this.scopeCanvas.width;
    const h = this.scopeCanvas.height;

    ctx.fillStyle = '#0c100e';
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = 'rgba(82, 196, 138, 0.14)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.moveTo(w / 2, 0);
    ctx.lineTo(w / 2, h);
    ctx.stroke();

    const stats = this.audio.getFastWaveTelemetry();
    const samples = this.audio.timeDomainBuf;

    ctx.strokeStyle = stats.clipping ? '#ff5c4d' : '#55e6a5';
    ctx.lineWidth = 1.8;
    ctx.beginPath();

    if (!samples || samples.length === 0) {
      ctx.moveTo(0, h / 2);
      ctx.lineTo(w, h / 2);
    } else {
      const step = Math.max(1, Math.floor(samples.length / w));
      for (let x = 0; x < w; x++) {
        const idx = Math.min(samples.length - 1, x * step);
        const y = (0.5 - samples[idx] * 0.44) * h;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
    }
    ctx.stroke();

    const meterText = `PEAK ${stats.peak.toFixed(3)} · RMS ${stats.rms.toFixed(3)}${stats.clipping ? ' [CLIP LIMIT]' : ''}`;
    if (this._lastMeterText !== meterText) {
      this._lastMeterText = meterText;
      const meterEl = document.getElementById('meter-readout');
      if (meterEl) {
        meterEl.textContent = meterText;
        meterEl.classList.toggle('clip-warn', stats.clipping);
      }
    }
  }

  // ============================================================================
  // DIAGNOSTICS FOR AUTOMATED VERIFICATION
  // ============================================================================
  getDiagnostics() {
    const wave = this.audio.getTelemetry();
    return {
      audioActivated: this.audio.isActivated,
      contextState: this.audio.ctx ? this.audio.ctx.state : 'uninitialized',
      sampleRate: this.audio.ctx ? this.audio.ctx.sampleRate : null,
      activePreset: this.currentPresetId,
      activeCables: this.audio.cables.map(
        (c) => `${c.fromSocketId}->${c.toSocketId}`
      ),
      activeNotes: Array.from(this.pressedKeys),
      knobValues: Object.fromEntries(this.knobValues),
      vcfCutoffHz: this.audio.nodes?.vcfStage1?.frequency?.value ?? null,
      turntable: {
        state: this.audio.turntableState,
        motorOn: this.audio.motorOn,
        tonearmLowered: this.audio.tonearmLowered,
        rpm: +this.audio.rpm.toFixed(2),
        playbackRate: +this.audio.getPlaybackRate().toFixed(3),
        positionSec: +this.audio.getTurntablePlaybackPositionSec().toFixed(3),
        platterAngleRad: +this.platterAngleRad.toFixed(3),
        tonearmYawDeg: +this.currentTonearmYawDeg.toFixed(2),
        tonearmPitchDeg: +this.currentTonearmPitchDeg.toFixed(2)
      },
      levels: {
        peak: wave.peak,
        rms: wave.rms,
        clipping: wave.clipping,
        centroidHz: wave.centroidHz
      },
      inputMode: {
        mode: this.inputMode,
        status: this.midiStatusText
      },
      worldVerification: this.worldVerification,
      performance: {
        ...this.frameStats,
        viewport: [this.canvas.clientWidth, this.canvas.clientHeight],
        devicePixelRatio: window.devicePixelRatio || 1
      }
    };
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const app = new ModularStudioApp();
  app.init().catch((err) => {
    console.error('Studio init failed:', err);
    const el = document.getElementById('status-banner');
    if (el) el.textContent = `Studio initialization error: ${err.message}`;
  });
});
