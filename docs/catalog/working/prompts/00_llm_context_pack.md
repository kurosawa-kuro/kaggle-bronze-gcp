# LLM Context Pack

## Mandatory Rules

- Do not create, overwrite, or backfill Evidence. `evidence/` is read-only Non-LLM input.
- Create `catalog_items` by repo object, not by Evidence artifact. One item key must be a file/module/symbol/entrypoint/env/dependency/test surface in the target repo.
- Evidence artifacts are inputs only. Never make `00_scan_manifest.md`, `03_symbols.md`, `30_static_signal_hits.md`, `99_scan_limitations.md`, `grep`, `change_signal`, `/`, or `src/` into a catalog item.
- Cover every relevant Evidence Index row by attaching evidence_ids to repo-object items, `scan_summary`, or `evidence_appendix`; do not silently drop evidence.
- Facts must describe the target object, not the existence of Evidence Pack files.
- Put count-only grep totals, no-hit notes, parser limitations, scan manifest/metrics/file tree, generic public API listings, and generic change signals in `scan_summary` or `evidence_appendix`, not in `catalog_items`.
- Dependency inventory and test evidence are not mere appendix when present. Create repo-object catalog items for dependency surface (`Cargo.toml` or package manifest) and test surface (`test_count`, test modules, or test files) when the evidence exists.
- A catalog item must be self-contained: an upper model must not need to open `evidence/` or `src/` to understand the object state. Do not write `refer to the evidence file`, `当該ファイルを参照`, or equivalent.
- `scan_summary` and `evidence_appendix` must also be self-contained summaries. Do not write `詳細は証拠`, `証拠を参照`, `文脈確認が必要`, or other next-action wording anywhere in the output.
- Meaning must pass the repo-specific test: could this role/implication have been written without seeing this repo? If yes, move it to appendix or rewrite it around concrete target paths/symbols.
- Add `flow_items` as first-class observed flow candidates when command/entrypoint/symbol evidence exposes connected movement. Use the name `Observed Primary Flow Candidate` conceptually, but the machine label should be descriptive such as `primary_task_lifecycle_candidate`, `destructive_management_candidate`, or `clear_all_surface_candidate`.
- Flow items are descriptive mirror material, not recommendations. Do not call a flow Golden Path or Critical User Journey as fact.
- Keep primary lifecycle and destructive management flows separate. The primary candidate must not include remove/delete/clear steps or basis entries. Clear-all is distinct from remove and must not be merged into the remove flow. If clear evidence exists, create a separate `clear_all_surface_candidate` with `flow_type: destructive_surface_candidate`; when CLI exposure is uncertain, use `surface: candidate clear operation` and put the exposure gap in `cannot_conclude`.
- Do not write real subcommand names such as `task add` unless Command variants or CLI parse evidence confirms that exact surface. If not confirmed, use candidate language such as `candidate add operation` / `candidate list operation` / `candidate status update operation`.
- Each flow must include `basis` and each step must include `user_intent`, `surface`, `components`, `data_effect`, `confidence`, and `evidence_ids` in JSON. Markdown body will render semantic fields only; evidence_ids remain machine-only. If call graph evidence is not available, set `grounding_level: weak` and put the limitation in `cannot_conclude`.
- A grep no-hit is not proof that something does not exist.
- Do not infer, reconstruct, or preserve secret values.
- Keep fact fields Non-LLM and observational; put role and current implications in meaning.
- Do not include advice, recommendations, next actions, validation plans, rollback plans, or change boundaries.

## Domain Selection Rules

- `domain` は scan profile ではなく、target の実コード・entrypoint・domain evidence から見える主対象を書く。
- `profiles_run` / `detected_profiles` に `infra` が含まれていても、それだけで `domain: infra` にしない。YAML/JSON/config は補助 evidence として扱う。
- `domain: infra` は `domain/00_infra_resources.md` に具体的な Terraform / GitHub Actions / Dockerfile resource, job, image, or secret/env reference が観測される場合だけ使う。
- `domain/00_infra_resources.md` が `status: no infra domain evidence detected` の場合、小さな CLI / library / web app の domain を infra にしない。

## Machine Provenance Boundary（重要）

JSON では、下の Evidence IDs 表にある `evidence_id` を `evidence_ids` に入れて接地を示す。存在しない id は禁止。
ただし `evidence_ids` は machine join key であり、最上位モデルの新しいアイディア・設計判断には寄与しない。
最終 Markdown 本体には program が `evidence_ids` / file / line / scan_id / sha256 を一切出さない。完全な machine provenance は `evidence_index.jsonl` sidecar に隔離する。

## Evidence IDs（catalog_items で使える evidence_id）

