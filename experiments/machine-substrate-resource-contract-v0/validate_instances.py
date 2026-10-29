import json
from pathlib import Path

ROOT = Path(__file__).parent

def main():
    obj=json.loads((ROOT/"CONTRACT-INSTANCES-v0.1.json").read_text())
    errors=[]
    a=obj["instances"]["abstract_machine"]
    r=obj["instances"]["machine_substrate_rev2_1"]

    if a["state_addressing_profile"] != "PROFILE_SET_UNFROZEN":
        errors.append("abstract profile must remain PROFILE_SET_UNFROZEN")
    if set(a["admissible_profiles"]) != {"A0_OPAQUE","A1_RANDOM_ACCESS","A2_SPECIALIZED_INDEX"}:
        errors.append("abstract admissible profiles mismatch")
    required={"source","commit","state_addressing_profile","semantic_transition_access",
              "derived_state_policy","timing","offline_work","persistent_extra_representation",
              "online_access","mutation_model","correctness","classification_status"}
    if set(r) != required:
        errors.append("Rev2.1 instance must declare all frozen dimensions")
    if r["state_addressing_profile"] != "A2_SPECIALIZED_INDEX":
        errors.append("Rev2.1 access profile mismatch")
    if r["online_access"] != "P05_FIBER_LOOKUP":
        errors.append("Rev2.1 P-05 access must be explicit")

    result={"schema":"machine.substrate-resource-contract.instances.validation.v0.1",
            "status":"PASS" if not errors else "FAIL","errors":errors}
    (ROOT/"INSTANCE-VALIDATION-V0.1.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if not errors else 1)

if __name__=="__main__":
    main()
