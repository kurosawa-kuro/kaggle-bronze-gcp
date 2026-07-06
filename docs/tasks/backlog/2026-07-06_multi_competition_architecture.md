# 複数 Kaggle コンペを低コストで切り替えるアーキテクチャ調査

## Goal

このプロジェクトを特定の Kaggle コンペ専用ではなく、ブロンズ取得まで複数コンペへ素早く乗り換えられる実験基盤にする。

目標状態:

```text
新コンペ参加時に必要な作業 =
  1. make init COMP=<slug>
  2. 生成された competition config を確認
  3. smoke → full → Vertex → submit

原則として src/ の共通コードは触らない。
```

## 調査結果

現状は「config 駆動」に見えるが、実際には `env/config.yaml` と `configs/*.yaml` と `src/config.py` の import-time 定数が混在している。そのため、`CONFIG=configs/<new_comp>.yaml` だけで安全にコンペ切替できる構造ではない。

特に問題が大きい箇所:

| 問題 | 影響 | 根拠 |
|---|---|---|
| `src/config.py` が import 時に `env/config.yaml` を読む | `CONFIG=...` を変えても、先に import 済みの `TARGET` / `METRIC` / `OBJECTIVE` / `DATA_RAW` が古いまま残り得る | `src/config.py` |
| `train.run()` の `--input-uri` staging が `KBC_CONFIG_PATH` 設定前に `from config import DATA_RAW` する | Vertex 実行で新コンペ config を渡しても、GCS raw を旧 comp の `data/<old>/raw` に落とす危険がある | `src/runner/experiment/train.py` |
| `Makefile stage-data` が `env/config.yaml` の `comp` を読む | `make stage-data CONFIG=configs/new.yaml` で新コンペではなく旧コンペを GCS へ upload し得る | `Makefile: COMP_DATA` |
| `pipelines.ingest/featurize/score/evaluate` と `models/*` が global config を import | コンペ切替、metric 切替、objective 切替が module cache に依存する | `src/pipelines/*.py`, `src/models/*.py` |
| `make init` が nested config を生成せず、下書きを表示するだけ | 新コンペ開始時に手作業が多く、ミスりやすい | `scripts/init_competition.py` |
| `sample_submission.csv` を正本として扱っていない | 提出形式が id+target だけではないコンペで壊れる | `src/pipelines/score.py` |
| データローダが `train.csv` / `test.csv` 前提 | 複数ファイル、外部メタデータ、時系列、画像パス付き表形式などに弱い | `src/pipelines/ingest.py` |
| FE が共通 entrypoint に固定で、コンペ固有 FE は未配線 | コンペ切替のたびに共通コードを編集しがち | `src/features/stellar.py`, `src/pipelines/featurize.py` |
| CV 戦略が objective から KFold/StratifiedKFold を自動選択するだけ | GroupKFold / TimeSeriesSplit / fold column / adversarial split が必要なコンペに弱い | `src/models/lgbm.py`, `train.py` |
| metric が `rmse` / `auc` / `logloss` のみ | Kaggle で多い RMSLE / MAE / QWK / F1 / MAP@K / custom metric に弱い | `src/pipelines/evaluate.py` |

## 結論

GCP/Vertex/Terraform 部分はかなり再利用可能。問題は GCP ではなく、**コンペ仕様が共通パイプラインに漏れていること**。

必要な方向性は「大きな MLOps 化」ではなく、以下の境界整理:

```text
GCP 基盤           = 全コンペ共通
runner / train    = 全コンペ共通
CompetitionSpec   = コンペごとの設定
CompetitionPlugin = コンペごとの loader / features / submission / metric / CV
```

## 推奨アーキテクチャ

### 1. `ExperimentConfig` / `CompetitionSpec` を導入する

`src/config.py` の global 定数を正本にしない。config YAML を読み、明示的なオブジェクトとして関数へ渡す。

目標例:

```python
cfg = ExperimentConfig.load(config_path)
train_df, test_df, sample = load_data(cfg.data)
X_train, y_train, X_test, meta = build_features(cfg, train_df, test_df)
oof, models = train_model(cfg, X_train, y_train)
submission = make_submission(cfg, preds, test_df, sample)
```

`KBC_CONFIG_PATH` は段階的に廃止し、どうしても互換が必要な旧経路だけに閉じ込める。

### 2. config schema を「コンペ仕様」と「実験仕様」に分ける

推奨 schema:

```yaml
competition:
  slug: "playground-series-s6e6"
  title: "Stellar Classification"
  task_type: "multiclass"
  target: "class"
  id_col: "id"
  metric: "logloss"
  lower_is_better: true
  sample_submission: "sample_submission.csv"
  plugin: "generic_tabular"

data:
  raw_dir: "data/${competition.slug}/raw"
  train_file: "train.csv"
  test_file: "test.csv"
  sample_submission_file: "sample_submission.csv"

features:
  preset: "generic"
  include:
    - "basic_impute_encode"

cv:
  strategy: "stratified"
  n_folds: 5
  seed: 42
  group_col: null
  time_col: null

model:
  name: "lgbm"
  params: {}

runtime:
  output_root: "outputs/runs"
```

### 3. `CompetitionPlugin` を作る

最初は大げさな plugin registry にせず、Python module import で十分。

```text
src/competitions/
  __init__.py
  generic_tabular.py
  playground_series_s6e6.py
  rogii.py
```

plugin の責務:

- `load_raw(cfg) -> RawData(train, test, sample_submission)`
- `build_features(cfg, raw) -> FeatureBundle`
- `make_cv(cfg, X, y) -> list[(train_idx, valid_idx)]`
- `metric(cfg, y_true, y_pred) -> float`
- `make_submission(cfg, predictions, raw, feature_meta) -> DataFrame`

