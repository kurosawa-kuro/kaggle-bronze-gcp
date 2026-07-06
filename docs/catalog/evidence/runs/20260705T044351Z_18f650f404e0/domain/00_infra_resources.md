# Infra Domain Evidence

evidence_id: ev.domain.infra

scope: Terraform / GitHub Actions / Dockerfile static definitions.

guardrail:
- IaC 定義は本番に存在する証明ではない。ここでは `found_in` の観測事実だけを出す。
- secret 値は出さず、参照名と場所だけを出す。

## Resources

- kind: `container-base-image`
  name: `python:3.12-slim`
  found_in: infra/Dockerfile:L1

## Secret And Env References

- name: `PYTHONPATH`
  found_in: infra/Dockerfile:L19
  value: redacted (name/参照のみ)
