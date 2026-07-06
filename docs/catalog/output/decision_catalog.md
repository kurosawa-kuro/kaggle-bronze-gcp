review_status: adopted
id: decision_catalog_20260705_kaggle_bronze_challenge
domain: ml_pipeline_and_serving
confidence: medium

# Decision Catalog

fact_source: non_llm_scan
evidence_run_id: 20260705T044351Z_18f650f404e0
machine_provenance: docs/catalog/evidence/evidence_index.jsonl

purpose: upper_model_input
catalog_id: decision_catalog_20260705_kaggle_bronze_challenge
domain: ml_pipeline_and_serving
high_end_ready: medium

## repo_topology

- kind: software_project
- core_files:
  - path: src/config.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/features/__init__.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/features/stellar.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/models/__init__.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/models/catboost_.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/models/ensemble.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/models/lgbm.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/models/xgboost_.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/pipelines/__init__.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/pipelines/evaluate.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/pipelines/featurize.py
    role: 特徴量生成モジュール（make_features）
    catalog_status: core
  - path: src/pipelines/ingest.py
    role: データ取り込み・前処理モジュール（CSV/データセット読み込みとエンコード）
    catalog_status: core
  - path: src/pipelines/score.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/ports.py
    role: domain_model_and_status
    catalog_status: core
  - path: src/runner/__init__.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/experiment/__init__.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/experiment/hp_tune.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/experiment/sweep.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/experiment/train.py
    role: domain_model_and_status
    catalog_status: core
  - path: src/runner/experiment/tune.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/experiment/vertex_run.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/model/__init__.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/model/batch_predict.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/model/deploy.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/model/pipeline.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/model/register.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/ops/__init__.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/ops/collect.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/ops/costs.py
    role: Vertexコスト収集・通知を行う運用モジュール
    catalog_status: core
  - path: src/runner/ops/submit.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/runner/run.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/serving/__init__.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/serving/predictor.py
    role: HTTPベースの推論ハンドラ（AIP互換ルートとストレージ参照を含む）
    catalog_status: core
  - path: src/utils/__init__.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/utils/artifact_store.py
    role: アーティファクト格納/取得ユーティリティ（GCS風URI操作とディレクトリ向けアップロード/ダウンロード）
    catalog_status: core
  - path: src/utils/bq.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
  - path: src/utils/logger.py
    role: low_signal_or_appendix
    catalog_status: low_signal_or_appendix
- runtime_surfaces:
  - CLI arguments
  - file_based_task_storage
- data_surfaces:
  - repo object state surfaces

## coverage_map

- scan_included_files: 105
- topology_files: 37
- catalog_core_items: 10
- covered_as_core:
  - src/runner/experiment/train.py
  - src/serving/predictor.py
  - src/runner/ops/costs.py
  - src/pipelines/ingest.py
  - src/pipelines/featurize.py
  - src/utils/artifact_store.py
  - src/ports.py
  - infra/Dockerfile
- covered_as_appendix:
  - dependency:requirements.txt
  - test_surface:test_count
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
  - src/pipelines/score.py
  - src/runner/__init__.py
  - src/runner/experiment/__init__.py
  - src/runner/experiment/hp_tune.py
  - src/runner/experiment/sweep.py
  - src/runner/experiment/tune.py
  - src/runner/experiment/vertex_run.py
  - src/runner/model/__init__.py
  - src/runner/model/batch_predict.py
  - src/runner/model/deploy.py
  - src/runner/model/pipeline.py
  - src/runner/model/register.py
  - src/runner/ops/__init__.py
  - src/runner/ops/collect.py
  - src/runner/ops/submit.py
  - src/runner/run.py
  - src/serving/__init__.py
  - src/utils/__init__.py
  - src/utils/bq.py
  - src/utils/logger.py
- omitted_or_low_signal:
  - reason: generated/vendor/test fixture/low-signal or scan metadata only

## scan_summary

- profile: infra+node+python
- profile_resolution: requested=auto detected=infra,node,python profiles_run=infra+node+python language=infra+node+python
- scan_included_files: 105
- symbols: 139
- entrypoints: 16
- tests_detected: 0
- high_risk_ops_hits: 11
- no_hit_is_not_absence: true

## flow_items

