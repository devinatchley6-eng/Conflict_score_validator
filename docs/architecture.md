# Architecture

The DCS Validator combines five layers:

1. **Core geometry**: field construction and blob extraction.
2. **Inference**: METIS operator set with a lightweight adaptive bandit.
3. **Conflict modeling**: MIS extraction and aggregate conflict energy.
4. **Safety**: Atchley invariant monitor and deepfreeze intervention.
5. **Certification**: statistical controls and formal proof export stubs.

The intended pipeline is:

`input observations -> scalar field -> blob topology -> conflict energy -> safety checks -> certification`.
