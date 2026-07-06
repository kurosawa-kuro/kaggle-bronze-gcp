# Create Decision Catalog Prompt

`00_llm_context_pack.md` の Evidence と Investigated Findings に基づき、Decision Catalog の判断を
**JSON schema に厳密準拠した JSON で** 返す（response_format で強制される）。markdown は書かない。

出力構造:
- `catalog_items`: 上位モデルが読む本体。repo object のみを書く。許可 subject は file / module / symbol / entrypoint / env / dependency / test_surface。
- `flow_items`: 観測される主要フロー候補を書く。product Golden Path 判定ではなく、entrypoint / command surface / touched symbols で弱接地した記述的な動線素材。`catalog_items` は部品、`flow_items` は部品間の方向・順序・候補導線、`evidence_appendix` は scan 足場。
- `scan_summary`: count-only signal、no-hit 注記、scan manifest / metrics / file tree など、意味付け対象ではないが捨ててはいけない scan 概要を書く。
- `evidence_appendix`: parser limitation、generic public API listing、generic change_signal、infra no-hit など、本体 item にしない補助 evidence を書く。

言語ルール:
- prose フィールド（fact.detail / meaning.role / meaning.current_implication）は**日本語**で書く。
- schema のキーと enum 値（confidence, fact.type, observed_by）は英語のまま。

参照ルール（最重要）:
- catalog_items の各項目は `evidence_ids` に、Evidence Index の `evidence_id` 値だけを入れる（例: `ev.03_symbols_md`）。
- `evidence_ids` は必ず `ev.` で始まる値だけ。`item.*` / `src.*` / `path.*` のような repo-object ID を入れない。
- 単数形 `evidence_id` は schema に存在しない。必ず配列 `evidence_ids` だけを使う。
- **file / line / scan_id / sha256 は書かない**。`evidence_ids` も machine join key なので Markdown 本体へ出ない。完全な machine provenance は `evidence_index.jsonl` sidecar に隔離する。
- 存在しない evidence_id を作らない。unknown id は reject される。
- catalog_items の全項目に最低 1 つの evidence_id を付ける。

- flow_items のルール:
- `subject_kind` は必ず `evidence_inferred_flow`。
- `flow_type` は `primary_candidate` / `destructive` / `destructive_surface_candidate` / `decoy_signal` / `config` / `error` / `unknown`。`grounding_level` と step `confidence` は `strong` / `medium` / `weak`。
- `label` は `primary_task_lifecycle_candidate` / `destructive_management_candidate` / `clear_all_surface_candidate` のように観測候補として書く。`Golden Path` / `Critical User Journey` を fact 化しない。
- primary と destructive を混ぜない。primary_candidate に remove/delete/clear の step や basis を入れない。clear は remove と別 flow item にし、`flow_type: destructive_surface_candidate` を使う。CLI 露出が evidence で不明なら `surface: candidate clear operation` として弱く書き、露出ギャップを `cannot_conclude` に残す。
- 各 flow は `basis` を持つ。例: `src/cli.rs::Command`, `src/store.rs::Store::{add,tasks,set_status,remove}`, `src/model.rs::{Task,Status}`。
- 各 step は `user_intent`, `surface`, `components`, `data_effect`, `confidence`, `evidence_ids` を持つ。`components` は repo object、`basis` は根拠シンボル。本文に evidence refs や evidence_ids は出ない。
- `surface` に `task add` のような実サブコマンド名を書けるのは、Command variant / CLI parse evidence で確認できた場合だけ。未確認なら `candidate add operation` / `candidate list operation` / `candidate status update operation` と書く。
- call graph が無い場合は `grounding_level: weak` とし、`cannot_conclude` に「product 上の主要行動かは断定しない」「dispatch 順序は call graph 未導入では弱接地」「CLI サブコマンド実名は未確認」のような接地ギャップを残す。
- flow は処方ではない。守るべき、改善すべき、確認ダイアログを足すべき、`next_action` などを書かない。

- fact は target の事実だけを書く。Evidence Pack や `evidence/` のファイルが存在する、というメタ事実を書かない。

内容ルール:
- catalog_items の fact.path は `/` / 空 / `src/` / evidence artifact 名にしない。`src/cli.rs`, `src/store.rs`, `src/model.rs::Task`, `src/model.rs::Status`, `src/main.rs`, `TASKCLI_DB` のように repo object をキーにする。
- Rust CLI で該当 evidence がある場合、最低限 `src/cli.rs`, `src/store.rs`, `src/model.rs::Task`, `src/model.rs::Status`, `src/main.rs`, `TASKCLI_DB`, `Cargo.toml`, `test_surface` を本体 `catalog_items` に置く。
- `grep` / `change_signal` / `symbols` は catalog_items の fact.type にしない。grep hit は該当 file/symbol item の evidence として吸収する。count のみなら scan_summary へ置く。
- `03_symbols.md 全体`, `30_static_signal_hits.md 全体`, `99_scan_limitations.md 全体` の説明を書かない。それらは repo object を照らす evidence であって subject ではない。
- catalog_items は fact と meaning の対で書く。fact には観測事実だけを書き、推論やリスク含意は meaning.current_implication に置く。
- meaning.role はその項目/ファイルが現在システム内で何であるかを書く。
- meaning.current_implication は現在の含意だけを書く。risk signal は記述的に書いてよいが、何をすべきかは書かない。
- meaning は evidence file を開かずに読める repo 固有の内容にする。「詳細は当該 evidence/インベントリファイルを参照」は禁止。
- `確認が必要` / `確認する必要がある` / `調査が必要` のような次行動要求を書かない。判断に効く未確定の含意は `current_implication` に記述的に書き、判断や追加調査は消費側に残す。
- この禁止は `scan_summary` / `evidence_appendix` にも適用する。appendix も「証拠へのリンク集」ではなく、自己完結した短い要約にする。
- 「TODO は未完了作業を示す」「変更シグナルは最近変更された可能性を示す」「grep hit は静的シグナルである」だけの辞書説明は禁止。
- `domain` は scan profile のコピーではなく、実コード・entrypoint・domain evidence から推定する。YAML/JSON/config があるだけで `infra` にしない。
- `domain: infra` は `domain/00_infra_resources.md` に具体的な infra resource/job/image/env reference がある場合に限定する。`status: no infra domain evidence detected` なら CLI / library / web など主対象の domain を選ぶ。
- `next_action` / `recommended_decision` / `decision_options` / `validation_plan` / `rollback_condition` / `failure_conditions` / `allowed_files` / `max_files_changed` は絶対に書かない。
- grep no-hit を「存在しない」「not found」「absent」と断定しない。低リスク判断でも「検出されていない」ではなく「cited evidence の範囲では小さい/限定的」と書く。
- no-hit に触れる必要がある場合は、必ず「不存在の証明ではない / not proof of absence」と同じ文の中で明記する。
- secret 値を出さない。