### primary_task_lifecycle_candidate  {subject_kind: evidence_inferred_flow}
- id: primary_task_lifecycle_candidate
- flow_type: primary_candidate
- grounding_level: strong
- basis:
  - src/runner/experiment/train.py::main
  - src/runner/experiment/train.py::run
  - src/runner/experiment/train.py::_train_lgbm
  - src/utils/artifact_store.py::upload_directory
  - src/utils/artifact_store.py::download_directory
- steps:
  - order: 1
    user_intent: 実験を起動して指定設定でトレーニングを実行したい
    surface: candidate start operation (experiment run entry)
    components: src/runner/experiment/train.py::main, src/runner/experiment/train.py::_parse_args
    data_effect: 実行パラメータを読み取り、実験設定の起点を作る（run への引き渡し準備）。
    confidence: strong
  - order: 2
    user_intent: 指定した構成で実験を実行したい
    surface: candidate config resolution
    components: src/runner/experiment/train.py::_resolve_config, src/runner/experiment/train.py::_cast, src/runner/experiment/train.py::_load_yaml
    data_effect: 設定ファイルとオーバーライドを解決・キャストして実行コンテキストを確定する。
    confidence: strong
  - order: 3
    user_intent: データからモデルを学習し、性能評価とモデルアーティファクトを得たい
    surface: candidate training operation
    components: src/pipelines/ingest.py::load_data, src/pipelines/featurize.py::make_features, src/runner/experiment/train.py::_train_lgbm, src/ports.py::ModelTrainer
    data_effect: データの読み込み→特徴量生成→モデル学習（CV/学習ループ）を実行しモデル重みと評価指標を生成する。
    confidence: strong
  - order: 4
    user_intent: 生成したモデルと成果物を永続化し共有したい
    surface: candidate artifact write & upload operation
    components: src/runner/experiment/train.py::_write_models, src/runner/experiment/train.py::_write_predictions, src/utils/artifact_store.py::upload_directory, src/runner/experiment/train.py::_write_dummy_artifacts
    data_effect: 学習結果（モデル/予測/OOF/重要度等）をファイルへ書き出し、必要に応じてクラウドストレージへアップロードする。ダミーアーティファクト生成ルートも存在する。
    confidence: strong
- cannot_conclude:
  - CLI や外部トリガーからの正確な起動コマンドラインやサブコマンド名はシンボル抽出だけでは確定できない（call graph/entrypoint 引数のバインディングは静的には未解決）。
  - 実際のランタイムでのパラメータ伝達順序やエラー処理の枝は静的シンボルだけでは断定できない。

### deploy_teardown_surface_candidate  {subject_kind: evidence_inferred_flow}
- id: deploy_teardown_surface_candidate
- flow_type: destructive_surface_candidate
- grounding_level: medium
- basis:
  - src/runner/model/deploy.py::deploy
  - src/runner/model/deploy.py::teardown
  - src/utils/artifact_store.py::download_directory
- steps:
  - order: 1
    user_intent: モデルを環境にデプロイして推論を開始したい
    surface: candidate deploy operation
    components: src/runner/model/deploy.py::deploy, src/utils/artifact_store.py::download_directory
    data_effect: リモートアーティファクト／モデルを取得し、指定された環境へ展開してサービングを開始する可能性がある。
    confidence: medium
  - order: 2
    user_intent: デプロイ済みモデルを停止または削除して状態を巻き戻したい
    surface: candidate teardown operation
    components: src/runner/model/deploy.py::teardown
    data_effect: 既存デプロイの停止・リソース解放を行う破壊的操作（テアダウン）を含む可能性がある。
    confidence: medium
- cannot_conclude:
  - デプロイの具体的な外部ターゲット（Vertex 上のサービス名や帳票）の完全な起動手順は静的シンボルだけでは確定できない。
  - CLIやAPI経由でのデプロイ暴露（サブコマンド名やHTTPエンドポイント）は証拠範囲で未確定。

## catalog_items

### src/runner/experiment/train.py  {subject_kind: file}
- role: 実験トレーニングの主要オーケストレータ（引数パース、設定解決、モデル学習、アーティファクト出力）
- implications:
  - このファイルはローカル実験実行と学習アーティファクトの生成を司る主要なオーケストレータとして機能していると考えられる。
  - トレーニングは構成解決→学習→アーティファクト書き出しの典型的なライフサイクルを持っており、CI/デバッグ用のダミーアーティファクト生成ルートも備えている痕跡がある。

