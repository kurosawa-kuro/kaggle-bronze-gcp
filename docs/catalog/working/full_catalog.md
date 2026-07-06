review_status: adopted

id: decision_catalog_20260705_kaggle_bronze_challenge
domain: ml_pipeline_and_serving
confidence: medium
confidence_policy: capped_to_medium (freshness=fresh, catalog_items=10, distinct_evidence_artifacts=34)
evidence_freshness: high
coverage_confidence: high
meaning_quality: medium
high_end_ready: medium

# Decision Catalog

fact_source: non_llm_scan
evidence_run_id: 20260705T044351Z_18f650f404e0
machine_provenance: docs/catalog/evidence/evidence_index.jsonl

## scan_summary

### scan_manifest
- summary: スキャンメタ情報: language profiles (infra,node,python) が検出され、対象コミットと生成時刻が記録されている。included_file_count: 105、symbol_count: 139、entrypoint_count: 16、test_count: 0。

### file_tree
- summary: ファイルツリーサマリ: notebooks, scripts, src, infra, configs, docs 等を含む。主要なスクリプトとモジュール群が存在するロジック構成が確認される。

### static_signal_counts
- summary: 静的シグナル集計（機械生成）: job_lifecycle=62 hits, env_secret=37 hits, high_risk_ops=11 hits, auth_permission=14 hits, infra_surface=93 hits 等が報告されている（これらは機械的集計であり個別ヒットの文脈で評価されるべきである）。

### tests_overview
- summary: テストサマリ: スキャンは test_count: 0 を報告している。検出されていないことはスキャン範囲における観測結果であり、不存在の完全な証明ではない。

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
- 事実: 実験用トレーニングオーケストレータ。コマンド引数解析、設定の解決、学習実行（少なくともLightGBMの_train関数名での呼び出し痕跡）、およびモデルや予測結果・OOFなどのアーティファクト書き出しを行う一連の関数群（main, run, _train_lgbm, _write_dummy_artifacts, _write_models 等）が存在する。
- 意味あい:
  - 役割: 実験トレーニングの主要オーケストレータ（引数パース、設定解決、モデル学習、アーティファクト出力）
  - 含意: このファイルはローカル実験実行と学習アーティファクトの生成を司る主要なオーケストレータとして機能していると考えられる。
  - 含意: トレーニングは構成解決→学習→アーティファクト書き出しの典型的なライフサイクルを持っており、CI/デバッグ用のダミーアーティファクト生成ルートも備えている痕跡がある。
  - confidence: high

### src/serving/predictor.py  {subject_kind: file}
- 事実: HTTPハンドラ/サーバ用のPredictor実装。do_GET/do_POSTハンドラやpredict/handler等のシンボルがあり、AIP_* 環境変数（AIP_HEALTH_ROUTE等）を参照する箇所が検出されている。
- 意味あい:
  - 役割: HTTPベースの推論ハンドラ（AIP互換ルートとストレージ参照を含む）
  - 含意: このモジュールはHTTP予測エンドポイントを提供する実行時サーバ/ハンドラを含み、Google Cloud AI Platform（AIP）向けの環境変数を参照しているため、AIP上での配備／起動を想定したサーブ実装である可能性が高い。
  - 含意: 外部ストレージ（AIP_STORAGE_URIやMODEL_DIR等）を参照してモデルを取得・初期化するような動作が想定される。
  - confidence: high

### src/runner/ops/costs.py  {subject_kind: file}
- 事実: コスト追跡と通知を扱うops向けモジュール。Vertex関連のコスト計算/記録関数や、通知用にDISCORD_WEBHOOK_URLの参照が検出されている。
- 意味あい:
  - 役割: Vertexコスト収集・通知を行う運用モジュール
  - 含意: Vertex利用時間やコストを集計・記録し、外部に通知（Discordウェブフック参照）する運用機能を含んでいる。
  - 含意: 運用側のコスト可視化・通知がリポジトリ内に実装されているため、ランタイム環境での運用シグナルが生成され得る。
  - confidence: medium

### src/pipelines/ingest.py  {subject_kind: file}
- 事実: データ取り込みモジュール。CSV からの読み込み、California Housing データセット用のロード関数、およびエンコード処理を示す関数群（load_data, _load_from_csv, _load_california_housing, encode）が存在する。
- 意味あい:
  - 役割: データ取り込み・前処理モジュール（CSV/データセット読み込みとエンコード）
  - 含意: データパイプラインの入力段に相当し、ローカルCSVや標準データセットからの読み込み経路を提供している。
  - 含意: フィーチャ生成の前段として、原データ収集と基本的な前処理（エンコード）がこのモジュールで担われる。
  - confidence: high

### src/pipelines/featurize.py  {subject_kind: file}
- 事実: 特徴量生成を行う関数 make_features を含むフィーチャ化モジュールが存在する。
- 意味あい:
  - 役割: 特徴量生成モジュール（make_features）
  - 含意: ingest モジュールで読み込まれたデータを受け取り、モデル学習／推論に使える特徴量セットへ変換する責務を持つことが想定される。
  - 含意: パイプライン内の中間ステップ（ingest→featurize→score）の一部として機能している。
  - confidence: high

