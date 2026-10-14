import bpy
import bmesh
import json
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "contract.json"
WORLD_PATH = ROOT / "world.json"
BLEND_OUT = ROOT / "blender" / "studio_scene.blend"
GLB_OUT = ROOT / "public" / "assets" / "models" / "studio_scene.glb"
TEX_DIR = ROOT / "public" / "assets" / "textures"


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0


def three_to_blender_pos(pos_m):
    """
    Converts Three.js (X_right, Y_up, Z_front) to Blender (X_right, Y_back, Z_up):
      bl_x = three_x
      bl_y = -three_z
      bl_z = three_y
    """
    return (float(pos_m[0]), -float(pos_m[2]), float(pos_m[1]))


def make_pbr_material(
    name,
    base_rgb,
    roughness,
    metallic=0.0,
    albedo_path=None,
    normal_path=None,
    roughness_path=None,
    normal_strength=1.0,
    coat_weight=0.0,
    coat_roughness=0.1,
    emission_rgb=None,
    emission_strength=0.0
):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base_rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic

    if "Coat Weight" in bsdf.inputs and coat_weight > 0.0:
        bsdf.inputs["Coat Weight"].default_value = coat_weight
        bsdf.inputs["Coat Roughness"].default_value = coat_roughness

    if emission_rgb and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*emission_rgb, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength

    if albedo_path and Path(albedo_path).exists():
        tex_node = nt.nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(str(albedo_path))
        nt.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])

    if roughness_path and Path(roughness_path).exists():
        r_node = nt.nodes.new("ShaderNodeTexImage")
        r_node.image = bpy.data.images.load(str(roughness_path))
        r_node.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(r_node.outputs["Color"], bsdf.inputs["Roughness"])

    if normal_path and Path(normal_path).exists():
        n_tex = nt.nodes.new("ShaderNodeTexImage")
        n_tex.image = bpy.data.images.load(str(normal_path))
        n_tex.image.colorspace_settings.name = 'Non-Color'
        n_map = nt.nodes.new("ShaderNodeNormalMap")
        n_map.inputs["Strength"].default_value = normal_strength
        nt.links.new(n_tex.outputs["Color"], n_map.inputs["Color"])
        nt.links.new(n_map.outputs["Normal"], bsdf.inputs["Normal"])

    return mat


def add_box_to_bm(bm, cx, cy, cz, sx, sy, sz, mat_idx=0, uv_mode="world", bevel_width=0.0, bevel_segs=2):
    """
    Adds an axis-aligned box in Blender coords centered at (cx, cy, cz) with full sizes (sx, sy, sz).
    Supports micro-beveling and luthier-grade long-axis wood grain UV orientation.
    """
    hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
    coords = [
        (cx - hx, cy - hy, cz - hz),
        (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz),
        (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz),
        (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz),
        (cx - hx, cy + hy, cz + hz),
    ]
    v = [bm.verts.new(c) for c in coords]
    faces_spec = [
        (v[0], v[3], v[2], v[1]),  # bottom (-Z)
        (v[4], v[5], v[6], v[7]),  # top (+Z)
        (v[0], v[1], v[5], v[4]),  # front (-Y)
        (v[2], v[3], v[7], v[6]),  # back (+Y)
        (v[0], v[4], v[7], v[3]),  # left (-X)
        (v[1], v[2], v[6], v[5]),  # right (+X)
    ]
    created_faces = []
    for f_verts in faces_spec:
        f = bm.faces.new(f_verts)
        f.material_index = mat_idx
        created_faces.append(f)

    all_box_faces = list(created_faces)
    if bevel_width > 0.0:
        box_edges = list({e for f in created_faces if f.is_valid for e in f.edges})
        res = bmesh.ops.bevel(
            bm,
            geom=box_edges,
            offset=bevel_width,
            offset_type='OFFSET',
            segments=bevel_segs,
            profile=0.5,
            affect='EDGES'
        )
        for f in res.get("faces", []):
            if f.is_valid:
                f.material_index = mat_idx
                f.smooth = True
                all_box_faces.append(f)

    uv_layer = bm.loops.layers.uv.verify()
    scale = 1.35  # Realistic macro walnut grain scale
    for f in all_box_faces:
        if not f.is_valid:
            continue
        f.normal_update()
        n = f.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for loop in f.loops:
            co = loop.vert.co
            if uv_mode == "front_panel" and n.y < -0.5:
                u = (co.x - (cx - hx)) / max(sx, 1e-6)
                v_coord = (co.z - (cz - hz)) / max(sz, 1e-6)
                loop[uv_layer].uv = (u, v_coord)
            elif uv_mode == "top_deck" and n.z > 0.5:
                u = (co.x - (cx - hx)) / max(sx, 1e-6)
                v_coord = (co.y - (cy - hy)) / max(sy, 1e-6)
                loop[uv_layer].uv = (u, v_coord)
            elif uv_mode == "desk_tile":
                loop[uv_layer].uv = ((co.x + 1.1) * 1.8, (co.y + 0.65) * 1.8)
            else:
                # Orient V (the wood fibre direction in walnut_wood_grain.png) along the longest axis of each board face
                if ax >= ay and ax >= az:
                    # Side face (Y-Z plane)
                    if sy >= sz:
                        loop[uv_layer].uv = ((co.z + 0.35) * scale, (co.y + 0.5) * scale)
                    else:
                        loop[uv_layer].uv = ((co.y + 0.5) * scale, (co.z + 0.35) * scale)
                elif ay >= ax and ay >= az:
                    # Front/back face (X-Z plane)
                    if sx >= sz:
                        loop[uv_layer].uv = ((co.z + 0.35) * scale, (co.x + 0.5) * scale)
                    else:
                        loop[uv_layer].uv = ((co.x + 0.5) * scale, (co.z + 0.35) * scale)
                else:
                    # Top/bottom face (X-Y plane)
                    if sx >= sy:
                        loop[uv_layer].uv = ((co.y + 0.5) * scale, (co.x + 0.5) * scale)
                    else:
                        loop[uv_layer].uv = ((co.x + 0.5) * scale, (co.y + 0.5) * scale)

    return all_box_faces


