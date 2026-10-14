import bpy
import bmesh
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLEND_OUT = ROOT / "blender" / "calibration_knob.blend"
GLB_OUT = ROOT / "public" / "assets" / "models" / "calibration_knob.glb"

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

def make_material(name, base_color, roughness, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

def create_fluted_bakelite_knob(name="Knob_05_VCF_Cutoff"):
    mat_bakelite = make_material("Mat_Bakelite_Knob", (0.06, 0.06, 0.07), roughness=0.26, metallic=0.05)
    mat_cap = make_material("Mat_Spun_Alum_Cap", (0.78, 0.80, 0.83), roughness=0.22, metallic=0.88)
    mat_inlay = make_material("Mat_Cream_Indicator", (0.96, 0.92, 0.82), roughness=0.35, metallic=0.0)

    # Create knob mesh in XY plane with +Z as shaft axis (or rotated for faceplate)
    # In our contract, faceplate children have local +Z pointing out from panel normal,
    # and +Y pointing toward 12 o'clock along the faceplate.
    # Remember Blender->glTF Y-up conversion:
    # To make glTF local axes have +Z out from panel and +Y up toward 12 o'clock,
    # we build the knob in a parent frame or directly in Blender's local coordinates.
    # Wait: in Blender, for an object with identity rotation, glTF export with export_yup=True
    # maps Blender (+X, +Y, +Z) -> glTF (+X, +Z_up->+Y, -Y_depth->+Z).
    # Specifically, in glTF after export_yup=True:
    #   glTF +X = Blender +X
    #   glTF +Y = Blender +Z
    #   glTF +Z = Blender -Y
    # Therefore, if a knob is mounted on a faceplate whose normal is glTF +Z (Blender -Y),
    # then in Blender the shaft points along -Y, and 12 o'clock points along +Z!
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    flutes = 20
    segs = flutes * 2
    r_skirt = 0.0145
    r_body_outer = 0.0125
    r_body_inner = 0.0108
    r_top = 0.0102

    # Build rings along shaft axis s from 0.0 (panel base) to 0.019 (top)
    # Where s maps to Blender -Y (so glTF +Z = +s!)
    # And angle theta=0 maps to 12 o'clock: glTF +Y = Blender +Z!
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

    r0 = ring_verts(0.000, r_skirt, r_skirt)
    r1 = ring_verts(0.003, r_skirt, r_skirt)
    r2 = ring_verts(0.0035, r_body_outer, r_body_inner)
    r3 = ring_verts(0.0175, r_body_outer * 0.93, r_body_inner * 0.93)
    r4 = ring_verts(0.0185, r_top, r_top)

    rings = [r0, r1, r2, r3, r4]
    for r_idx in range(len(rings) - 1):
        ra = rings[r_idx]
        rb = rings[r_idx + 1]
        for i in range(segs):
            j = (i + 1) % segs
            f = bm.faces.new((ra[i], rb[i], rb[j], ra[j]))
            f.material_index = 0

    # Top spun-aluminium cap face
    center_top = bm.verts.new((0.0, -0.0190, 0.0))
    for i in range(segs):
        j = (i + 1) % segs
        f = bm.faces.new((r4[i], center_top, r4[j]))
        f.material_index = 1

    # Raised cream indicator inlay bar pointing to 12 o'clock (Blender +Z, glTF +Y)
    # Covers from radius 0.002 to 0.0138, width 0.0022
    w_half = 0.0011
    z_in = 0.0025
    z_out = 0.0138
    y_top = -0.0196
    y_bot = -0.0178
    v_b0 = bm.verts.new((-w_half, y_bot, z_in))
    v_b1 = bm.verts.new(( w_half, y_bot, z_in))
    v_b2 = bm.verts.new(( w_half, y_bot, z_out))
    v_b3 = bm.verts.new((-w_half, y_bot, z_out))
    v_t0 = bm.verts.new((-w_half, y_top, z_in))
    v_t1 = bm.verts.new(( w_half, y_top, z_in))
    v_t2 = bm.verts.new(( w_half, y_top, z_out))
    v_t3 = bm.verts.new((-w_half, y_top, z_out))

    inlay_faces = [
        (v_t0, v_t1, v_t2, v_t3),
        (v_b0, v_t0, v_t3, v_b3),
        (v_b1, v_b2, v_t2, v_t1),
        (v_b3, v_t3, v_t2, v_b2),
        (v_b0, v_b1, v_t1, v_t0),
    ]
    for verts in inlay_faces:
        f = bm.faces.new(verts)
        f.material_index = 2

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_bakelite)
    obj.data.materials.append(mat_cap)
    obj.data.materials.append(mat_inlay)
    bpy.context.collection.objects.link(obj)
    return obj

def main():
    clear_scene()
    knob = create_fluted_bakelite_knob("Knob_05_VCF_Cutoff")
    knob.location = (0.0, 0.0, 0.0)

    BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
    GLB_OUT.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_OUT),
        export_format='GLB',
        export_yup=True,
        export_apply=False
    )
    print(f"CALIBRATION KNOB EXPORTED: {BLEND_OUT} -> {GLB_OUT} ({GLB_OUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
