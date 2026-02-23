def export_to_coq_stub(theorem_name: str, statement: str) -> str:
    return f"Theorem {theorem_name} : {statement}.\nProof. Admitted.\n"
