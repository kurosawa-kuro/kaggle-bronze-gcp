# Review Decision Catalog Prompt

Review the draft against the Context Pack.

Reject or flag:
- catalog_items whose facts are not grounded in the JSON evidence_ids before rendering.
- Markdown body containing machine join keys such as `evidence_ids`.
- inference or risk language presented as fact.
- missing or weak meaning.role / meaning.current_implication.
- grep no-hit treated as absence proof.
- any secret value or reconstructed secret.
- any advice, next action, recommendation, validation plan, rollback plan, or change boundary.