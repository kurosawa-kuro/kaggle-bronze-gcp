# Scan Manifest

schema_version: 1
tool_version: 0.1.0
scan_id: 20260705T044351Z_18f650f404e0
generated_at: 2026-07-05T04:43:51Z
tool: decision-catalog (dcm)
language: infra+node+python
root: /home/ubuntu/repos/kaggle-bronze-challenge
git_commit: 516cac3014fd29562805042ff7d40a234f10ca0b
git_branch: main
git_dirty: false
freshness_status: fresh

query_config_hash: e9dac3c3870d09c48c44a7f09c409e5a055fb41f762463fbe198c0ee6c5769aa
ignore_rules_hash: e8f0b03b63182f211b568f1e240f120892ed77d888a5fbac0075c20478e975a4
source_tree_hash: 4de67242a4b628327b687c78992a70bae4bf779109e7144dc05f628ade9628b2
output_schema_version: 1

profile_resolution:
mode: auto
resolver: deterministic
llm_router_used: false
llm_router_is_evidence: false
candidates: infra,node,python
profiles_run: infra+node+python

requested_profiles: auto
detected_profiles: infra,node,python
coverage_warnings: unsupported extensions detected: csv,parquet,serving,tfevents,tsv

included_file_count: 105
symbol_count: 139
test_count: 0
entrypoint_count: 16

extractor:
  rust: syn AST exact v1 (line fallback only on parse failure)
  python: indent-heuristic v2 (public-by-convention/import/dependency inventory)
  typescript: line-heuristic v2 (export/import/dependency inventory)
  metrics: deterministic loc/symbol counts v1
  grep: substring v1

notes:
  - symbol 抽出は heuristic。macro / 動的生成は取りこぼす（99_scan_limitations.md 参照）。
  - grep no-hit は不存在の証明ではない。
