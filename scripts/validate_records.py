import json
import sys
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parent.parent

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    contract_schema = load_json(ROOT / "schemas" / "contract.schema.json")
    world_schema = load_json(ROOT / "schemas" / "world.schema.json")
    progress_schema = load_json(ROOT / "schemas" / "progress.schema.json")

    contract = load_json(ROOT / "contract.json")
    world = load_json(ROOT / "world.json")
    progress = load_json(ROOT / "progress.json")

    jsonschema.validate(instance=contract, schema=contract_schema)
    jsonschema.validate(instance=world, schema=world_schema)
    jsonschema.validate(instance=progress, schema=progress_schema)

    # Cross-record integrity checks
    assert len(contract["knobs"]) == 16, f"Expected 16 knobs, got {len(contract['knobs'])}"
    assert len(contract["patch_sockets"]) == 12, f"Expected 12 sockets, got {len(contract['patch_sockets'])}"
    assert len(contract["keyboard"]["keys"]) == 25, f"Expected 25 keys, got {len(contract['keyboard']['keys'])}"
    assert contract["keyboard"]["keys"][0]["note_name"] == "C3"
    assert contract["keyboard"]["keys"][-1]["note_name"] == "C5"

    entity_by_id = {e["entity_id"]: e for e in world["entities"]}
    entity_by_node = {e["node_name"]: e for e in world["entities"]}

    # Verify parent references exist
    for e in world["entities"]:
        pid = e["parent_id"]
        if pid is not None and pid not in entity_by_id:
            raise ValueError(f"Entity {e['entity_id']} references missing parent_id {pid}")

    # Verify all contract knobs, sockets, keys, and turntable nodes exist in world.json
    for k in contract["knobs"]:
        assert k["id"] in entity_by_id, f"Missing knob {k['id']} in world.json"
        assert k["node_name"] in entity_by_node, f"Missing knob node {k['node_name']} in world.json"

    for s in contract["patch_sockets"]:
        assert s["id"] in entity_by_id, f"Missing socket {s['id']} in world.json"
        assert s["node_name"] in entity_by_node, f"Missing socket node {s['node_name']} in world.json"

    for key in contract["keyboard"]["keys"]:
        assert key["id"] in entity_by_id, f"Missing key {key['id']} in world.json"
        assert key["node_name"] in entity_by_node, f"Missing key node {key['node_name']} in world.json"

    for req_node in ["Turntable_Platter", "Tonearm_Gimbal", "Tonearm_Headshell", "Turntable_SpeedSwitch", "Turntable_StartStop"]:
        assert req_node in entity_by_node, f"Missing turntable node {req_node} in world.json"

    import shutil
    shutil.copyfile(ROOT / "contract.json", ROOT / "public" / "contract.json")
    shutil.copyfile(ROOT / "world.json", ROOT / "public" / "world.json")

    print(f"VALIDATION PASS: contract.json (16 knobs, 12 sockets, 25 keys C3-C5), world.json ({len(world['entities'])} entities), progress.json (rev {progress['build_revision']}) all valid and synced to public/.")

if __name__ == "__main__":
    main()
