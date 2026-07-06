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
- L165: function `_load_yaml`
- L171: function `_image_uri`

## src/runner/model/batch_predict.py

- L20: function `submit_batch`
- L99: function `_label_value`
- L103: function `_load_yaml`
- L109: function `main`

## src/runner/model/deploy.py

- L20: function `deploy`
- L69: function `teardown`
- L99: function `_resolve`
- L111: function `_resolve_model`
- L120: function `_load_yaml`
- L126: function `main`

## src/runner/model/pipeline.py

- L27: function `build_and_run`
- L70: function `train_op`
- L79: function `register_op`
- L87: function `_pipeline`
- L134: function `_label_value`
- L138: function `_load_yaml`
- L144: function `_image_uri`
- L151: function `main`

## src/runner/model/register.py

- L24: function `register_from_run`
- L123: function `_find_parent`
- L128: function `_read_cv_score`
- L141: function `_cv_from_text`
- L149: function `_label_value`
- L154: function `_load_yaml`
- L160: function `_image_uri`
- L167: function `_resolve_config`
- L180: function `main`

## src/runner/ops/collect.py

- L10: function `_parse_args`
- L21: function `main`
- L42: function `_load_yaml`

## src/runner/ops/costs.py

- L46: function `_vertex_hourly_usd`
- L53: function `_insert_row`
- L57: function `_parse_ts`
- L61: function `record_vertex`
- L106: function `_webhook_url`
- L113: function `_discord_post`
- L131: function `_month_summary`
- L143: function `_zone_line`
- L151: function `report`
- L163: function `notify`
- L169: function `_load_yaml`
- L173: function `main`

## src/runner/ops/submit.py

- L12: function `_parse_args`
- L22: function `main`

## src/runner/run.py

- L20: function `main`

## src/serving/predictor.py

- L26: function `_resolve_model_dir`
- L37: function `_download`
- L52: class `Predictor`
- L53: method `__init__` parent=Predictor
- L63: method `predict` parent=Predictor
- L72: function `_predictor`
- L79: class `Handler`
- L80: method `_send` parent=Handler
- L88: method `do_GET` parent=Handler
- L94: method `do_POST` parent=Handler
- L106: method `log_message` parent=Handler
- L110: function `main`

## src/utils/artifact_store.py

- L9: class `GcsPrefix`
- L14: method `parse` parent=GcsPrefix
- L23: method `uri` parent=GcsPrefix
- L29: function `upload_directory`
- L45: function `download_directory`
- L63: function `latest_run_id`

## src/utils/bq.py

- L15: function `clean_env`
- L21: function `load_gcp`
- L31: function `query`
- L42: function `lit`
- L54: function `insert_row`

## src/utils/logger.py

- L22: function `_table`
- L26: function `_ensure`
- L46: function `log_run`
- L69: function `show_runs`