def build_fluted_knob_mesh(name, mats):
    """
    Creates a high-precision 56-segment fluted phenolic bakelite knob mesh with smooth shading on the
    machined skirt, crisp flutes, bevelled top crown, recessed spun-aluminium center insert, and raised cream pointer inlay.
    """
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    flutes = 28
    segs = flutes * 2
    r_skirt = 0.0154
    r_body_outer = 0.0130
    r_body_inner = 0.0112
    r_top = 0.0106

    def ring_verts(s_height, r_even, r_odd):
        ring = []
        for i in range(segs):
            angle = (2.0 * math.pi * i) / segs
            r = r_even if (i % 2 == 0) else r_odd
            x = r * math.sin(angle)
            z = r * math.cos(angle)
            y = -s_height
            ring.append(bm.verts.new((x, y, z)))
        return ring

    r0 = ring_verts(0.0002, r_skirt, r_skirt)
    r1 = ring_verts(0.0034, r_skirt * 0.985, r_skirt * 0.985)
    r2 = ring_verts(0.0040, r_body_outer, r_body_inner)
    r3 = ring_verts(0.0182, r_body_outer * 0.91, r_body_inner * 0.91)
    r4 = ring_verts(0.0196, r_top, r_top)
    r5 = ring_verts(0.0200, 0.0052, 0.0052)
    r6 = ring_verts(0.0195, 0.0049, 0.0049)

    rings = [r0, r1, r2, r3, r4, r5, r6]
    for r_idx in range(len(rings) - 1):
        ra = rings[r_idx]
        rb = rings[r_idx + 1]
        for i in range(segs):
            j = (i + 1) % segs
            f = bm.faces.new((ra[i], rb[i], rb[j], ra[j]))
            f.material_index = 0  # Bakelite body
            f.smooth = True

    center_top = bm.verts.new((0.0, -0.0196, 0.0))
    uv_layer = bm.loops.layers.uv.verify()
    for i in range(segs):
        j = (i + 1) % segs
        f = bm.faces.new((r6[i], center_top, r6[j]))
        f.material_index = 1  # Spun aluminium center insert
        f.smooth = True
        for loop in f.loops:
            loop[uv_layer].uv = (0.5 + loop.vert.co.x * 80.0, 0.5 + loop.vert.co.z * 80.0)

    # Raised bevelled warm-cream pointer inlay bar (+Z in Blender = 12 o'clock +Y in Three.js)
    add_box_to_bm(
        bm,
        0.0, -0.0124, 0.0082,
        0.0028, 0.0172, 0.0118,
        mat_idx=2,
        bevel_width=0.0004,
        bevel_segs=2
    )

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    for m in mats:
        mesh.materials.append(m)
    return mesh


def build_patch_socket_mesh(name, mat_chrome, mat_bore, mat_ring):
    """
    High-precision 3.5mm modular patch jack: colour-coded anodised bushing washer, chamfered chrome hex nut,
    smooth 32-segment knurled ferrule lip, and deep recessed internal spring contact bore.
    """
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    segs_ring = 32
    r_wash_out = 0.0094
    w0 = [bm.verts.new((r_wash_out * math.sin(2*math.pi*i/segs_ring), 0.0, r_wash_out * math.cos(2*math.pi*i/segs_ring))) for i in range(segs_ring)]
    w1 = [bm.verts.new((r_wash_out * math.sin(2*math.pi*i/segs_ring), -0.0016, r_wash_out * math.cos(2*math.pi*i/segs_ring))) for i in range(segs_ring)]
    for i in range(segs_ring):
        j = (i + 1) % segs_ring
        f = bm.faces.new((w0[i], w1[i], w1[j], w0[j]))
        f.material_index = 2
        f.smooth = True

    # Hexagonal chrome jack nut with bevelled top chamfer
    r_hex = 0.0076
    r_hex_top = 0.0071
    h0 = [bm.verts.new((r_hex * math.sin(2*math.pi*i/6 + math.pi/6), -0.0014, r_hex * math.cos(2*math.pi*i/6 + math.pi/6))) for i in range(6)]
    h1 = [bm.verts.new((r_hex * math.sin(2*math.pi*i/6 + math.pi/6), -0.0050, r_hex * math.cos(2*math.pi*i/6 + math.pi/6))) for i in range(6)]
    h2 = [bm.verts.new((r_hex_top * math.sin(2*math.pi*i/6 + math.pi/6), -0.0056, r_hex_top * math.cos(2*math.pi*i/6 + math.pi/6))) for i in range(6)]
    for i in range(6):
        j = (i + 1) % 6
        f = bm.faces.new((h0[i], h1[i], h1[j], h0[j]))
        f.material_index = 0
        f_cham = bm.faces.new((h1[i], h2[i], h2[j], h1[j]))
        f_cham.material_index = 0
        f_cham.smooth = True

    # Smooth 32-segment chrome ferrule collar & dark 3.5mm bore
    segs_cyl = 32
    r_ferrule = 0.0053
    r_lip = 0.0048
    r_bore = 0.0031
    c0 = [bm.verts.new((r_ferrule * math.sin(2*math.pi*i/segs_cyl), -0.0054, r_ferrule * math.cos(2*math.pi*i/segs_cyl))) for i in range(segs_cyl)]
    c1 = [bm.verts.new((r_ferrule * math.sin(2*math.pi*i/segs_cyl), -0.0082, r_ferrule * math.cos(2*math.pi*i/segs_cyl))) for i in range(segs_cyl)]
    c2 = [bm.verts.new((r_lip * math.sin(2*math.pi*i/segs_cyl), -0.0086, r_lip * math.cos(2*math.pi*i/segs_cyl))) for i in range(segs_cyl)]
    b1 = [bm.verts.new((r_bore * math.sin(2*math.pi*i/segs_cyl), -0.0084, r_bore * math.cos(2*math.pi*i/segs_cyl))) for i in range(segs_cyl)]
    b_deep = [bm.verts.new((r_bore * 0.85 * math.sin(2*math.pi*i/segs_cyl), -0.0015, r_bore * 0.85 * math.cos(2*math.pi*i/segs_cyl))) for i in range(segs_cyl)]
    b_center = bm.verts.new((0.0, -0.0010, 0.0))

    hex_center = bm.verts.new((0.0, -0.0055, 0.0))
    for i in range(6):
        j = (i + 1) % 6
        f = bm.faces.new((h2[i], hex_center, h2[j]))
        f.material_index = 0

    for i in range(segs_cyl):
        j = (i + 1) % segs_cyl
        for ra, rb, mat_i in [(c0, c1, 0), (c1, c2, 0), (c2, b1, 0), (b1, b_deep, 1)]:
            f_s = bm.faces.new((ra[i], rb[i], rb[j], ra[j]))
            f_s.material_index = mat_i
            f_s.smooth = True
        f_bore = bm.faces.new((b_deep[i], b_center, b_deep[j]))
        f_bore.material_index = 1

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_chrome)
    mesh.materials.append(mat_bore)
    mesh.materials.append(mat_ring)
    return mesh