共通 runner は plugin の関数を呼ぶだけにする。

### 4. `sample_submission.csv` を提出形式の正本にする

Kaggle 提出は `id_col + target` と限らない。今後の切替コストを下げるには、`sample_submission.csv` を読み、列名・列順・行数を合わせるべき。

方針:

- sample があれば必ず読み込む
- `submission.csv` は sample の列順を維持
- multiclass 確率提出、複数 target、ranking 形式は plugin が実装
- `submission_contract.json` を run artifact に保存

### 5. CV / metric を config/plugin 化する

Kaggle では CV が勝負。objective だけから自動決定すると弱い。

必要な戦略:

- `kfold`
- `stratified`
- `group`
- `stratified_group`
- `time_series`
- `fold_column`
- `custom plugin`

metric も `metric_registry` にする。

- regression: `rmse`, `rmsle`, `mae`, `mape`
- classification: `auc`, `logloss`, `f1_macro`, `accuracy`
- ordinal: `qwk`
- ranking/recsys: `mapk`
- custom: plugin

### 6. `make init` を「下書き表示」から「config 生成」へ上げる

現状の `scripts/init_competition.py` は良い入口だが、最後が手作業。

改善:

- `configs/<comp>/baseline.yaml` を生成
- `docs/competitions/<comp>.md` を生成
- `sample_submission.csv` を検出
- target / id / task_type / metric 候補を YAML に書く
- `make smoke CONFIG=configs/<comp>/baseline.yaml RUN_ID=smoke01` まで案内

### 7. データキャッシュを config hash 単位にする

現状は `data/<comp>/interim/train.parquet` なので、target/id/loader を変えても古い cache を読み得る。

推奨:

```text
data/<comp>/interim/<config_hash>/train.parquet
data/<comp>/interim/<config_hash>/test.parquet
```

または最初は `make init` / `make smoke` 時に対象 comp の interim を自動 invalidation する。

## 実装フェーズ

### Phase 1: 致命的な切替バグを潰す

- `Makefile COMP_DATA` を `CONFIG` から読むように変更する。
- `train.run()` 冒頭で `KBC_CONFIG_PATH` を設定し、`input_uri` staging も config_path 由来の raw dir に落とす。
- `logger.log_run()` に `competition` / `metric` を引数で渡せるようにし、global `config` 依存を弱める。
- `make smoke CONFIG=configs/<comp>.yaml` が `env/config.yaml` に依存しないことを検証する。

Acceptance:

```bash
make init COMP=titanic
make smoke CONFIG=configs/titanic/baseline.yaml RUN_ID=titanic_smoke
make stage-data CONFIG=configs/titanic/baseline.yaml
make train-vertex CONFIG=configs/titanic/baseline.yaml RUN_ID=titanic_vertex_smoke --smoke
```

### Phase 2: Config object 化

- `src/config.py` global constants を `ExperimentConfig` dataclass に置き換える。
- `ingest`, `featurize`, `evaluate`, `score`, `models.lgbm` に cfg を明示的に渡す。
- 旧 `env/config.yaml` は legacy `make run` 用に隔離する。

Acceptance:

- 同一 Python process 内で `configs/titanic/baseline.yaml` → `configs/playground-series-s6e6/baseline.yaml` を連続実行しても、target/metric/path が混ざらない。

### Phase 3: Generic tabular plugin

- `src/competitions/generic_tabular.py` を作る。
- `train.csv` / `test.csv` / `sample_submission.csv` 型の Playground / Getting Started コンペは plugin なしで動くようにする。
- submission を sample schema に合わせる。

Acceptance:

- Titanic / House Prices / Playground 系の smoke が config 変更だけで通る。

### Phase 4: CV / metric registry

- `cv.strategy` と `metric.name` を registry 化。
- `lower_is_better` を config に持たせ、`compare` / HPT direction / Optuna direction で使う。

Acceptance:

- regression / binary / multiclass の3種類で smoke が通る。
- `make compare` が metric direction を誤らない。

### Phase 5: コンペ別 plugin を必要時だけ追加

ROGII のように通常の `train.csv/test.csv` ではないコンペだけ plugin を追加する。

Acceptance:

- generic で済むコンペは `src/` 変更なし。
- 特殊コンペだけ `src/competitions/<slug>.py` と `configs/<slug>/baseline.yaml` を追加する。

## 優先度

| 優先 | 作業 | 理由 |
|---|---|---|
| P0 | `CONFIG` と `env/config.yaml` の二重正本を解消 | 新コンペ切替の最大バグ源 |
| P0 | `stage-data` を CONFIG 由来にする | Vertex が旧コンペ data を読む事故を防ぐ |
| P0 | sample_submission ベース提出 | Kaggle 切替で最も壊れやすい |
| P1 | CV / metric registry | ブロンズ狙いの差が出る |
| P1 | `make init` config 自動生成 | 切替速度を上げる |
| P2 | CompetitionPlugin | 特殊コンペ対応の逃げ道 |
| P2 | cache hash 化 | 実験事故防止 |

## Notes

- GCP/Terraform は全コンペ共通でよい。コンペごとに GCP リソースを分ける必要は薄い。
- BigQuery は既に `competition` カラムを持つので横断比較に向いている。
- Model Registry の display name `kaggle-<comp>` はコンペ単位で版が分かれるため妥当。
- いま必要なのは過剰な抽象化ではなく、「コンペ仕様が共通コードへ漏れない境界」を作ること。