| evidence_id | file | lines |
|---|---|---|
| ev.00_scan_manifest_md | evidence/00_scan_manifest.md | 1-46 |
| ev.00_evidence_freshness_md | evidence/00_evidence_freshness.md | 1-12 |
| ev.01_file_tree_md | evidence/01_file_tree.md | 1-107 |
| ev.02_files_json | evidence/02_files.json | 1-107 |
| ev.03_symbols_md | evidence/03_symbols.md | 1-231 |
| ev.03_symbols_md.infra_dockerfile | evidence/03_symbols.md | 3-6 |
| ev.03_symbols_md.notebooks_optuna_lgbm_py | evidence/03_symbols.md | 7-10 |
| ev.03_symbols_md.scripts_init_competition_py | evidence/03_symbols.md | 11-19 |
| ev.03_symbols_md.src_features_stellar_py | evidence/03_symbols.md | 20-23 |
| ev.03_symbols_md.src_models_catboost__py | evidence/03_symbols.md | 24-29 |
| ev.03_symbols_md.src_models_ensemble_py | evidence/03_symbols.md | 30-33 |
| ev.03_symbols_md.src_models_lgbm_py | evidence/03_symbols.md | 34-39 |
| ev.03_symbols_md.src_models_xgboost__py | evidence/03_symbols.md | 40-45 |
| ev.03_symbols_md.src_pipelines_evaluate_py | evidence/03_symbols.md | 46-49 |
| ev.03_symbols_md.src_pipelines_featurize_py | evidence/03_symbols.md | 50-53 |
| ev.03_symbols_md.src_pipelines_ingest_py | evidence/03_symbols.md | 54-60 |
| ev.03_symbols_md.src_pipelines_score_py | evidence/03_symbols.md | 61-65 |
| ev.03_symbols_md.src_ports_py | evidence/03_symbols.md | 66-72 |
| ev.03_symbols_md.src_runner_experiment_hp_tune_py | evidence/03_symbols.md | 73-76 |
| ev.03_symbols_md.src_runner_experiment_sweep_py | evidence/03_symbols.md | 77-80 |
| ev.03_symbols_md.src_runner_experiment_train_py | evidence/03_symbols.md | 81-105 |
| ev.03_symbols_md.src_runner_experiment_tune_py | evidence/03_symbols.md | 106-114 |
| ev.03_symbols_md.src_runner_experiment_vertex_run_py | evidence/03_symbols.md | 115-123 |
| ev.03_symbols_md.src_runner_model_batch_predict_py | evidence/03_symbols.md | 124-130 |
| ev.03_symbols_md.src_runner_model_deploy_py | evidence/03_symbols.md | 131-139 |
| ev.03_symbols_md.src_runner_model_pipeline_py | evidence/03_symbols.md | 140-150 |
| ev.03_symbols_md.src_runner_model_register_py | evidence/03_symbols.md | 151-162 |
| ev.03_symbols_md.src_runner_ops_collect_py | evidence/03_symbols.md | 163-168 |
| ev.03_symbols_md.src_runner_ops_costs_py | evidence/03_symbols.md | 169-183 |
| ev.03_symbols_md.src_runner_ops_submit_py | evidence/03_symbols.md | 184-188 |
| ev.03_symbols_md.src_runner_run_py | evidence/03_symbols.md | 189-192 |
| ev.03_symbols_md.src_serving_predictor_py | evidence/03_symbols.md | 193-207 |
| ev.03_symbols_md.src_utils_artifact_store_py | evidence/03_symbols.md | 208-216 |
| ev.03_symbols_md.src_utils_bq_py | evidence/03_symbols.md | 217-224 |
| ev.03_symbols_md.src_utils_logger_py | evidence/03_symbols.md | 225-231 |
| ev.03_symbols_md.infra_dockerfile.python_3_12_slim.l5 | evidence/03_symbols.md | 5-5 |
| ev.03_symbols_md.notebooks_optuna_lgbm_py.objective.l9 | evidence/03_symbols.md | 9-9 |
| ev.03_symbols_md.scripts_init_competition_py.download.l13 | evidence/03_symbols.md | 13-13 |
| ev.03_symbols_md.scripts_init_competition_py.find_csv.l14 | evidence/03_symbols.md | 14-14 |
| ev.03_symbols_md.scripts_init_competition_py.normalize.l15 | evidence/03_symbols.md | 15-15 |
| ev.03_symbols_md.scripts_init_competition_py.analyze.l16 | evidence/03_symbols.md | 16-16 |
| ev.03_symbols_md.scripts_init_competition_py.create_doc.l17 | evidence/03_symbols.md | 17-17 |
| ev.03_symbols_md.scripts_init_competition_py.main.l18 | evidence/03_symbols.md | 18-18 |
| ev.03_symbols_md.src_features_stellar_py.add_stellar_fe.l22 | evidence/03_symbols.md | 22-22 |
| ev.03_symbols_md.src_models_catboost__py.train_cv.l26 | evidence/03_symbols.md | 26-26 |
| ev.03_symbols_md.src_models_catboost__py.splits.l27 | evidence/03_symbols.md | 27-27 |
| ev.03_symbols_md.src_models_catboost__py.log.l28 | evidence/03_symbols.md | 28-28 |
| ev.03_symbols_md.src_models_ensemble_py.average.l32 | evidence/03_symbols.md | 32-32 |
| ev.03_symbols_md.src_models_lgbm_py.train_cv.l36 | evidence/03_symbols.md | 36-36 |
| ev.03_symbols_md.src_models_lgbm_py.splits.l37 | evidence/03_symbols.md | 37-37 |
| ev.03_symbols_md.src_models_lgbm_py.log.l38 | evidence/03_symbols.md | 38-38 |
| ev.03_symbols_md.src_models_xgboost__py.train_cv.l42 | evidence/03_symbols.md | 42-42 |
| ev.03_symbols_md.src_models_xgboost__py.splits.l43 | evidence/03_symbols.md | 43-43 |
| ev.03_symbols_md.src_models_xgboost__py.log.l44 | evidence/03_symbols.md | 44-44 |
| ev.03_symbols_md.src_pipelines_evaluate_py.cv_score.l48 | evidence/03_symbols.md | 48-48 |
| ev.03_symbols_md.src_pipelines_featurize_py.make_features.l52 | evidence/03_symbols.md | 52-52 |
| ev.03_symbols_md.src_pipelines_ingest_py.load_data.l56 | evidence/03_symbols.md | 56-56 |
| ev.03_symbols_md.src_pipelines_ingest_py.load_from_csv.l57 | evidence/03_symbols.md | 57-57 |
| ev.03_symbols_md.src_pipelines_ingest_py.load_california_housing.l58 | evidence/03_symbols.md | 58-58 |
| ev.03_symbols_md.src_pipelines_ingest_py.encode.l59 | evidence/03_symbols.md | 59-59 |
| ev.03_symbols_md.src_pipelines_score_py.predict.l63 | evidence/03_symbols.md | 63-63 |
| ev.03_symbols_md.src_pipelines_score_py.make_submission.l64 | evidence/03_symbols.md | 64-64 |
| ev.03_symbols_md.src_ports_py.modeltrainer.l68 | evidence/03_symbols.md | 68-68 |
| ev.03_symbols_md.src_ports_py.train_cv.l69 | evidence/03_symbols.md | 69-69 |
| ev.03_symbols_md.src_ports_py.featuretransformer.l70 | evidence/03_symbols.md | 70-70 |
| ev.03_symbols_md.src_ports_py.call.l71 | evidence/03_symbols.md | 71-71 |
| ev.03_symbols_md.src_runner_experiment_hp_tune_py.main.l75 | evidence/03_symbols.md | 75-75 |
| ev.03_symbols_md.src_runner_experiment_sweep_py.main.l79 | evidence/03_symbols.md | 79-79 |
| ev.03_symbols_md.src_runner_experiment_train_py.parse_args.l83 | evidence/03_symbols.md | 83-83 |
| ev.03_symbols_md.src_runner_experiment_train_py.parse_overrides.l84 | evidence/03_symbols.md | 84-84 |
| ev.03_symbols_md.src_runner_experiment_train_py.cast.l85 | evidence/03_symbols.md | 85-85 |
| ev.03_symbols_md.src_runner_experiment_train_py.resolve_config.l86 | evidence/03_symbols.md | 86-86 |
| ev.03_symbols_md.src_runner_experiment_train_py.main.l87 | evidence/03_symbols.md | 87-87 |
| ev.03_symbols_md.src_runner_experiment_train_py.run.l88 | evidence/03_symbols.md | 88-88 |
| ev.03_symbols_md.src_runner_experiment_train_py.train_lgbm.l89 | evidence/03_symbols.md | 89-89 |
| ev.03_symbols_md.src_runner_experiment_train_py.report_hp_metric.l90 | evidence/03_symbols.md | 90-90 |
| ev.03_symbols_md.src_runner_experiment_train_py.load_yaml.l91 | evidence/03_symbols.md | 91-91 |
| ev.03_symbols_md.src_runner_experiment_train_py.make_run_id.l92 | evidence/03_symbols.md | 92-92 |
| ev.03_symbols_md.src_runner_experiment_train_py.write_config_snapshot.l93 | evidence/03_symbols.md | 93-93 |
| ev.03_symbols_md.src_runner_experiment_train_py.write_dummy_artifacts.l94 | evidence/03_symbols.md | 94-94 |
| ev.03_symbols_md.src_runner_experiment_train_py.trained_mask.l95 | evidence/03_symbols.md | 95-95 |
| ev.03_symbols_md.src_runner_experiment_train_py.write_oof.l96 | evidence/03_symbols.md | 96-96 |
| ev.03_symbols_md.src_runner_experiment_train_py.write_predictions.l97 | evidence/03_symbols.md | 97-97 |
| ev.03_symbols_md.src_runner_experiment_train_py.write_models.l98 | evidence/03_symbols.md | 98-98 |
| ev.03_symbols_md.src_runner_experiment_train_py.write_feature_importance.l99 | evidence/03_symbols.md | 99-99 |
| ev.03_symbols_md.src_runner_experiment_train_py.tee.l100 | evidence/03_symbols.md | 100-100 |
| ev.03_symbols_md.src_runner_experiment_train_py.init.l101 | evidence/03_symbols.md | 101-101 |
| ev.03_symbols_md.src_runner_experiment_train_py.write.l102 | evidence/03_symbols.md | 102-102 |
| ev.03_symbols_md.src_runner_experiment_train_py.flush.l103 | evidence/03_symbols.md | 103-103 |
| ev.03_symbols_md.src_runner_experiment_train_py.tee_stdout.l104 | evidence/03_symbols.md | 104-104 |
| ev.03_symbols_md.src_runner_experiment_tune_py.load_yaml.l108 | evidence/03_symbols.md | 108-108 |
| ev.03_symbols_md.src_runner_experiment_tune_py.direction.l109 | evidence/03_symbols.md | 109-109 |
| ev.03_symbols_md.src_runner_experiment_tune_py.search_space.l110 | evidence/03_symbols.md | 110-110 |
| ev.03_symbols_md.src_runner_experiment_tune_py.run.l111 | evidence/03_symbols.md | 111-111 |
| ev.03_symbols_md.src_runner_experiment_tune_py.objective.l112 | evidence/03_symbols.md | 112-112 |
| ev.03_symbols_md.src_runner_experiment_tune_py.main.l113 | evidence/03_symbols.md | 113-113 |
| ev.03_symbols_md.src_runner_experiment_vertex_run_py.parse_args.l117 | evidence/03_symbols.md | 117-117 |
| ev.03_symbols_md.src_runner_experiment_vertex_run_py.submit_from_config.l118 | evidence/03_symbols.md | 118-118 |
| ev.03_symbols_md.src_runner_experiment_vertex_run_py.main.l119 | evidence/03_symbols.md | 119-119 |
| ev.03_symbols_md.src_runner_experiment_vertex_run_py.label_value.l120 | evidence/03_symbols.md | 120-120 |
| ev.03_symbols_md.src_runner_experiment_vertex_run_py.load_yaml.l121 | evidence/03_symbols.md | 121-121 |
| ev.03_symbols_md.src_runner_experiment_vertex_run_py.image_uri.l122 | evidence/03_symbols.md | 122-122 |
| ev.03_symbols_md.src_runner_model_batch_predict_py.submit_batch.l126 | evidence/03_symbols.md | 126-126 |
| ev.03_symbols_md.src_runner_model_batch_predict_py.label_value.l127 | evidence/03_symbols.md | 127-127 |
| ev.03_symbols_md.src_runner_model_batch_predict_py.load_yaml.l128 | evidence/03_symbols.md | 128-128 |
| ev.03_symbols_md.src_runner_model_batch_predict_py.main.l129 | evidence/03_symbols.md | 129-129 |
| ev.03_symbols_md.src_runner_model_deploy_py.deploy.l133 | evidence/03_symbols.md | 133-133 |
| ev.03_symbols_md.src_runner_model_deploy_py.teardown.l134 | evidence/03_symbols.md | 134-134 |
| ev.03_symbols_md.src_runner_model_deploy_py.resolve.l135 | evidence/03_symbols.md | 135-135 |
| ev.03_symbols_md.src_runner_model_deploy_py.resolve_model.l136 | evidence/03_symbols.md | 136-136 |
| ev.03_symbols_md.src_runner_model_deploy_py.load_yaml.l137 | evidence/03_symbols.md | 137-137 |
| ev.03_symbols_md.src_runner_model_deploy_py.main.l138 | evidence/03_symbols.md | 138-138 |
| ev.03_symbols_md.src_runner_model_pipeline_py.build_and_run.l142 | evidence/03_symbols.md | 142-142 |
| ev.03_symbols_md.src_runner_model_pipeline_py.train_op.l143 | evidence/03_symbols.md | 143-143 |
| ev.03_symbols_md.src_runner_model_pipeline_py.register_op.l144 | evidence/03_symbols.md | 144-144 |
| ev.03_symbols_md.src_runner_model_pipeline_py.pipeline.l145 | evidence/03_symbols.md | 145-145 |
| ev.03_symbols_md.src_runner_model_pipeline_py.label_value.l146 | evidence/03_symbols.md | 146-146 |
| ev.03_symbols_md.src_runner_model_pipeline_py.load_yaml.l147 | evidence/03_symbols.md | 147-147 |
| ev.03_symbols_md.src_runner_model_pipeline_py.image_uri.l148 | evidence/03_symbols.md | 148-148 |
| ev.03_symbols_md.src_runner_model_pipeline_py.main.l149 | evidence/03_symbols.md | 149-149 |
| ev.03_symbols_md.src_runner_model_register_py.register_from_run.l153 | evidence/03_symbols.md | 153-153 |
| ev.03_symbols_md.src_runner_model_register_py.find_parent.l154 | evidence/03_symbols.md | 154-154 |
| ev.03_symbols_md.src_runner_model_register_py.read_cv_score.l155 | evidence/03_symbols.md | 155-155 |
| ev.03_symbols_md.src_runner_model_register_py.cv_from_text.l156 | evidence/03_symbols.md | 156-156 |
| ev.03_symbols_md.src_runner_model_register_py.label_value.l157 | evidence/03_symbols.md | 157-157 |
| ev.03_symbols_md.src_runner_model_register_py.load_yaml.l158 | evidence/03_symbols.md | 158-158 |
| ev.03_symbols_md.src_runner_model_register_py.image_uri.l159 | evidence/03_symbols.md | 159-159 |
| ev.03_symbols_md.src_runner_model_register_py.resolve_config.l160 | evidence/03_symbols.md | 160-160 |
| ev.03_symbols_md.src_runner_model_register_py.main.l161 | evidence/03_symbols.md | 161-161 |
| ev.03_symbols_md.src_runner_ops_collect_py.parse_args.l165 | evidence/03_symbols.md | 165-165 |
| ev.03_symbols_md.src_runner_ops_collect_py.main.l166 | evidence/03_symbols.md | 166-166 |
| ev.03_symbols_md.src_runner_ops_collect_py.load_yaml.l167 | evidence/03_symbols.md | 167-167 |
| ev.03_symbols_md.src_runner_ops_costs_py.vertex_hourly_usd.l171 | evidence/03_symbols.md | 171-171 |
| ev.03_symbols_md.src_runner_ops_costs_py.insert_row.l172 | evidence/03_symbols.md | 172-172 |
| ev.03_symbols_md.src_runner_ops_costs_py.parse_ts.l173 | evidence/03_symbols.md | 173-173 |
| ev.03_symbols_md.src_runner_ops_costs_py.record_vertex.l174 | evidence/03_symbols.md | 174-174 |
| ev.03_symbols_md.src_runner_ops_costs_py.webhook_url.l175 | evidence/03_symbols.md | 175-175 |
| ev.03_symbols_md.src_runner_ops_costs_py.discord_post.l176 | evidence/03_symbols.md | 176-176 |
| ev.03_symbols_md.src_runner_ops_costs_py.month_summary.l177 | evidence/03_symbols.md | 177-177 |
| ev.03_symbols_md.src_runner_ops_costs_py.zone_line.l178 | evidence/03_symbols.md | 178-178 |
| ev.03_symbols_md.src_runner_ops_costs_py.report.l179 | evidence/03_symbols.md | 179-179 |
| ev.03_symbols_md.src_runner_ops_costs_py.notify.l180 | evidence/03_symbols.md | 180-180 |
| ev.03_symbols_md.src_runner_ops_costs_py.load_yaml.l181 | evidence/03_symbols.md | 181-181 |
| ev.03_symbols_md.src_runner_ops_costs_py.main.l182 | evidence/03_symbols.md | 182-182 |
| ev.03_symbols_md.src_runner_ops_submit_py.parse_args.l186 | evidence/03_symbols.md | 186-186 |
| ev.03_symbols_md.src_runner_ops_submit_py.main.l187 | evidence/03_symbols.md | 187-187 |
| ev.03_symbols_md.src_runner_run_py.main.l191 | evidence/03_symbols.md | 191-191 |
| ev.03_symbols_md.src_serving_predictor_py.resolve_model_dir.l195 | evidence/03_symbols.md | 195-195 |
| ev.03_symbols_md.src_serving_predictor_py.download.l196 | evidence/03_symbols.md | 196-196 |
| ev.03_symbols_md.src_serving_predictor_py.predictor.l197 | evidence/03_symbols.md | 197-197 |
| ev.03_symbols_md.src_serving_predictor_py.init.l198 | evidence/03_symbols.md | 198-198 |
| ev.03_symbols_md.src_serving_predictor_py.predict.l199 | evidence/03_symbols.md | 199-199 |
| ev.03_symbols_md.src_serving_predictor_py.predictor.l200 | evidence/03_symbols.md | 200-200 |
| ev.03_symbols_md.src_serving_predictor_py.handler.l201 | evidence/03_symbols.md | 201-201 |
| ev.03_symbols_md.src_serving_predictor_py.send.l202 | evidence/03_symbols.md | 202-202 |
| ev.03_symbols_md.src_serving_predictor_py.do_get.l203 | evidence/03_symbols.md | 203-203 |
| ev.03_symbols_md.src_serving_predictor_py.do_post.l204 | evidence/03_symbols.md | 204-204 |
| ev.03_symbols_md.src_serving_predictor_py.log_message.l205 | evidence/03_symbols.md | 205-205 |
| ev.03_symbols_md.src_serving_predictor_py.main.l206 | evidence/03_symbols.md | 206-206 |
| ev.03_symbols_md.src_utils_artifact_store_py.gcsprefix.l210 | evidence/03_symbols.md | 210-210 |
| ev.03_symbols_md.src_utils_artifact_store_py.parse.l211 | evidence/03_symbols.md | 211-211 |
| ev.03_symbols_md.src_utils_artifact_store_py.uri.l212 | evidence/03_symbols.md | 212-212 |
| ev.03_symbols_md.src_utils_artifact_store_py.upload_directory.l213 | evidence/03_symbols.md | 213-213 |
| ev.03_symbols_md.src_utils_artifact_store_py.download_directory.l214 | evidence/03_symbols.md | 214-214 |
| ev.03_symbols_md.src_utils_artifact_store_py.latest_run_id.l215 | evidence/03_symbols.md | 215-215 |
| ev.03_symbols_md.src_utils_bq_py.clean_env.l219 | evidence/03_symbols.md | 219-219 |
| ev.03_symbols_md.src_utils_bq_py.load_gcp.l220 | evidence/03_symbols.md | 220-220 |
| ev.03_symbols_md.src_utils_bq_py.query.l221 | evidence/03_symbols.md | 221-221 |
| ev.03_symbols_md.src_utils_bq_py.lit.l222 | evidence/03_symbols.md | 222-222 |
| ev.03_symbols_md.src_utils_bq_py.insert_row.l223 | evidence/03_symbols.md | 223-223 |
| ev.03_symbols_md.src_utils_logger_py.table.l227 | evidence/03_symbols.md | 227-227 |
| ev.03_symbols_md.src_utils_logger_py.ensure.l228 | evidence/03_symbols.md | 228-228 |
| ev.03_symbols_md.src_utils_logger_py.log_run.l229 | evidence/03_symbols.md | 229-229 |
| ev.03_symbols_md.src_utils_logger_py.show_runs.l230 | evidence/03_symbols.md | 230-230 |
| ev.04_symbols_json | evidence/04_symbols.json | 1-141 |
| ev.05_tests_md | evidence/05_tests.md | 1-3 |
| ev.07_entrypoints_md | evidence/07_entrypoints.md | 1-18 |
| ev.08_config_env_md | evidence/08_config_env.md | 1-50 |
| ev.08_config_env_md.scan_limitations | evidence/08_config_env.md | 46-50 |
| ev.09_diff_evidence_md | evidence/09_diff_evidence.md | 1-42 |
| ev.09_diff_evidence_md.working_tree | evidence/09_diff_evidence.md | 5-10 |
| ev.09_diff_evidence_md.staged_files | evidence/09_diff_evidence.md | 11-16 |
| ev.09_diff_evidence_md.unstaged_files | evidence/09_diff_evidence.md | 17-22 |
| ev.09_diff_evidence_md.last_commit_files | evidence/09_diff_evidence.md | 23-28 |
| ev.09_diff_evidence_md.since_scope | evidence/09_diff_evidence.md | 29-42 |
| ev.10_observed_change_signals_md | evidence/10_observed_change_signals.md | 1-33 |
| ev.10_observed_change_signals_md.notes | evidence/10_observed_change_signals.md | 30-33 |
| ev.10_observed_change_signals_json | evidence/10_observed_change_signals.json | 1-153 |
| ev.11_dependency_inventory_md | evidence/11_dependency_inventory.md | 1-239 |
| ev.11_dependency_inventory_md.guardrail | evidence/11_dependency_inventory.md | 237-239 |
| ev.11_dependency_inventory_json | evidence/11_dependency_inventory.json | 1-229 |
| ev.12_code_metrics_md | evidence/12_code_metrics.md | 1-62 |
| ev.12_code_metrics_md.guardrail | evidence/12_code_metrics.md | 60-62 |
| ev.12_code_metrics_json | evidence/12_code_metrics.json | 1-52 |
| ev.13_public_api_surface_md | evidence/13_public_api_surface.md | 1-82 |
| ev.13_public_api_surface_md.guardrail | evidence/13_public_api_surface.md | 80-82 |
| ev.13_public_api_surface_json | evidence/13_public_api_surface.json | 1-72 |
| ev.14_code_excerpts_md | evidence/14_code_excerpts.md | 1-342 |
| ev.14_code_excerpts_md.infra_dockerfile_1_4__python_3_12_slim | evidence/14_code_excerpts.md | 7-17 |
| ev.14_code_excerpts_md.notebooks_optuna_lgbm_py_35_41__objective | evidence/14_code_excerpts.md | 18-31 |
| ev.14_code_excerpts_md.scripts_init_competition_py_76_82__analyze | evidence/14_code_excerpts.md | 32-45 |
| ev.14_code_excerpts_md.scripts_init_competition_py_130_136__create_doc | evidence/14_code_excerpts.md | 46-59 |
| ev.14_code_excerpts_md.scripts_init_competition_py_17_23__download | evidence/14_code_excerpts.md | 60-73 |
| ev.14_code_excerpts_md.scripts_init_competition_py_144_150__main | evidence/14_code_excerpts.md | 74-87 |
| ev.14_code_excerpts_md.scripts_init_competition_py_46_52__normalize | evidence/14_code_excerpts.md | 88-101 |
| ev.14_code_excerpts_md.src_features_stellar_py_3_9__add_stellar_fe | evidence/14_code_excerpts.md | 102-115 |
| ev.14_code_excerpts_md.src_models_catboost__py_16_22__train_cv | evidence/14_code_excerpts.md | 116-129 |
| ev.14_code_excerpts_md.src_models_ensemble_py_2_8__average | evidence/14_code_excerpts.md | 130-143 |
| ev.14_code_excerpts_md.src_models_lgbm_py_24_30__train_cv | evidence/14_code_excerpts.md | 144-157 |
| ev.14_code_excerpts_md.src_models_xgboost__py_21_27__train_cv | evidence/14_code_excerpts.md | 158-171 |
| ev.14_code_excerpts_md.src_pipelines_evaluate_py_5_11__cv_score | evidence/14_code_excerpts.md | 172-185 |
| ev.14_code_excerpts_md.src_pipelines_featurize_py_11_17__make_features | evidence/14_code_excerpts.md | 186-199 |
| ev.14_code_excerpts_md.src_pipelines_ingest_py_54_60__encode | evidence/14_code_excerpts.md | 200-213 |
| ev.14_code_excerpts_md.src_pipelines_ingest_py_8_14__load_data | evidence/14_code_excerpts.md | 214-227 |
| ev.14_code_excerpts_md.src_pipelines_score_py_14_20__make_submission | evidence/14_code_excerpts.md | 228-241 |
| ev.14_code_excerpts_md.src_pipelines_score_py_9_15__predict | evidence/14_code_excerpts.md | 242-255 |
| ev.14_code_excerpts_md.src_ports_py_23_29__featuretransformer | evidence/14_code_excerpts.md | 256-269 |
| ev.14_code_excerpts_md.src_ports_py_8_14__modeltrainer | evidence/14_code_excerpts.md | 270-283 |
| ev.14_code_excerpts_md.src_ports_py_13_19__train_cv | evidence/14_code_excerpts.md | 284-297 |
| ev.14_code_excerpts_md.src_runner_experiment_hp_tune_py_17_23__main | evidence/14_code_excerpts.md | 298-311 |
| ev.14_code_excerpts_md.src_runner_experiment_sweep_py_12_18__main | evidence/14_code_excerpts.md | 312-325 |
| ev.14_code_excerpts_md.src_runner_experiment_train_py_367_373__flush | evidence/14_code_excerpts.md | 326-339 |
| ev.14_code_excerpts_md.guardrail | evidence/14_code_excerpts.md | 340-342 |
| ev.14_code_excerpts_json | evidence/14_code_excerpts.json | 1-26 |
| ev.15_decision_memory_md | evidence/15_decision_memory.md | 1-5 |
| ev.15_decision_memory_json | evidence/15_decision_memory.json | 1-3 |
| ev.domain_00_infra_resources_md | evidence/domain/00_infra_resources.md | 1-21 |
| ev.domain_00_infra_resources_md.resources | evidence/domain/00_infra_resources.md | 11-16 |
| ev.domain_00_infra_resources_md.secret_and_env_references | evidence/domain/00_infra_resources.md | 17-21 |
| ev.30_static_signal_hits_md | evidence/30_static_signal_hits.md | 1-22 |
| ev.30_static_signal_hits_md.guardrail | evidence/30_static_signal_hits.md | 20-22 |
| ev.98_redaction_report_md | evidence/98_redaction_report.md | 1-20 |
| ev.99_scan_limitations_md | evidence/99_scan_limitations.md | 1-18 |
| ev.99_scan_limitations_md.parser_limitations__infra_node_python | evidence/99_scan_limitations.md | 3-9 |
| ev.99_scan_limitations_md.search_limitations | evidence/99_scan_limitations.md | 10-14 |
| ev.99_scan_limitations_md.current_limits | evidence/99_scan_limitations.md | 15-18 |
| ev.grep_01_todos_md | evidence/grep/01_todos.md | 1-8 |
| ev.grep_02_job_lifecycle_md | evidence/grep/02_job_lifecycle.md | 1-67 |
| ev.grep_03_env_secret_md | evidence/grep/03_env_secret.md | 1-42 |
| ev.grep_04_high_risk_ops_md | evidence/grep/04_high_risk_ops.md | 1-16 |
| ev.grep_05_auth_permission_md | evidence/grep/05_auth_permission.md | 1-19 |
| ev.grep_06_infra_surface_md | evidence/grep/06_infra_surface.md | 1-98 |
| ev.grep_99_no_hits_md | evidence/grep/99_no_hits.md | 1-10 |
| ev.grep_99_no_hits_md.todos | evidence/grep/99_no_hits.md | 3-10 |
| ev.grep_00_queries_json | evidence/grep/00_queries.json | 1-8 |