def build_key_mesh(name, is_sharp, mat_key):
    """
    Sculpted, bevelled Pratt-Read style 1970s synthesiser key mesh with local origin (0,0,0) at rear hinge pivot.
    """
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()
    if is_sharp:
        y_back = -0.002
        y_front_bot = -0.088
        y_front_top = -0.078
        z_bot = 0.002
        z_top = 0.0195
        w_bot = 0.0114
        w_top = 0.0082

        v0 = bm.verts.new((-w_bot, y_front_bot, z_bot))
        v1 = bm.verts.new(( w_bot, y_front_bot, z_bot))
        v2 = bm.verts.new(( w_bot, y_back,      z_bot))
        v3 = bm.verts.new((-w_bot, y_back,      z_bot))
        v4 = bm.verts.new((-w_top, y_front_top, z_top))
        v5 = bm.verts.new(( w_top, y_front_top, z_top))
        v6 = bm.verts.new(( w_top, y_back,      z_top))
        v7 = bm.verts.new((-w_top, y_back,      z_top))

        created = []
        for quad in [
            (v3, v2, v1, v0),
            (v4, v5, v6, v7),
            (v0, v1, v5, v4),
            (v1, v2, v6, v5),
            (v2, v3, v7, v6),
            (v3, v0, v4, v7),
        ]:
            f = bm.faces.new(quad)
            f.material_index = 0
            created.append(f)

        edges = list({e for f in created for e in f.edges})
        res = bmesh.ops.bevel(bm, geom=edges, offset=0.0012, offset_type='OFFSET', segments=2, profile=0.5, affect='EDGES')
        for f in res.get("faces", []):
            f.material_index = 0
            f.smooth = True
    else:
        length = 0.136
        width = 0.0444
        # Recessed lower apron body behind front overhang lip
        add_box_to_bm(bm, 0.0, -length * 0.5 + 0.002, -0.002, width * 0.95, length - 0.004, 0.013, mat_idx=0, bevel_width=0.0008, bevel_segs=2)
        # Bevelled upper playing surface with waterfall/overhang front lip
        add_box_to_bm(bm, 0.0, -length * 0.5, 0.0060, width, length, 0.0055, mat_idx=0, bevel_width=0.0012, bevel_segs=2)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_key)
    return mesh


def build_turntable_platter_mesh(mat_chrome, mat_vinyl, mat_label, mat_strobe_dark):
    """
    240-segment smooth-shaded 0.30 m direct-drive cast-aluminium platter with 2-track precision
    strobe dot bands, machined separator groove, rubber mat lip, jet-black 180g vinyl LP with radial
    groove normal map, domed center label, and polished chrome spindle.
    """
    mesh = bpy.data.meshes.new("Turntable_Platter_Mesh")
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.verify()

    segs = 240
    r_b0 = 0.1558
    r_b1 = 0.1548
    r_b2 = 0.1530
    r_b3 = 0.1518
    r_b4 = 0.1502
    r_b5 = 0.1494
    r_vinyl = 0.1465
    r_label = 0.0500
    r_spindle = 0.0036

    b0 = [bm.verts.new((r_b0 * math.cos(2*math.pi*i/segs), r_b0 * math.sin(2*math.pi*i/segs), -0.0110)) for i in range(segs)]
    b1 = [bm.verts.new((r_b1 * math.cos(2*math.pi*i/segs), r_b1 * math.sin(2*math.pi*i/segs), -0.0086)) for i in range(segs)]
    b2 = [bm.verts.new((r_b2 * math.cos(2*math.pi*i/segs), r_b2 * math.sin(2*math.pi*i/segs), -0.0044)) for i in range(segs)]
    b3 = [bm.verts.new((r_b3 * math.cos(2*math.pi*i/segs), r_b3 * math.sin(2*math.pi*i/segs), -0.0024)) for i in range(segs)]
    b4 = [bm.verts.new((r_b4 * math.cos(2*math.pi*i/segs), r_b4 * math.sin(2*math.pi*i/segs),  0.0008)) for i in range(segs)]
    b5 = [bm.verts.new((r_b5 * math.cos(2*math.pi*i/segs), r_b5 * math.sin(2*math.pi*i/segs),  0.0020)) for i in range(segs)]

    for i in range(segs):
        j = (i + 1) % segs
        # Lower machined chrome flange
        f0 = bm.faces.new((b0[i], b0[j], b1[j], b1[i]))
        f0.material_index = 0
        f0.smooth = True

        # Lower precision strobe track (120 cast-aluminium strobe dots for 33 1/3 RPM)
        f1 = bm.faces.new((b1[i], b1[j], b2[j], b2[i]))
        f1.material_index = 0 if (i % 2 == 0) else 3
        f1.smooth = True

        # Recessed dark anodised separator groove
        f2 = bm.faces.new((b2[i], b2[j], b3[j], b3[i]))
        f2.material_index = 3
        f2.smooth = True

        # Upper precision strobe track (80 cast-aluminium strobe dots for 45 RPM)
        f3 = bm.faces.new((b3[i], b3[j], b4[j], b4[i]))
        f3.material_index = 0 if (i % 3 == 0) else 3
        f3.smooth = True

        # Top machined chrome rim collar
        f4 = bm.faces.new((b4[i], b4[j], b5[j], b5[i]))
        f4.material_index = 0
        f4.smooth = True

    # Vinyl LP disc with raised outer lead-in bead & groove zone
    v_mat_lip = [bm.verts.new((r_vinyl * 1.008 * math.cos(2*math.pi*i/segs), r_vinyl * 1.008 * math.sin(2*math.pi*i/segs), 0.0028)) for i in range(segs)]
    v_outer = [bm.verts.new((r_vinyl * math.cos(2*math.pi*i/segs), r_vinyl * math.sin(2*math.pi*i/segs), 0.0046)) for i in range(segs)]
    v_label = [bm.verts.new((r_label * math.cos(2*math.pi*i/segs), r_label * math.sin(2*math.pi*i/segs), 0.0049)) for i in range(segs)]

    for i in range(segs):
        j = (i + 1) % segs
        f_rim = bm.faces.new((b5[i], b5[j], v_mat_lip[j], v_mat_lip[i]))
        f_rim.material_index = 3
        f_rim.smooth = True

        f_edge = bm.faces.new((v_mat_lip[i], v_mat_lip[j], v_outer[j], v_outer[i]))
        f_edge.material_index = 1
        f_edge.smooth = True

        f_vinyl = bm.faces.new((v_label[i], v_label[j], v_outer[j], v_outer[i]))
        f_vinyl.material_index = 1
        f_vinyl.smooth = True
        for loop in f_vinyl.loops:
            co = loop.vert.co
            u = 0.5 + (co.x / (2.0 * r_vinyl))
            v = 0.5 + (co.y / (2.0 * r_vinyl))
            loop[uv_layer].uv = (u, v)

    # Record center label & machined chrome center spindle
    v_spin_base = [bm.verts.new((r_spindle * math.cos(2*math.pi*i/segs), r_spindle * math.sin(2*math.pi*i/segs), 0.0052)) for i in range(segs)]
    v_spin_mid = [bm.verts.new((r_spindle * math.cos(2*math.pi*i/segs), r_spindle * math.sin(2*math.pi*i/segs), 0.020)) for i in range(segs)]
    v_spin_top = [bm.verts.new((r_spindle * 0.65 * math.cos(2*math.pi*i/segs), r_spindle * 0.65 * math.sin(2*math.pi*i/segs), 0.0235)) for i in range(segs)]
    spin_tip = bm.verts.new((0.0, 0.0, 0.0245))

    for i in range(segs):
        j = (i + 1) % segs
        f_lbl = bm.faces.new((v_spin_base[i], v_spin_base[j], v_label[j], v_label[i]))
        f_lbl.material_index = 2
        f_lbl.smooth = True
        for loop in f_lbl.loops:
            co = loop.vert.co
            u = 0.5 + (co.x / r_label) * 0.332
            v = 0.5 + (co.y / r_label) * 0.332
            loop[uv_layer].uv = (u, v)

        for ra, rb in [(v_spin_base, v_spin_mid), (v_spin_mid, v_spin_top)]:
            f_sp = bm.faces.new((ra[i], rb[i], rb[j], ra[j]))
            f_sp.material_index = 0
            f_sp.smooth = True
        f_spindle_cap = bm.faces.new((v_spin_top[i], spin_tip, v_spin_top[j]))
        f_spindle_cap.material_index = 0
        f_spindle_cap.smooth = True

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_chrome)
    mesh.materials.append(mat_vinyl)
    mesh.materials.append(mat_label)
    mesh.materials.append(mat_strobe_dark)
    return mesh


