import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "contract.json"
WORLD_PATH = ROOT / "world.json"
GLB_PATH = ROOT / "public" / "assets" / "models" / "studio_scene.glb"


def parse_glb_json(glb_path: Path) -> dict:
    data = glb_path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    assert magic == b"glTF", f"Invalid GLB magic: {magic}"
    chunk_len, chunk_type = struct.unpack_from("<II", data, 12)
    assert chunk_type == 0x4E4F534A, "First chunk is not JSON"
    json_bytes = data[20 : 20 + chunk_len]
    return json.loads(json_bytes.decode("utf-8"))


def main():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    world = json.loads(WORLD_PATH.read_text(encoding="utf-8"))
    gltf = parse_glb_json(GLB_PATH)

    nodes = gltf.get("nodes", [])
    node_by_name = {}
    parent_by_name = {}

    for idx, n in enumerate(nodes):
        name = n.get("name")
        if name:
            node_by_name[name] = n
        for c_idx in n.get("children", []):
            c_name = nodes[c_idx].get("name")
            if c_name and name:
                parent_by_name[c_name] = name

    # Verify all 64 entities in world.json exist in exported GLB with matching parent hierarchy and position
    entity_node_by_id = {e["entity_id"]: e["node_name"] for e in world["entities"]}
    missing = []
    hierarchy_mismatches = []
    pos_mismatches = []

    for e in world["entities"]:
        n_name = e["node_name"]
        if n_name not in node_by_name:
            missing.append(n_name)
            continue

        expected_parent = entity_node_by_id[e["parent_id"]] if e["parent_id"] else None
        actual_parent = parent_by_name.get(n_name)
        if expected_parent != actual_parent:
            hierarchy_mismatches.append((n_name, expected_parent, actual_parent))

        node = node_by_name[n_name]
        t = node.get("translation", [0.0, 0.0, 0.0])
        exp_t = e["position_m"]
        dist = sum((t[i] - exp_t[i]) ** 2 for i in range(3)) ** 0.5
        if dist > 1e-3:
            pos_mismatches.append((n_name, exp_t, t))

    assert not missing, f"Missing nodes in GLB: {missing}"
    assert not hierarchy_mismatches, f"Hierarchy mismatches in GLB: {hierarchy_mismatches}"
    assert not pos_mismatches, f"Transform position mismatches in GLB: {pos_mismatches}"

    print(
        f"GLB-WORLD VERIFICATION PASS: {len(world['entities'])}/{len(world['entities'])} world.json entities "
        f"verified in {GLB_PATH.name} (0 missing nodes, 0 hierarchy mismatches, 0 position mismatches < 1mm)."
    )


if __name__ == "__main__":
    main()