### src/utils/artifact_store.py  {subject_kind: file}
- 事実: アーティファクトストア用ユーティリティ。GCS 風のプレフィックス/URI処理やディレクトリ単位のアップロード・ダウンロード、最新ランID取得などの関数が存在する。
- 意味あい:
  - 役割: アーティファクト格納/取得ユーティリティ（GCS風URI操作とディレクトリ向けアップロード/ダウンロード）
  - 含意: 学習済みモデルや出力アーティファクトの格納/取得にクラウドストレージ（GCS に類するURI）を利用する設計になっている。
  - 含意: トレーニングやサービングのアーティファクト入出力はこのユーティリティに依存する可能性が高い。
  - confidence: high

### src/ports.py  {subject_kind: file}
- 事実: 抽象インターフェースを定義するポートモジュール。ModelTrainer クラスや FeatureTransformer の呼び出しポイント、train_cv の共通インターフェースの痕跡がある。
- 意味あい:
  - 役割: モデル学習/特徴変換の抽象インターフェース定義（依存注入境界）
  - 含意: 各モデル実装やパイプラインはこのポートで定義されたインターフェースに合わせて繋がる設計を想定しており、依存注入や差し替えが可能な境界を提供している。
  - 含意: 静的証拠からは具体的な実装バインディングは解決できないため、実行時のワイヤリング次第で振る舞いが変わる。
  - confidence: medium

### infra/Dockerfile  {subject_kind: file}
- 事実: インフラ向けDockerfileが存在し、ベースイメージとして python:3.12-slim を使用している。PYTHONPATH 参照箇所も検出されている。
- 意味あい:
  - 役割: コンテナベースの実行環境定義（python:3.12-slim ベース）
  - 含意: 開発/配備用イメージは Python 3.12 slim ベースで組まれており、環境変数（PYTHONPATHなど）を通じたパス設定が行われる構成である。
  - 含意: ローカルDockerイメージやコンテナ化されたサービング/実験環境を前提としたプロジェクト構成が示唆される。
  - confidence: high

### dependency:requirements.txt  {subject_kind: dependency}
- 事実: 依存関係インベントリが存在する（requirements.txt 等を含む依存一覧の抽出結果）。
- 意味あい:
  - 役割: Pythonパッケージ依存リスト（requirements.txt ベースの依存インベントリ）
  - 含意: プロジェクトはrequirements.txt ベースの Python 依存管理を行っている痕跡があり、外部ライブラリ群に依存して実行される設計である。
  - 含意: 依存リストは環境構築や脆弱性レビューの対象となるが、本事実は依存の存在のみを記述している。
  - confidence: medium

### test_surface:test_count  {subject_kind: test_surface}
- 事実: テストサーフェスの検出結果: スキャンは test_count: 0 を報告している（明示的なテストファイルはスキャン範囲で検出されていない）。
- 意味あい:
  - 役割: テストサーフェス検出結果（scan が test_count: 0 を報告）
  - 含意: スキャン時点でリポジトリ内にテストとして特定可能なファイル/記述が見つかっていないことを示す（ただしスキャン制限やファイル種別により検出できない場合があり得る）。
  - 含意: CIや品質ゲートの観点では、テストの明示的なサーフェスが小さいことを示す指標になる。
  - confidence: medium

## evidence_appendix

### symbols_overview
- summary: 抽出されたシンボル一覧とコード抜粋の集約。各モジュール（ランナー、モデル、パイプライン、ユーティリティ、サービング等）から main/run/train/predict/handler/utility 関連のシンボルが検出されている。

### config_and_env
- summary: 環境変数インベントリ: AIP_* 系のルート/ポート/ストレージ参照、DISCORD_WEBHOOK_URL、KBC_CONFIG_PATH、MODEL_DIR、PYTHONPATH 等の名前参照が検出されている。値は redacted として扱われる。

### scan_limitations
- summary: スキャン制限の要約: シンボル抽出はヒューリスティックであり動的生成やデコレータ登録、grep no-hit は不存在の証明ではない等の制限が報告されている。

### static_signals
- summary: 静的シグナルのサマリ: job_lifecycle、env_secret、high_risk_ops、auth_permission、infra_surface などのクエリでヒットが検出されている（これは機械生成のシグナル一覧であり、各ヒットは個別のファイル/箇所と照合して評価されるべきである）。

### file_tree
- summary: ファイルツリーとファイルインベントリの集約。リポジトリは notebooks, scripts, src, infra, configs, docs 等を含む構造で、entrypoint や docs が多数存在する。

### dependency_inventory
- summary: 依存関係インベントリが抽出されている（requirements.txt 等）。詳細なパッケージリストは依存インベントリに含まれる。