def add_cylinder_z(bm, cx, cy, z0, z1, r_bot, r_top, segs, mat_idx, smooth=True):
    ring0 = [bm.verts.new((cx + r_bot * math.cos(2*math.pi*i/segs), cy + r_bot * math.sin(2*math.pi*i/segs), z0)) for i in range(segs)]
    ring1 = [bm.verts.new((cx + r_top * math.cos(2*math.pi*i/segs), cy + r_top * math.sin(2*math.pi*i/segs), z1)) for i in range(segs)]
    c_top = bm.verts.new((cx, cy, z1))
    for i in range(segs):
        j = (i + 1) % segs
        f_side = bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))
        f_side.material_index = mat_idx
        f_side.smooth = smooth
        f_cap = bm.faces.new((ring1[i], ring1[j], c_top))
        f_cap.material_index = mat_idx
        f_cap.smooth = False


def build_tonearm_gimbal_mesh(mat_chrome, mat_black):
    """
    Precision S-shaped tubular chrome tonearm, cylindrical gimbal yoke with pivot rings,
    and knurled rear counterweight with tracking-force dial.
    """
    mesh = bpy.data.meshes.new("Tonearm_Gimbal_Mesh")
    bm = bmesh.new()

    # 1. Precision cylindrical gimbal column & C-yoke at (0,0,0)
    add_cylinder_z(bm, 0.0, 0.0, -0.012, 0.004, 0.017, 0.016, 36, mat_idx=1, smooth=True)
    add_cylinder_z(bm, 0.0, 0.0, 0.004, 0.017, 0.0115, 0.0115, 36, mat_idx=0, smooth=True)
    # Outer gimbal C-frame bridge & precision bearing screws
    add_box_to_bm(bm, -0.0135, 0.0, 0.0085, 0.0042, 0.015, 0.023, mat_idx=0, bevel_width=0.0007, bevel_segs=2)
    add_box_to_bm(bm,  0.0135, 0.0, 0.0085, 0.0042, 0.015, 0.023, mat_idx=0, bevel_width=0.0007, bevel_segs=2)
    add_box_to_bm(bm,  0.0,    0.0, 0.0195, 0.031,  0.015, 0.0042, mat_idx=0, bevel_width=0.0007, bevel_segs=2)
    add_cylinder_z(bm, 0.0, 0.0, 0.0215, 0.0245, 0.0045, 0.0040, 24, mat_idx=0, smooth=True)

    # 2. Rear counterweight cylinder along +Y in Blender (-Z in Three.js)
    segs = 36
    r_cw = 0.0145
    cw0 = [bm.verts.new((r_cw * math.cos(2*math.pi*i/segs), 0.026, 0.006 + r_cw * math.sin(2*math.pi*i/segs))) for i in range(segs)]
    cw_mid = [bm.verts.new((r_cw * 1.03 * math.cos(2*math.pi*i/segs), 0.034, 0.006 + r_cw * 1.03 * math.sin(2*math.pi*i/segs))) for i in range(segs)]
    cw1 = [bm.verts.new((r_cw * math.cos(2*math.pi*i/segs), 0.058, 0.006 + r_cw * math.sin(2*math.pi*i/segs))) for i in range(segs)]
    cw_c0 = bm.verts.new((0.0, 0.026, 0.006))
    cw_c1 = bm.verts.new((0.0, 0.058, 0.006))
    for i in range(segs):
        j = (i + 1) % segs
        f_ring = bm.faces.new((cw0[i], cw_mid[i], cw_mid[j], cw0[j]))
        f_ring.material_index = 1 if (i % 2 == 0) else 0
        f_ring.smooth = True
        f_body = bm.faces.new((cw_mid[i], cw1[i], cw1[j], cw_mid[j]))
        f_body.material_index = 0
        f_body.smooth = True
        bm.faces.new((cw0[j], cw_c0, cw0[i])).material_index = 1
        bm.faces.new((cw1[i], cw_c1, cw1[j])).material_index = 0

    # 3. 36-step smooth S-shaped tubular chrome tonearm + locking collar at headshell joint
    pts = []
    num_arm_steps = 36
    for s_i in range(num_arm_steps + 1):
        u = s_i / num_arm_steps
        by = 0.028 - u * (0.028 + 0.195)
        bx = 0.014 * math.sin(2.0 * math.pi * u) - 0.052 * (u ** 1.35)
        bz = 0.006 - 0.010 * u
        pts.append(Vector((bx, by, bz)))

    r_tube = 0.0033
    tube_segs = 24
    arm_rings = []
    for idx, p in enumerate(pts):
        r_cur = r_tube * 1.35 if idx >= num_arm_steps - 2 else r_tube
        ring = []
        for i in range(tube_segs):
            ang = 2.0 * math.pi * i / tube_segs
            ring.append(bm.verts.new((p.x + r_cur * math.cos(ang), p.y, p.z + r_cur * math.sin(ang))))
        arm_rings.append(ring)

    for r_i in range(len(arm_rings) - 1):
        ra = arm_rings[r_i]
        rb = arm_rings[r_i + 1]
        for i in range(tube_segs):
            j = (i + 1) % tube_segs
            f = bm.faces.new((ra[i], rb[i], rb[j], ra[j]))
            f.material_index = 0
            f.smooth = True

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_chrome)
    mesh.materials.append(mat_black)
    return mesh