## Evidence Inputs

### evidence/00_scan_manifest.md

```markdown
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
```

### evidence/03_symbols.md

```markdown
# Symbols

## infra/Dockerfile

- L1: container-base-image `python:3.12-slim`

## notebooks/optuna_lgbm.py

- L38: function `objective`

## scripts/init_competition.py

- L20: function `download`
- L40: function `_find_csv`
- L49: function `normalize`
- L79: function `analyze`
- L133: function `create_doc`
- L147: function `main`

## src/features/stellar.py

- L6: function `add_stellar_fe`

## src/models/catboost_.py

- L19: function `train_cv`
- L65: function `_splits`
- L71: function `_log`

## src/models/ensemble.py

- L5: function `average`

## src/models/lgbm.py

- L27: function `train_cv`
- L86: function `_splits`
- L92: function `_log`

## src/models/xgboost_.py

- L24: function `train_cv`
- L71: function `_splits`
- L77: function `_log`

## src/pipelines/evaluate.py

- L8: function `cv_score`

## src/pipelines/featurize.py

- L14: function `make_features`

## src/pipelines/ingest.py

- L11: function `load_data`
- L30: function `_load_from_csv`
- L41: function `_load_california_housing`
- L57: function `encode`

## src/pipelines/score.py

- L12: function `predict`
- L17: function `make_submission`

## src/ports.py

- L11: class `ModelTrainer`
- L16: method `train_cv` parent=ModelTrainer
- L26: class `FeatureTransformer`
- L34: method `__call__` parent=FeatureTransformer

## src/runner/experiment/hp_tune.py

- L20: function `main`

## src/runner/experiment/sweep.py

- L15: function `main`

## src/runner/experiment/train.py

- L19: function `_parse_args`
- L38: function `_parse_overrides`
- L60: function `_cast`
- L69: function `_resolve_config`
- L83: function `main`
- L104: function `run`
- L166: function `_train_lgbm`
- L251: function `_report_hp_metric`
- L264: function `_load_yaml`
- L268: function `_make_run_id`
- L273: function `_write_config_snapshot`
- L277: function `_write_dummy_artifacts`
- L295: function `_trained_mask`
- L301: function `_write_oof`
- L312: function `_write_predictions`
- L321: function `_write_models`
- L347: function `_write_feature_importance`
- L360: class `_Tee`
- L361: method `__init__` parent=_Tee
- L364: method `write` parent=_Tee
- L370: method `flush` parent=_Tee
- L376: function `_tee_stdout`

## src/runner/experiment/tune.py

- L20: function `_load_yaml`
- L24: function `_direction`
- L28: function `_search_space`
- L40: function `run`
- L72: function `objective`
- L107: function `main`

## src/runner/experiment/vertex_run.py

- L11: function `_parse_args`
- L31: function `submit_from_config`
- L136: function `main`
- L158: function `_label_value`

[truncated for context pack]
```

