import json
import hashlib
from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class ProviderFixture:
    name: str
    role: str
    native_noncanonical_proposal: bool
    notes: str

GITHUB_PR10 = ProviderFixture("GitHub PR #10","contribution",True,"open/unmerged proposal")
AT_RECORD = ProviderFixture("AT Protocol public repository record","contribution",False,"native repository mutation")

def remove_component_checks() -> Dict[str, Dict[str, Any]]:
    return {
        "observation":{"distinction_preserved":False,"collapse":"signal/evidence boundary becomes unobservable","ordinary_data_replacement_possible":True},
        "evidence":{"distinction_preserved":False,"collapse":"observation would need evidentiary status","ordinary_data_replacement_possible":True},
        "authority":{"distinction_preserved":False,"collapse":"evidence/decision would need mutation permission","ordinary_data_replacement_possible":True},
        "decision_acceptance":{"distinction_preserved":False,"collapse":"canonicalization becomes implicit without an explicit decision transition","ordinary_data_replacement_possible":True},
        "contribution_proposal":{"distinction_preserved":False,"collapse":"no explicit proposal locus remains before canonical state","ordinary_data_replacement_possible":True},
        "reconstruction":{"distinction_preserved":False,"collapse":"durable reconstruction contract disappears","ordinary_data_replacement_possible":True},
    }

def main() -> None:
    direct = GITHUB_PR10.native_noncanonical_proposal == AT_RECORD.native_noncanonical_proposal
    result = {
        "schema":"hsdcr-composition-reduction-v0.1",
        "status":"INTERNAL_MODEL_CHECK",
        "scope":"semantic minimization of the current candidate composition",
        "domain_semantics":["proposal/contribution","observation","evidence","authority","decision/acceptance","canonical_state","reconstruction"],
        "substrate_capabilities":["identity","durable state","replication/synchronization","signal transport"],
        "methodological_constraints":["identity != location","signal != evidence","evidence != authority","convergence != acceptance","semantic equivalence != resource equivalence"],
        "behavioral_constraints":["high sensitivity without automatic canonical reaction"],
        "component_removal":remove_component_checks(),
        "substitution":{
            "github_pr_to_at_record_direct":{"semantic_equivalence":direct,"classification":"DIRECT_COLLISION" if not direct else "DIRECT_EQUIVALENT","adapter_required":not direct},
            "evidence_provider_pair":{"normalized_semantics_equivalent":True,"adapter_type":"ordinary-record-normalization"},
            "authority_provider_pair":{"normalized_semantics_equivalent":True,"adapter_type":"ordinary-policy-or-capability-normalization"},
            "reduction_observation":{"known_provider_capabilities_cover_current_functions":True,"new_execution_primitive_detected":False,"new_repository_primitive_detected":False}
        },
        "disposition":{
            "single_family_absorption":"NOT_IDENTIFIED",
            "composition_can_be_described_with_existing_capabilities":True,
            "irreducible_new_semantic_primitive":False,
            "architectural_novelty":"OPEN",
            "protocol_status":"NOT_ASSIGNED",
            "key_residual":"typed separation + explicit acceptance transition between contribution and canonical state",
            "residual_currently_looks_like":"ordinary data + explicit transition/policy composition",
            "next_test":"end-to-end two-provider substitution with durable reconstruction and separated authority/evidence"
        }
    }
    raw=json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False).encode()
    result["canonical_payload_sha256"]=hashlib.sha256(raw).hexdigest()
    print(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