def build_headshell_cartridge_mesh(mat_black, mat_chrome, mat_amber):
    """
    Sculpted die-cast magnesium headshell with machined silver side rails, top mounting screws,
    rear bayonet locking collar, curved chrome finger lift, moving-magnet cartridge body,
    amber stylus guard visor, and diamond stylus cantilever.
    """
    mesh = bpy.data.meshes.new("Tonearm_Headshell_Mesh")
    bm = bmesh.new()

    # Rear bayonet locking collar & neck
    add_box_to_bm(bm, 0.0, 0.004, 0.0035, 0.010, 0.010, 0.0085, mat_idx=1, bevel_width=0.0012, bevel_segs=2)
    # Bevelled black-anodised magnesium headshell top plate & tapered front nose
    add_box_to_bm(bm, 0.0, -0.011, 0.0042, 0.0175, 0.032, 0.0034, mat_idx=0, bevel_width=0.0008, bevel_segs=2)
    add_box_to_bm(bm, 0.0, -0.028, 0.0036, 0.0145, 0.008, 0.0028, mat_idx=0, bevel_width=0.0007, bevel_segs=2)
    # Machined silver side rails & dual cartridge mounting screw rails on top of headshell
    add_box_to_bm(bm, -0.0062, -0.012, 0.0061, 0.0022, 0.024, 0.0010, mat_idx=1, bevel_width=0.0002, bevel_segs=1)
    add_box_to_bm(bm,  0.0062, -0.012, 0.0061, 0.0022, 0.024, 0.0010, mat_idx=1, bevel_width=0.0002, bevel_segs=1)
    add_cylinder_z(bm, -0.0038, -0.016, 0.0058, 0.0072, 0.0016, 0.0015, 16, mat_idx=1, smooth=True)
    add_cylinder_z(bm,  0.0038, -0.016, 0.0058, 0.0072, 0.0016, 0.0015, 16, mat_idx=1, smooth=True)
    # Curved chrome finger lift bar on right side
    add_box_to_bm(bm, 0.014, -0.018, 0.0055, 0.013, 0.0028, 0.0028, mat_idx=1, bevel_width=0.0006, bevel_segs=2)
    add_box_to_bm(bm, 0.020, -0.018, 0.0082, 0.0028, 0.0028, 0.0055, mat_idx=1, bevel_width=0.0006, bevel_segs=2)
    # Moving-magnet cartridge body + amber stylus guard carrier
    add_box_to_bm(bm, 0.0, -0.015, -0.0032, 0.0132, 0.024, 0.010, mat_idx=0, bevel_width=0.0008, bevel_segs=2)
    add_box_to_bm(bm, 0.0, -0.023, -0.0062, 0.0122, 0.010, 0.0048, mat_idx=2, bevel_width=0.0006, bevel_segs=2)
    # Cantilever & diamond stylus tip contacting record groove at 0 deg pitch
    add_box_to_bm(bm, 0.0, -0.024, -0.0112, 0.0016, 0.006, 0.0065, mat_idx=1, bevel_width=0.0003, bevel_segs=1)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_black)
    mesh.materials.append(mat_chrome)
    mesh.materials.append(mat_amber)
    return mesh