### evidence/08_config_env.md

```markdown
# Config / Env Inventory

- AIP_HEALTH_ROUTE
  found_in:
    - src/serving/predictor.py:L21
  value: redacted (name/参照のみ)
  requiredness: unknown
- AIP_HTTP_PORT
  found_in:
    - src/serving/predictor.py:L23
  value: redacted (name/参照のみ)
  requiredness: unknown
- AIP_PREDICT_ROUTE
  found_in:
    - src/serving/predictor.py:L22
  value: redacted (name/参照のみ)
  requiredness: unknown
- AIP_STORAGE_URI
  found_in:
    - src/serving/predictor.py:L31
  value: redacted (name/参照のみ)
  requiredness: unknown
- DISCORD_WEBHOOK_URL
  found_in:
    - src/runner/ops/costs.py:L107
  value: redacted (name/参照のみ)
  requiredness: unknown
- KBC_CONFIG_PATH
  found_in:
    - src/config.py:L7
    - src/runner/experiment/train.py:L167
    - src/runner/experiment/tune.py:L53
  value: redacted (name/参照のみ)
  requiredness: unknown
- MODEL_DIR
  found_in:
    - src/serving/predictor.py:L28
  value: redacted (name/参照のみ)
  requiredness: unknown
- PYTHONPATH
  found_in:
    - infra/Dockerfile:L19
  value: redacted (name/参照のみ)
  requiredness: unknown

## Scan Limitations

- required/optional は未確認。
- default 値は解析していない。
- secret 値は含めない。
```