### src/serving/predictor.py  {subject_kind: file}
- role: HTTPベースの推論ハンドラ（AIP互換ルートとストレージ参照を含む）
- implications:
  - このモジュールはHTTP予測エンドポイントを提供する実行時サーバ/ハンドラを含み、Google Cloud AI Platform（AIP）向けの環境変数を参照しているため、AIP上での配備／起動を想定したサーブ実装である可能性が高い。
  - 外部ストレージ（AIP_STORAGE_URIやMODEL_DIR等）を参照してモデルを取得・初期化するような動作が想定される。

### src/runner/ops/costs.py  {subject_kind: file}
- role: Vertexコスト収集・通知を行う運用モジュール
- implications:
  - Vertex利用時間やコストを集計・記録し、外部に通知（Discordウェブフック参照）する運用機能を含んでいる。
  - 運用側のコスト可視化・通知がリポジトリ内に実装されているため、ランタイム環境での運用シグナルが生成され得る。

### src/pipelines/ingest.py  {subject_kind: file}
- role: データ取り込み・前処理モジュール（CSV/データセット読み込みとエンコード）
- implications:
  - データパイプラインの入力段に相当し、ローカルCSVや標準データセットからの読み込み経路を提供している。
  - フィーチャ生成の前段として、原データ収集と基本的な前処理（エンコード）がこのモジュールで担われる。

### src/pipelines/featurize.py  {subject_kind: file}
- role: 特徴量生成モジュール（make_features）
- implications:
  - ingest モジュールで読み込まれたデータを受け取り、モデル学習／推論に使える特徴量セットへ変換する責務を持つことが想定される。
  - パイプライン内の中間ステップ（ingest→featurize→score）の一部として機能している。

### src/utils/artifact_store.py  {subject_kind: file}
- role: アーティファクト格納/取得ユーティリティ（GCS風URI操作とディレクトリ向けアップロード/ダウンロード）
- implications:
  - 学習済みモデルや出力アーティファクトの格納/取得にクラウドストレージ（GCS に類するURI）を利用する設計になっている。
  - トレーニングやサービングのアーティファクト入出力はこのユーティリティに依存する可能性が高い。

### src/ports.py  {subject_kind: file}
- role: モデル学習/特徴変換の抽象インターフェース定義（依存注入境界）
- implications:
  - 各モデル実装やパイプラインはこのポートで定義されたインターフェースに合わせて繋がる設計を想定しており、依存注入や差し替えが可能な境界を提供している。
  - 静的証拠からは具体的な実装バインディングは解決できないため、実行時のワイヤリング次第で振る舞いが変わる。

### infra/Dockerfile  {subject_kind: file}
- role: コンテナベースの実行環境定義（python:3.12-slim ベース）
- implications:
  - 開発/配備用イメージは Python 3.12 slim ベースで組まれており、環境変数（PYTHONPATHなど）を通じたパス設定が行われる構成である。
  - ローカルDockerイメージやコンテナ化されたサービング/実験環境を前提としたプロジェクト構成が示唆される。

### dependency:requirements.txt  {subject_kind: dependency}
- role: Pythonパッケージ依存リスト（requirements.txt ベースの依存インベントリ）
- implications:
  - プロジェクトはrequirements.txt ベースの Python 依存管理を行っている痕跡があり、外部ライブラリ群に依存して実行される設計である。
  - 依存リストは環境構築や脆弱性レビューの対象となるが、本事実は依存の存在のみを記述している。

### test_surface:test_count  {subject_kind: test_surface}
- role: テストサーフェス検出結果（scan が test_count: 0 を報告）
- implications:
  - スキャン時点でリポジトリ内にテストとして特定可能なファイル/記述が見つかっていないことを示す（ただしスキャン制限やファイル種別により検出できない場合があり得る）。
  - CIや品質ゲートの観点では、テストの明示的なサーフェスが小さいことを示す指標になる。

## evidence_appendix

- pointer: docs/catalog/evidence/evidence_index.jsonl
- pointer: docs/catalog/evidence/current_run_id