def main():
    clear_scene()
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    world = json.loads(WORLD_PATH.read_text(encoding="utf-8"))

    # Create high-realism PBR materials with full albedo, roughness, normal, and clearcoat maps
    mat_walnut = make_pbr_material(
        "mat_walnut_cabinet", (0.36, 0.20, 0.11), 0.34, 0.0,
        albedo_path=TEX_DIR / "walnut_wood_grain.png",
        normal_path=TEX_DIR / "walnut_wood_normal.png",
        roughness_path=TEX_DIR / "walnut_wood_roughness.png",
        normal_strength=1.25,
        coat_weight=0.48,
        coat_roughness=0.18
    )
    mat_panel = make_pbr_material(
        "mat_anodised_panel", (0.07, 0.08, 0.10), 0.42, 0.52,
        albedo_path=TEX_DIR / "synth_faceplate_albedo.png",
        roughness_path=TEX_DIR / "synth_faceplate_roughness.png",
        normal_path=TEX_DIR / "synth_faceplate_normal.png",
        normal_strength=0.22
    )
    mat_tt_deck = make_pbr_material(
        "mat_turntable_deck", (0.13, 0.14, 0.16), 0.32, 0.78,
        albedo_path=TEX_DIR / "turntable_deck_albedo.png",
        roughness_path=TEX_DIR / "turntable_deck_roughness.png",
        normal_path=TEX_DIR / "turntable_deck_normal.png",
        normal_strength=0.22,
        coat_weight=0.18,
        coat_roughness=0.24
    )
    mat_trim = make_pbr_material(
        "mat_anodised_trim", (0.08, 0.09, 0.11), 0.36, 0.62
    )
    mat_bakelite = make_pbr_material(
        "mat_bakelite_knob", (0.025, 0.025, 0.03), 0.18, 0.06,
        coat_weight=0.72, coat_roughness=0.12
    )
    mat_alum_cap = make_pbr_material(
        "mat_spun_alum_cap", (0.80, 0.82, 0.86), 0.18, 0.92
    )
    mat_cream_inlay = make_pbr_material("mat_cream_inlay", (0.98, 0.94, 0.84), 0.22, 0.0)
    mat_chrome = make_pbr_material("mat_chrome_fitting", (0.92, 0.94, 0.97), 0.09, 0.97)
    mat_bore = make_pbr_material("mat_socket_bore", (0.01, 0.01, 0.015), 0.92, 0.0)
    mat_ring_amber = make_pbr_material(
        "mat_ring_amber", (0.98, 0.46, 0.10), 0.22, 0.15,
        emission_rgb=(1.0, 0.42, 0.06), emission_strength=1.40
    )
    mat_ring_cyan = make_pbr_material("mat_ring_cyan", (0.32, 0.74, 0.88), 0.28, 0.15)
    mat_ring_cream = make_pbr_material("mat_ring_cream", (0.92, 0.88, 0.78), 0.28, 0.12)
    mat_ivory = make_pbr_material(
        "mat_ivory_key", (0.95, 0.91, 0.82), 0.16, 0.0,
        coat_weight=0.75, coat_roughness=0.10
    )
    mat_ebony = make_pbr_material(
        "mat_ebony_key", (0.035, 0.035, 0.045), 0.22, 0.02,
        coat_weight=0.50, coat_roughness=0.16
    )
    mat_felt_red = make_pbr_material(
        "mat_keybed_felt", (0.58, 0.07, 0.09), 0.92, 0.0,
        normal_path=TEX_DIR / "studio_desk_normal.png",
        normal_strength=0.8
    )
    mat_vinyl = make_pbr_material(
        "mat_vinyl_record", (0.012, 0.012, 0.016), 0.14, 0.08,
        normal_path=TEX_DIR / "vinyl_grooves_normal.png",
        normal_strength=1.35,
        coat_weight=0.92,
        coat_roughness=0.07
    )
    mat_label = make_pbr_material(
        "mat_vinyl_label", (0.94, 0.89, 0.76), 0.38, 0.0,
        albedo_path=TEX_DIR / "vinyl_label_albedo.png"
    )
    mat_sleeve = make_pbr_material(
        "mat_record_sleeve", (0.92, 0.88, 0.83), 0.48, 0.0,
        albedo_path=TEX_DIR / "vinyl_sleeve_art.png",
        normal_path=TEX_DIR / "walnut_wood_normal.png",
        normal_strength=0.22,
        coat_weight=0.22,
        coat_roughness=0.32
    )
    mat_desk = make_pbr_material(
        "mat_studio_slate_desk", (0.09, 0.075, 0.07), 0.68, 0.02,
        albedo_path=TEX_DIR / "studio_desk_albedo.png",
        roughness_path=TEX_DIR / "studio_desk_roughness.png",
        normal_path=TEX_DIR / "studio_desk_normal.png",
        normal_strength=1.15
    )

    # 1. Studio_Desk_Surface (Deep espresso leatherette studio console tabletop + bullnose walnut trim + continuous L-wrap slatted acoustic wall)
    desk_mesh = bpy.data.meshes.new("Studio_Desk_Surface_Mesh")
    bm = bmesh.new()
    add_box_to_bm(bm, 0.20, 0.0, -0.02, 3.80, 1.60, 0.04, mat_idx=0, uv_mode="desk_tile", bevel_width=0.003, bevel_segs=2)
    # Front oiled walnut console bolster rail with rounded bullnose bevel
    add_box_to_bm(bm, 0.20, -0.785, -0.015, 3.80, 0.048, 0.054, mat_idx=1, bevel_width=0.007, bevel_segs=3)
    # Continuous studio backwall acoustic absorber panel & bevelled walnut diffuser slats (extends full width behind synth & turntable)
    add_box_to_bm(bm, 0.15, 0.36, 0.36, 3.80, 0.04, 1.04, mat_idx=0, uv_mode="desk_tile")
    # Walnut wainscot horizontal ledger rail along the desk-wall junction so zero gap is visible from any angle
    add_box_to_bm(bm, 0.15, 0.335, 0.022, 3.80, 0.028, 0.048, mat_idx=1, bevel_width=0.003, bevel_segs=2)
    for slat_i in range(-32, 33):
        sx = slat_i * 0.056
        add_box_to_bm(bm, sx, 0.338, 0.42, 0.024, 0.020, 0.94, mat_idx=1, bevel_width=0.002, bevel_segs=2)
    # Right-side studio acoustic return wall & vertical walnut slats (eliminates void in side_profile_tilt view)
    add_box_to_bm(bm, 1.48, -0.15, 0.38, 0.03, 1.10, 1.00, mat_idx=0, uv_mode="desk_tile")
    for r_i in range(-8, 9):
        ry = -0.12 + r_i * 0.056
        add_box_to_bm(bm, 1.458, ry, 0.40, 0.018, 0.024, 0.92, mat_idx=1, bevel_width=0.002, bevel_segs=2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(desk_mesh)
    bm.free()
    desk_mesh.materials.append(mat_desk)
    desk_mesh.materials.append(mat_walnut)
    desk_obj = bpy.data.objects.new("Studio_Desk_Surface", desk_mesh)
    desk_obj.location = three_to_blender_pos([0.0, -0.02, 0.0])
    bpy.context.collection.objects.link(desk_obj)

    # 2. Synth_Cabinet_Root (Bevelled oiled American walnut cheeks, top overhang hood, brushed trim rails & wrist bolster)
    cab_mesh = bpy.data.meshes.new("Synth_Cabinet_Root_Mesh")
    bm = bmesh.new()
    for sign in (-1.0, 1.0):
        cx = sign * 0.417
        # Upper angled walnut cheek
        add_box_to_bm(bm, cx, 0.045, 0.23, 0.034, 0.225, 0.425, mat_idx=0, bevel_width=0.0035, bevel_segs=3)
        # Lower keybed walnut cheek extension
        add_box_to_bm(bm, cx, -0.142, 0.056, 0.034, 0.225, 0.114, mat_idx=0, bevel_width=0.0035, bevel_segs=3)
    # Top walnut canopy hood with bevelled front lip
    add_box_to_bm(bm, 0.0, 0.095, 0.433, 0.868, 0.145, 0.030, mat_idx=0, bevel_width=0.0035, bevel_segs=3)
    # Rear dark anodised enclosure backplane
    add_box_to_bm(bm, 0.0, 0.145, 0.22, 0.80, 0.024, 0.40, mat_idx=1, bevel_width=0.002, bevel_segs=2)
    # Front oiled walnut wrist rest bar in front of keys
    add_box_to_bm(bm, 0.0, -0.245, 0.024, 0.868, 0.038, 0.048, mat_idx=0, bevel_width=0.004, bevel_segs=3)
    # Heavy chassis base plinth
    add_box_to_bm(bm, 0.0, -0.04, 0.016, 0.80, 0.38, 0.032, mat_idx=1, bevel_width=0.002, bevel_segs=2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(cab_mesh)
    bm.free()
    cab_mesh.materials.append(mat_walnut)
    cab_mesh.materials.append(mat_trim)
    cab_mesh.materials.append(mat_chrome)
    cab_obj = bpy.data.objects.new("Synth_Cabinet_Root", cab_mesh)
    cab_obj.location = three_to_blender_pos([-0.22, 0.0, 0.0])
    bpy.context.collection.objects.link(cab_obj)

    # 3. Synth_Faceplate_Frame (0.80 m wide x 0.34 m tall, tilted -15 deg around X)
    fp_mesh = bpy.data.meshes.new("Synth_Faceplate_Frame_Mesh")
    bm = bmesh.new()
    add_box_to_bm(bm, 0.0, 0.006, 0.0, 0.80, 0.012, 0.34, mat_idx=0, uv_mode="front_panel")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(fp_mesh)
    bm.free()
    fp_mesh.materials.append(mat_panel)
    fp_obj = bpy.data.objects.new("Synth_Faceplate_Frame", fp_mesh)
    fp_obj.parent = cab_obj
    fp_obj.location = three_to_blender_pos([0.0, 0.255, -0.045])
    fp_obj.rotation_euler = Euler((math.radians(-15.0), 0.0, 0.0), 'XYZ')
    bpy.context.collection.objects.link(fp_obj)

    # 4. 16 Knobs parented to Synth_Faceplate_Frame
    shared_knob_mesh = build_fluted_knob_mesh("Shared_Fluted_Knob", [mat_bakelite, mat_alum_cap, mat_cream_inlay])
    for k in contract["knobs"]:
        k_obj = bpy.data.objects.new(k["node_name"], shared_knob_mesh.copy())
        k_obj.parent = fp_obj
        k_obj.location = three_to_blender_pos(k["panel_local_pos_m"])
        bpy.context.collection.objects.link(k_obj)

    # 5. 12 Patch Sockets parented to Synth_Faceplate_Frame
    sock_mesh_amber = build_patch_socket_mesh("Sock_Amber", mat_chrome, mat_bore, mat_ring_amber)
    sock_mesh_cyan = build_patch_socket_mesh("Sock_Cyan", mat_chrome, mat_bore, mat_ring_cyan)
    sock_mesh_cream = build_patch_socket_mesh("Sock_Cream", mat_chrome, mat_bore, mat_ring_cream)

    for s in contract["patch_sockets"]:
        is_cv = ("cv" in s["port_type"])
        is_out = (s["direction"] == "output")
        s_mesh = sock_mesh_cyan if is_cv else (sock_mesh_amber if is_out else sock_mesh_cream)
        s_obj = bpy.data.objects.new(s["node_name"], s_mesh.copy())
        s_obj.parent = fp_obj
        s_obj.location = three_to_blender_pos(s["panel_local_pos_m"])
        bpy.context.collection.objects.link(s_obj)

    # 6. Synth_Keybed_Frame & 25 Sculpted Hinged Keys
    kb_mesh = bpy.data.meshes.new("Synth_Keybed_Frame_Mesh")
    bm = bmesh.new()
    add_box_to_bm(bm, 0.0, 0.0, -0.014, 0.79, 0.165, 0.012, mat_idx=0, bevel_width=0.0015, bevel_segs=2)
    add_box_to_bm(bm, -0.382, -0.005, 0.001, 0.028, 0.152, 0.022, mat_idx=0, bevel_width=0.002, bevel_segs=2)
    add_box_to_bm(bm,  0.382, -0.005, 0.001, 0.028, 0.152, 0.022, mat_idx=0, bevel_width=0.002, bevel_segs=2)
    add_box_to_bm(bm, 0.0, 0.072, 0.012, 0.79, 0.018, 0.016, mat_idx=0, bevel_width=0.002, bevel_segs=2)
    add_box_to_bm(bm, 0.0, 0.062, 0.0095, 0.745, 0.009, 0.006, mat_idx=1, bevel_width=0.001, bevel_segs=2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(kb_mesh)
    bm.free()
    kb_mesh.materials.append(mat_trim)
    kb_mesh.materials.append(mat_felt_red)
    kb_obj = bpy.data.objects.new("Synth_Keybed_Frame", kb_mesh)
    kb_obj.parent = cab_obj
    kb_obj.location = three_to_blender_pos([0.0, 0.048, 0.165])
    bpy.context.collection.objects.link(kb_obj)

    white_key_mesh = build_key_mesh("White_Key", False, mat_ivory)
    sharp_key_mesh = build_key_mesh("Sharp_Key", True, mat_ebony)
    for key in contract["keyboard"]["keys"]:
        km = sharp_key_mesh.copy() if key["is_sharp"] else white_key_mesh.copy()
        k_obj = bpy.data.objects.new(key["node_name"], km)
        k_obj.parent = kb_obj
        k_obj.location = three_to_blender_pos(key["keybed_local_pos_m"])
        bpy.context.collection.objects.link(k_obj)

    # 7. Turntable_Root (Bevelled walnut plinth + 4 isolation feet + UV-mapped brushed gunmetal top deck + sculpted strobe tower & cue hardware)
    tt_mesh = bpy.data.meshes.new("Turntable_Root_Mesh")
    bm = bmesh.new()
    # 4 machined chrome & rubber shock-absorber isolation feet at the plinth corners
    for fx in (-0.175, 0.175):
        for fy in (-0.140, 0.140):
            add_cylinder_z(bm, fx, fy, 0.0, 0.008, 0.024, 0.022, 28, mat_idx=3, smooth=True)
            add_cylinder_z(bm, fx, fy, 0.008, 0.012, 0.020, 0.020, 28, mat_idx=4, smooth=True)
    # Bevelled American walnut plinth box (0.42 m x 0.35 m)
    add_box_to_bm(bm, 0.0, 0.0, 0.036, 0.42, 0.35, 0.052, mat_idx=0, bevel_width=0.004, bevel_segs=3)
    # Brushed gunmetal aluminium top deck plate (0.39 m x 0.32 m) with exact top_deck UV mapping!
    add_box_to_bm(bm, 0.0, 0.0, 0.0635, 0.39, 0.32, 0.005, mat_idx=1, uv_mode="top_deck")
    # Sculpted die-cast strobe illuminator prism housing (cylindrical pedestal + angled prism hood + neon-amber lens window)
    add_cylinder_z(bm, -0.156, -0.095, 0.065, 0.070, 0.0115, 0.0110, 28, mat_idx=3, smooth=True)
    add_box_to_bm(bm, -0.155, -0.095, 0.0745, 0.016, 0.021, 0.010, mat_idx=4, bevel_width=0.0015, bevel_segs=2)
    add_box_to_bm(bm, -0.153, -0.095, 0.0802, 0.018, 0.022, 0.0022, mat_idx=3, bevel_width=0.0005, bevel_segs=2)
    add_box_to_bm(bm, -0.146, -0.092, 0.0742, 0.0032, 0.014, 0.0068, mat_idx=2, bevel_width=0.0004, bevel_segs=1)
    # Machined 45-RPM aluminium single adapter puck recessed in back-left deck corner
    add_cylinder_z(bm, -0.148, 0.115, 0.0655, 0.0705, 0.0185, 0.0180, 36, mat_idx=3, smooth=True)
    add_cylinder_z(bm, -0.148, 0.115, 0.0705, 0.0725, 0.0042, 0.0040, 24, mat_idx=4, smooth=True)
    # Tonearm rest post, cradle clip, hydraulic cueing cylinder, cue lever bar & anti-skate bias dial near gimbal base
    add_cylinder_z(bm, 0.095, -0.048, 0.065, 0.082, 0.0042, 0.0032, 20, mat_idx=3, smooth=True)
    add_box_to_bm(bm, 0.095, -0.048, 0.0835, 0.009, 0.005, 0.004, mat_idx=4, bevel_width=0.0006, bevel_segs=1)
    add_cylinder_z(bm, 0.112, -0.018, 0.065, 0.078, 0.0055, 0.0052, 24, mat_idx=4, smooth=True)
    add_box_to_bm(bm, 0.104, -0.018, 0.079, 0.018, 0.0028, 0.0024, mat_idx=3, bevel_width=0.0004, bevel_segs=1)
    add_cylinder_z(bm, 0.165,  0.075, 0.065, 0.074, 0.009,  0.0085, 28, mat_idx=3, smooth=True)
    add_cylinder_z(bm, 0.165,  0.075, 0.074, 0.077, 0.006,  0.0055, 28, mat_idx=4, smooth=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(tt_mesh)
    bm.free()
    tt_mesh.materials.append(mat_walnut)       # 0
    tt_mesh.materials.append(mat_tt_deck)      # 1
    tt_mesh.materials.append(mat_ring_amber)   # 2
    tt_mesh.materials.append(mat_chrome)       # 3
    tt_mesh.materials.append(mat_bakelite)     # 4
    tt_obj = bpy.data.objects.new("Turntable_Root", tt_mesh)
    tt_obj.location = three_to_blender_pos([0.44, 0.0, 0.05])
    bpy.context.collection.objects.link(tt_obj)

    # 8. Turntable_Platter
    platter_mesh = build_turntable_platter_mesh(mat_chrome, mat_vinyl, mat_label, mat_bakelite)
    platter_obj = bpy.data.objects.new("Turntable_Platter", platter_mesh)
    platter_obj.parent = tt_obj
    platter_obj.location = three_to_blender_pos(contract["turntable"]["platter_node"]["local_pos_m"])
    bpy.context.collection.objects.link(platter_obj)

    # 9. Tonearm_Gimbal & Tonearm_Headshell
    gimbal_mesh = build_tonearm_gimbal_mesh(mat_chrome, mat_bakelite)
    gimbal_obj = bpy.data.objects.new("Tonearm_Gimbal", gimbal_mesh)
    gimbal_obj.parent = tt_obj
    gimbal_obj.location = three_to_blender_pos(contract["turntable"]["tonearm_gimbal_node"]["local_pos_m"])
    gimbal_obj.rotation_euler = Euler((math.radians(5.5), 0.0, 0.0), 'XYZ')
    bpy.context.collection.objects.link(gimbal_obj)

    headshell_mesh = build_headshell_cartridge_mesh(mat_bakelite, mat_chrome, mat_ring_amber)
    headshell_obj = bpy.data.objects.new("Tonearm_Headshell", headshell_mesh)
    headshell_obj.parent = gimbal_obj
    headshell_obj.location = three_to_blender_pos([-0.052, -0.008, 0.195])
    headshell_obj.rotation_euler = Euler((0.0, 0.0, math.radians(22.0)), 'XYZ')
    bpy.context.collection.objects.link(headshell_obj)

    # 10. Turntable_SpeedSwitch (Machined 32-segment rotary selector with bevelled pointer blade)
    sw_mesh = bpy.data.meshes.new("Turntable_SpeedSwitch_Mesh")
    bm = bmesh.new()
    add_cylinder_z(bm, 0.0, 0.0, 0.0, 0.003, 0.0125, 0.0118, 32, mat_idx=1, smooth=True)
    add_cylinder_z(bm, 0.0, 0.0, 0.003, 0.011, 0.0095, 0.0088, 32, mat_idx=0, smooth=True)
    add_box_to_bm(bm, 0.0, 0.003, 0.0125, 0.0036, 0.0165, 0.0042, mat_idx=1, bevel_width=0.0006, bevel_segs=2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(sw_mesh)
    bm.free()
    sw_mesh.materials.append(mat_bakelite)
    sw_mesh.materials.append(mat_chrome)
    sw_obj = bpy.data.objects.new("Turntable_SpeedSwitch", sw_mesh)
    sw_obj.parent = tt_obj
    sw_obj.location = three_to_blender_pos(contract["turntable"]["speed_switch_node"]["local_pos_m"])
    bpy.context.collection.objects.link(sw_obj)

    # 11. Turntable_StartStop (Machined 36-segment chrome collar + tactile spun-aluminium actuator button)
    st_mesh = bpy.data.meshes.new("Turntable_StartStop_Mesh")
    bm = bmesh.new()
    add_cylinder_z(bm, 0.0, 0.0, 0.0, 0.0045, 0.0145, 0.0132, 36, mat_idx=0, smooth=True)
    add_cylinder_z(bm, 0.0, 0.0, 0.0045, 0.0095, 0.0105, 0.0100, 36, mat_idx=1, smooth=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(st_mesh)
    bm.free()
    st_mesh.materials.append(mat_chrome)
    st_mesh.materials.append(mat_alum_cap)
    st_obj = bpy.data.objects.new("Turntable_StartStop", st_mesh)
    st_obj.parent = tt_obj
    st_obj.location = three_to_blender_pos(contract["turntable"]["start_stop_node"]["local_pos_m"])
    bpy.context.collection.objects.link(st_obj)

    # 12. Vinyl_Sleeve_Stand (Thick bevelled gatefold LP jacket + inner paper dust sleeve + peeking 12-inch vinyl disc edge)
    sl_mesh = bpy.data.meshes.new("Vinyl_Sleeve_Stand_Mesh")
    bm = bmesh.new()
    # Front and rear gatefold cardboard leaves with visible bevelled spine and opening slot
    add_box_to_bm(bm, 0.0, -0.0038, 0.0, 0.314, 0.0055, 0.314, mat_idx=0, uv_mode="front_panel")
    add_box_to_bm(bm, 0.0,  0.0038, 0.0, 0.314, 0.0055, 0.314, mat_idx=0, uv_mode="front_panel")
    # Gatefold left spine binding
    add_box_to_bm(bm, -0.155, 0.0, 0.0, 0.007, 0.0135, 0.314, mat_idx=1, bevel_width=0.0012, bevel_segs=2)
    # Inner cream paper dust sleeve peeking 5mm out of the right opening
    add_box_to_bm(bm, 0.006, 0.0, 0.0, 0.308, 0.0035, 0.304, mat_idx=1, bevel_width=0.0006, bevel_segs=1)
    # Peeking 180g black vinyl LP edge protruding slightly from the dust sleeve
    add_box_to_bm(bm, 0.012, 0.0, 0.0, 0.304, 0.0022, 0.296, mat_idx=2, bevel_width=0.0005, bevel_segs=1)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(sl_mesh)
    bm.free()
    sl_mesh.materials.append(mat_sleeve)
    sl_mesh.materials.append(mat_cream_inlay)
    sl_mesh.materials.append(mat_vinyl)
    sl_obj = bpy.data.objects.new("Vinyl_Sleeve_Stand", sl_mesh)
    sl_obj.parent = tt_obj
    sl_obj.location = three_to_blender_pos([0.02, 0.185, -0.195])
    sl_obj.rotation_euler = Euler((math.radians(-12.0), 0.0, math.radians(-8.0)), 'XYZ')
    bpy.context.collection.objects.link(sl_obj)

    BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
    GLB_OUT.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_OUT),
        export_format='GLB',
        export_yup=True,
        export_apply=False
    )
    print(f"STUDIO SCENE EXPORTED: {BLEND_OUT} -> {GLB_OUT} ({GLB_OUT.stat().st_size} bytes, {len(bpy.data.objects)} objects)")


if __name__ == "__main__":
    main()