### evidence/30_static_signal_hits.md

```markdown
# Static Signal Hits

This is a machine-generated signal inventory, not a decision.
Every row points back to grep evidence.

| query_id | hit_state | hits | evidence_ref | follow_up |
|---|---|---:|---|---|
| `todos` | `no_hit` | 0 | `file=evidence/grep/01_todos.md query_id=todos` | treat as no-hit, not absence |
| `job_lifecycle` | `matched` | 62 | `file=evidence/grep/02_job_lifecycle.md query_id=job_lifecycle` | review matching lines before deciding |
| `env_secret` | `matched` | 37 | `file= <REDACTED>
| `high_risk_ops` | `matched` | 11 | `file=evidence/grep/04_high_risk_ops.md query_id=high_risk_ops` | review matching lines before deciding |
| `auth_permission` | `matched` | 14 | `file=evidence/grep/05_auth_permission.md query_id=auth_permission` | review matching lines before deciding |
| `infra_surface` | `matched` | 93 | `file=evidence/grep/06_infra_surface.md query_id=infra_surface` | review matching lines before deciding |
| `change_signal:docs/02_architecture.md` | `observed` | 15 | `file=evidence/10_observed_change_signals.md path=docs/02_architecture.md` | inspect change history before editing |
| `change_signal:Makefile` | `observed` | 14 | `file=evidence/10_observed_change_signals.md path=Makefile` | inspect change history before editing |
| `change_signal:docs/01_requirements.md` | `observed` | 13 | `file=evidence/10_observed_change_signals.md path=docs/01_requirements.md` | inspect change history before editing |
| `change_signal:docs/04_workflows.md` | `observed` | 12 | `file=evidence/10_observed_change_signals.md path=docs/04_workflows.md` | inspect change history before editing |
| `change_signal:CLAUDE.md` | `observed` | 12 | `file=evidence/10_observed_change_signals.md path=CLAUDE.md` | inspect change history before editing |

## Guardrail

- Static signal entries are observations only. Decision Catalog claims still need explicit `evidence_ref` values.
```

### evidence/99_scan_limitations.md

```markdown
# Scan Limitations

## Parser Limitations (infra+node+python)

- シンボル抽出は行ベース heuristic であり AST ではない。
- Rust: macro / proc-macro 生成、複数行シグネチャ、conditional compilation は取りこぼす。
- Python: 動的生成 class/function、デコレータ経由の登録、import hook は静的には見えない。
- impl 内メソッドと自由関数の区別（Rust）は近似。

## Search Limitations

- grep は指定 query 語彙に依存する。no-hit は不存在の証明ではない。
- 同義語・ドメイン固有命名は取りこぼす可能性がある。

## Current Limits

- 検出したシンボルの責務は未判定（investigate / Decision Catalog で扱う）。
- env の required/optional、secret の取り扱いは未確認。
```

### evidence/evidence_index.jsonl

```markdown
{"evidence_id":"ev.00_scan_manifest_md","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"00_scan_manifest.md","line_start":1,"line_end":46,"sha256":"f01a53094ebc02c54a6e9088e8e01899c4acf23ad85764a253b9539be1d19681"}
{"evidence_id":"ev.00_evidence_freshness_md","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"00_evidence_freshness.md","line_start":1,"line_end":12,"sha256":"6aec92e28f3c2593819a16dd392f38a99a3a8f2681d88708963be426b7f0e943"}
{"evidence_id":"ev.01_file_tree_md","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"01_file_tree.md","line_start":1,"line_end":107,"sha256":"57836a629b1a481ec58d8de952a687da8f17cdaf276d436d485d4652ac934172"}
{"evidence_id":"ev.02_files_json","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"02_files.json","line_start":1,"line_end":107,"sha256":"0b91e945e9126d0e0cdf08b36252144ee3271a5f0b790cac83970921b4a503b6"}
{"evidence_id":"ev.03_symbols_md","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":1,"line_end":231,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.infra_dockerfile","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":3,"line_end":6,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.notebooks_optuna_lgbm_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":7,"line_end":10,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.scripts_init_competition_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":11,"line_end":19,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_features_stellar_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":20,"line_end":23,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_catboost__py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":24,"line_end":29,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_ensemble_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":30,"line_end":33,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_lgbm_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":34,"line_end":39,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_xgboost__py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":40,"line_end":45,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_evaluate_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":46,"line_end":49,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_featurize_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":50,"line_end":53,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_ingest_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":54,"line_end":60,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_score_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":61,"line_end":65,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_ports_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":66,"line_end":72,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_hp_tune_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":73,"line_end":76,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_sweep_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":77,"line_end":80,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":81,"line_end":105,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_tune_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":106,"line_end":114,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_vertex_run_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":115,"line_end":123,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_batch_predict_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":124,"line_end":130,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_deploy_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":131,"line_end":139,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_pipeline_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":140,"line_end":150,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_register_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":151,"line_end":162,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_ops_collect_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":163,"line_end":168,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_ops_costs_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":169,"line_end":183,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_ops_submit_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":184,"line_end":188,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_run_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":189,"line_end":192,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_serving_predictor_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":193,"line_end":207,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_utils_artifact_store_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":208,"line_end":216,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_utils_bq_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":217,"line_end":224,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_utils_logger_py","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":225,"line_end":231,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.infra_dockerfile.python_3_12_slim.l5","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":5,"line_end":5,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.notebooks_optuna_lgbm_py.objective.l9","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":9,"line_end":9,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.scripts_init_competition_py.download.l13","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":13,"line_end":13,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.scripts_init_competition_py.find_csv.l14","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":14,"line_end":14,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.scripts_init_competition_py.normalize.l15","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":15,"line_end":15,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.scripts_init_competition_py.analyze.l16","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":16,"line_end":16,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.scripts_init_competition_py.create_doc.l17","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":17,"line_end":17,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.scripts_init_competition_py.main.l18","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":18,"line_end":18,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_features_stellar_py.add_stellar_fe.l22","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":22,"line_end":22,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_catboost__py.train_cv.l26","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":26,"line_end":26,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_catboost__py.splits.l27","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":27,"line_end":27,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_catboost__py.log.l28","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":28,"line_end":28,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_ensemble_py.average.l32","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":32,"line_end":32,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_lgbm_py.train_cv.l36","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":36,"line_end":36,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_lgbm_py.splits.l37","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":37,"line_end":37,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_lgbm_py.log.l38","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":38,"line_end":38,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_xgboost__py.train_cv.l42","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":42,"line_end":42,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_xgboost__py.splits.l43","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":43,"line_end":43,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_models_xgboost__py.log.l44","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":44,"line_end":44,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_evaluate_py.cv_score.l48","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":48,"line_end":48,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_featurize_py.make_features.l52","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":52,"line_end":52,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_ingest_py.load_data.l56","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":56,"line_end":56,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_ingest_py.load_from_csv.l57","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":57,"line_end":57,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_ingest_py.load_california_housing.l58","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":58,"line_end":58,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_ingest_py.encode.l59","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":59,"line_end":59,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_score_py.predict.l63","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":63,"line_end":63,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_pipelines_score_py.make_submission.l64","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":64,"line_end":64,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_ports_py.modeltrainer.l68","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":68,"line_end":68,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_ports_py.train_cv.l69","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":69,"line_end":69,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_ports_py.featuretransformer.l70","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":70,"line_end":70,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_ports_py.call.l71","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":71,"line_end":71,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_hp_tune_py.main.l75","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":75,"line_end":75,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_sweep_py.main.l79","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":79,"line_end":79,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.parse_args.l83","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":83,"line_end":83,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.parse_overrides.l84","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":84,"line_end":84,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.cast.l85","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":85,"line_end":85,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.resolve_config.l86","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":86,"line_end":86,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.main.l87","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":87,"line_end":87,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.run.l88","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":88,"line_end":88,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.train_lgbm.l89","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":89,"line_end":89,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.report_hp_metric.l90","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":90,"line_end":90,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.load_yaml.l91","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":91,"line_end":91,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.make_run_id.l92","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":92,"line_end":92,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.write_config_snapshot.l93","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":93,"line_end":93,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.write_dummy_artifacts.l94","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":94,"line_end":94,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.trained_mask.l95","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":95,"line_end":95,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.write_oof.l96","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":96,"line_end":96,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.write_predictions.l97","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":97,"line_end":97,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.write_models.l98","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":98,"line_end":98,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.write_feature_importance.l99","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":99,"line_end":99,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.tee.l100","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":100,"line_end":100,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.init.l101","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":101,"line_end":101,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.write.l102","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":102,"line_end":102,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.flush.l103","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":103,"line_end":103,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_train_py.tee_stdout.l104","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":104,"line_end":104,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_tune_py.load_yaml.l108","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":108,"line_end":108,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_tune_py.direction.l109","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":109,"line_end":109,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_tune_py.search_space.l110","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":110,"line_end":110,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_tune_py.run.l111","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":111,"line_end":111,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_tune_py.objective.l112","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":112,"line_end":112,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_tune_py.main.l113","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":113,"line_end":113,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_vertex_run_py.parse_args.l117","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":117,"line_end":117,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_vertex_run_py.submit_from_config.l118","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":118,"line_end":118,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_vertex_run_py.main.l119","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":119,"line_end":119,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_vertex_run_py.label_value.l120","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":120,"line_end":120,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_vertex_run_py.load_yaml.l121","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":121,"line_end":121,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_experiment_vertex_run_py.image_uri.l122","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":122,"line_end":122,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_batch_predict_py.submit_batch.l126","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":126,"line_end":126,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_batch_predict_py.label_value.l127","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":127,"line_end":127,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_batch_predict_py.load_yaml.l128","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":128,"line_end":128,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_batch_predict_py.main.l129","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":129,"line_end":129,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_deploy_py.deploy.l133","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":133,"line_end":133,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_deploy_py.teardown.l134","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":134,"line_end":134,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_deploy_py.resolve.l135","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":135,"line_end":135,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_deploy_py.resolve_model.l136","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":136,"line_end":136,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_deploy_py.load_yaml.l137","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":137,"line_end":137,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_deploy_py.main.l138","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":138,"line_end":138,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_pipeline_py.build_and_run.l142","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":142,"line_end":142,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_pipeline_py.train_op.l143","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":143,"line_end":143,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_pipeline_py.register_op.l144","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":144,"line_end":144,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_pipeline_py.pipeline.l145","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":145,"line_end":145,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_pipeline_py.label_value.l146","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":146,"line_end":146,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_pipeline_py.load_yaml.l147","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":147,"line_end":147,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_pipeline_py.image_uri.l148","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":148,"line_end":148,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}
{"evidence_id":"ev.03_symbols_md.src_runner_model_pipeline_py.main.l149","scan_id":"20260705T044351Z_18f650f404e0","target_git_commit":"516cac3014fd29562805042ff7d40a234f10ca0b","artifact":"03_symbols.md","line_start":149,"line_end":149,"sha256":"bdcad1eba9af7a3ea63d879228a1ae161809d23ca45f2ecdfd3e34d95bc00c5e"}

[truncated for context pack]
```

### evidence/01_file_tree.md

```markdown
# File Tree

- .claude/rules/docs.md
- .claude/rules/security.md
- .claude/skills/create-task/SKILL.md
- .claude/skills/execute-task/SKILL.md
- .claude/skills/hallucination-check/SKILL.md
- .claude/skills/project-review/SKILL.md
- .claude/skills/refactor-plan/SKILL.md
- .claude/skills/review-task/SKILL.md
- .claude/skills/skeleton-first/SKILL.md
- .claude/skills/write-spec/SKILL.md
- .dockerignore
- .gitignore
- AGENTS.md
- CLAUDE.md
- Makefile
- README.md
- SPEC.md
- catboost_info/catboost_training.json
- catboost_info/learn/events.out.tfevents
- catboost_info/learn_error.tsv
- catboost_info/test/events.out.tfevents
- catboost_info/test_error.tsv
- catboost_info/time_left.tsv
- configs/lgbm_baseline.yaml
- configs/lgbm_deep.yaml
- data/playground-series-s6e6/interim/test.parquet
- data/playground-series-s6e6/interim/train.parquet
- data/playground-series-s6e6/raw/sample_submission.csv
- data/playground-series-s6e6/raw/test.csv
- data/playground-series-s6e6/raw/train.csv
- docs/00_index.md
- docs/01_requirements.md
- docs/02_architecture.md
- docs/03_domain_model.md
- docs/04_workflows.md
- docs/05_data_model.md
- docs/06_error_policy.md
- docs/07_test_strategy.md
- docs/08_release_runbook.md
- docs/adr/0001-vertex-ready-experiment-runner.md
- docs/adr/0002-full-vertex-non-dl.md
- docs/competitions/README.md
- docs/competitions/_template.md
- docs/competitions/california_housing.md
- docs/competitions/rogii-wellbore-geology-prediction.md
- docs/competitions/stellar-class/README.md
- docs/competitions/titanic.md
- docs/competitions/データ取得方法.md
- docs/tasks/README.md
- docs/tasks/active/refactoring-candidates.md
- docs/tasks/active/vertex-ready-runner.md
- docs/tasks/backlog/汎用的コード.md
- docs/tasks/done/cost-tracking-bigquery.md
- docs/tasks/done/hpo-leverage-phase1.md
- docs/tasks/done/superseded-vertex-ready-runner-direction-note.md
- doppler.yaml
- env/config.yaml
- env/project.yaml
- env/secret.example.yaml
- env/secret.yaml
- infra/Dockerfile
- infra/Dockerfile.serving
- notebooks/exp001_lgbm_base.py
- notebooks/exp002_catboost_base.py
- notebooks/exp003_ensemble_lgbm_cat.py
- notebooks/optuna_lgbm.py
- requirements.txt
- scripts/init_competition.py
- src/config.py
- src/features/__init__.py
- src/features/stellar.py
- src/models/__init__.py
- src/models/catboost_.py
- src/models/ensemble.py
- src/models/lgbm.py
- src/models/xgboost_.py
- src/pipelines/__init__.py
- src/pipelines/evaluate.py
- src/pipelines/featurize.py
- src/pipelines/ingest.py
- src/pipelines/score.py
- src/ports.py
- src/runner/__init__.py
- src/runner/experiment/__init__.py
- src/runner/experiment/hp_tune.py
- src/runner/experiment/sweep.py
- src/runner/experiment/train.py
- src/runner/experiment/tune.py
- src/runner/experiment/vertex_run.py
- src/runner/model/__init__.py
- src/runner/model/batch_predict.py
- src/runner/model/deploy.py
- src/runner/model/pipeline.py
- src/runner/model/register.py
- src/runner/ops/__init__.py
- src/runner/ops/collect.py
- src/runner/ops/costs.py
- src/runner/ops/submit.py
- src/runner/run.py
- src/serving/__init__.py
- src/serving/predictor.py
- src/utils/__init__.py
- src/utils/artifact_store.py
- src/utils/bq.py
- src/utils/logger.py
```

### evidence/98_redaction_report.md

```markdown
# Redaction Report

status: passed
redacted_count: 3

checked_keywords:
  - secret
  - token
  - password
  - api_key
  - apikey
  - key

scope:
  - env_secret grep の代入形 (`KEY = ...` / `KEY: <REDACTED>

notes:
  - name / 参照箇所は残し、value のみ `<redacted>` に置換している。
  - これは網羅的な secret スキャンではない（高エントロピー文字列検出は対象外）。
  - env 参照の呼び出し（env::var / os.environ）は value を持たないため redaction 対象外。
```

## Investigated Findings

```markdown
# Investigated Findings

generated_by: dcm investigate
source: non_llm_evidence_investigation
judgment_status: llm_enriched

## observed_signals

- Evidence Pack exists and has the required scan, symbol, config, risk, and scan-limitation files. evidence_ref: file=evidence/00_scan_manifest.md
- Symbol evidence exists for code navigation and candidate responsibility boundaries. evidence_ref: file=evidence/03_symbols.md
- Configuration and environment evidence exists for secret and runtime-risk review. evidence_ref: file=evidence/08_config_env.md
- Static signal evidence exists and must be investigated before draft. evidence_ref: file=evidence/30_static_signal_hits.md
- Scan limitation evidence exists and can inform descriptive current implications when judgment-relevant. evidence_ref: file=evidence/99_scan_limitations.md

## available_evidence_files

- `00_evidence_freshness.md`
- `00_scan_manifest.md`
- `01_file_tree.md`
- `02_files.json`
- `03_symbols.md`
- `04_symbols.json`
- `05_tests.md`
- `07_entrypoints.md`
- `08_config_env.md`
- `09_diff_evidence.md`
- `10_observed_change_signals.json`
- `10_observed_change_signals.md`
- `11_dependency_inventory.json`
- `11_dependency_inventory.md`
- `12_code_metrics.json`
- `12_code_metrics.md`
- `13_public_api_surface.json`
- `13_public_api_surface.md`
- `14_code_excerpts.json`
- `14_code_excerpts.md`
- `15_decision_memory.json`
- `15_decision_memory.md`
- `30_static_signal_hits.md`
- `98_redaction_report.md`
- `99_scan_limitations.md`

## llm_enrichment

## item_meaning_candidates

- `src/runner/experiment/train.py` appears to be the primary training orchestrator, comprising argument parsing, config resolution, model training (LGBM at least), artifact writing, and stdout tee-ing. Reference: symbols in `evidence/03_symbols.md` for `src/runner/experiment/train.py`.
- `src/serving/predictor.py` implements a custom HTTP `Handler` (`do_GET`, `do_POST`) that loads a `Predictor` class for inference, and references AI Platform (AIP) environment variables (`AIP_HEALTH_ROUTE`, `AIP_HTTP_PORT`, `AIP_PREDICT_ROUTE`, `AIP_STORAGE_URI`). Reference: `evidence/08_config_env.md` (AIP_* env vars), `evidence/03_symbols.md` (`Predictor`, `Handler`).
- `src/runner/ops/costs.py` records Vertex AI usage costs and sends Discord notifications via `DISCORD_WEBHOOK_URL`. Reference: `evidence/08_config_env.md` for `DISCORD_WEBHOOK_URL`; symbols in `evidence/03_symbols.md` for functions `record_vertex`, `report`, `notify`.
- `src/pipelines/featurize.py` contains `make_features` and `src/pipelines/ingest.py` contains `load_data`, suggesting a data pipeline that loads from CSV or California housing dataset and encodes features. Reference: `evidence/03_symbols.md` for those symbols.
- `src/utils/artifact_store.py` provides GCS upload/download and `latest_run_id` utility, indicating reliance on Google Cloud Storage for artifacts. Reference: symbols in `evidence/03_symbols.md`.
- `src/utils/bq.py` exposes BigQuery query and insert operations, suggesting logging or storing results to BigQuery. Reference: symbols in `evidence/03_symbols.md`.
- The presence of `src/models/ensemble.py` with an `average` function and separate model modules (`lgbm`, `xgboost_`, `catboost_`) suggests ensemble averaging as a prediction strategy. Reference: `evidence/03_symbols.md`.
- `infra/Dockerfile` uses `python:3.12-slim` as base image and sets `PYTHONPATH`. Reference: `evidence/08_config_env.md` for `PYTHONPATH`; `evidence/03_symbols.md` for container-base-image.

## role_notes

- `src/pipelines/` modules (`ingest`, `featurize`, `score`, `evaluate`) form a classic ML data pipeline: ingest → featurize → score (predict) → evaluate (CV score). Reference: symbols in `evidence/03_symbols.md`.
- `src/models/` modules each expose a `train_cv` function and internal helper `_splits` and `_log`, indicating a consistent cross‑validation interface across LightGBM, XGBoost, CatBoost, and ensemble. Reference: `evidence/03_symbols.md` for each model file.
- `src/runner/experiment/` hosts experiment‑level orchestration: `train.py`, `tune.py` (hyperparameter tuning with Optuna per `notebooks/optuna_lgbm.py`), `hp_tune.py`, `sweep.py`, and `vertex_run.py` for submitting to Vertex AI. Reference: symbols in `evidence/03_symbols.md`.
- `src/runner/model/` manages model deployment lifecycle: `register.py` (register from run), `deploy.py` (deploy/teardown), `batch_predict.py`, and `pipeline.py` (build Vertex AI pipeline). Reference: symbols in `evidence/03_symbols.md`.
- `src/utils/` provides infrastructure utilities: artifact store (GCS), BigQuery, logger, and config. Reference: symbols in `evidence/03_symbols.md`.
- The entrypoints (`scripts/init_competition.py`, `src/runner/run.py`, etc.) indicate distinct invocation modes: data initialization, experiment runs, serving, and ops (costs, collect, submit). Reference: `evidence/07_entrypoints.md` (not provided in full but entrypoint_count=16 suggests many). The symbols in `evidence/03_symbols.md` also show `main` functions in multiple scripts.
- `notebooks/optuna_lgbm.py` contains an Optuna `objective` function, likely used for hyperparameter search outside the main experiment orchestration. Reference: `evidence/03_symbols.md`.

## current_implications

- Serving is designed to run on Google Cloud AI Platform (AIP) due to the presence of `AIP_` environment variables and the `Handler` class with health and predict routes. Reference: `evidence/08_config_env.md` (AIP_* entries) and `evidence/03_symbols.md` (predictor.py symbols).
- Cost tracking via Vertex AI and Discord notifications is actively implemented, implying operational monitoring. Reference: `evidence/30_static_signal_hits.md` (high_risk_ops matched 11 hits) and `evidence/08_config_env.md` (`DISCORD_WEBHOOK_URL`).
- Several documentation files (`docs/01_requirements.md`, `docs/02_architecture.md`, `docs/04_workflows.md`) and `CLAUDE.md` have observed change signals, indicating active documentation evolution. Reference: `evidence/30_static_signal_hits.md` (`change_signal:*` entries).
- The project uses multiple model implementations (LGBM, XGBoost, CatBoost) with a common CV interface, suggesting the user runs benchmarks or ensemble experiments. Reference: `evidence/03_symbols.md` (model files).
- The `_write_dummy_artifacts` function in `train.py` (symbol L277) suggests the training pipeline can produce placeholder artifacts, possibly for debugging or CI. Reference: `evidence/03_symbols.md`.
- No tests are detected (`test_count: 0` in `evidence/00_scan_manifest.md`), which implies either tests are absent, excluded, or not captured by the scan (e.g., in unsupported extensions). Reference: `evidence/00_scan_manifest.md`.
- The scan detected no TODO comments (`todos` no_hit in `evidence/30_static_signal_hits.md`), though that does not prove absence (per scan limitations).
- `src/ports.py` defines abstract interfaces (`ModelTrainer`, `FeatureTransformer`), but their concrete implementations are not statically resolvable to specific classes, suggesting dependency injection or dynamic dispatch. Reference: `evidence/03_symbols.md`.

## uncertainty_notes

- Requiredness and default values for all environment variables are unknown; the scan only recorded names/references. Reference: `evidence/08_config_env.md` (value redacted, requiredness unknown).
- The symbol extraction is heuristic‑based; dynamic code (e.g., decorator‑registered endpoints, class‑factory functions) may be missed. Reference: `evidence/99_scan_limitations.md` (parser limitations).
- The absence of test files (`test_count: 0`) may be due to test files having unsupported extensions (e.g., `.csv`, `.parquet`) or being in directories excluded by `.gitignore`; not confirmed absence. Reference: `evidence/99_scan_limitations.md` and `evidence/00_scan_manifest.md`.
- The “no-hit” for `todos` does not guarantee no TODOs exist; grep depends on query vocabulary. Reference: `evidence/30_static_signal_hits.md` (guardrail) and `evidence/99_scan_limitations.md`.
- The relationship between the Optuna notebook (`notebooks/optuna_lgbm.py`) and the experiment tuning scripts (`src/runner/experiment/tune.py`) is unclear from static symbols alone — they may share logic or be separate workflows.
- `src/ports.py` interfaces (`ModelTrainer`, `FeatureTransformer`) have no concrete static bindings; the runtime wiring is not visible in the evidence.
- The `secret` values (e.g., `DISCORD_WEBHOOK_URL`) are redacted; actual secrets may be present in the repository but are excluded from the scan output. Reference: <REDACTED>
- The scan manifest notes unsupported extensions (`.csv`, `.parquet`, `.serving`, `.tfevents`, `.tsv`) which could contain additional configuration or model artifacts not analyzed. Reference: `evidence/00_scan_manifest.md`.
- The `src/runner/ops/collect.py` and `src/runner/ops/submit.py` functions have limited documented purpose from symbols; their exact behavior is not fully derivable.

## judgment_value_added

- Raw inventory has been classified into draft inputs: observed signals, roles, and current implications.
- LLM enrichment, when present, adds meaning for each evidence item without changing observed evidence.
- This file does not approve an implementation choice or prescribe future work. It prevents raw scan output from being treated as a completed Decision Catalog.

## draft_inputs

- Draft must create `catalog_items` where each item pairs fact and meaning.
- Draft must not include advice, recommendations, next actions, validation plans, rollback plans, or change boundaries.
- Draft must cite evidence_ids for fact items and must not invent facts outside the Evidence Pack.

## required_llm_enrichment

- Assign role/current implication to evidence items.
- Keep risk language descriptive and current-state only.
- Put judgment-relevant uncertainty in descriptive current implications instead of a separate field.

## next_step

- Run `dcm draft <TARGET>` or `dcm llm draft <TARGET>` only after this investigated findings file exists.
```
