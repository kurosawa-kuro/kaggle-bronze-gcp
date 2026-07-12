# アーキテクチャ・設計・リファクタリング調査（2026-07-12）

- Status: Idea / implementation not started
- Review target: `4e099ce` (`main`)
- Scope: architecture, design boundaries, medium-term refactoring
- Out of scope: small bug inventory, DL/GPU/LLM/RAG, Vertex/GCP retreat

## 1. 結論

このプロジェクトは、Kaggle 表形式コンペ用の実験基盤として必要な「機能」はすでにかなり揃っている。local / Vertex 共通 runner、config 配送、GroupKFold、複数モデル、blend、Kaggle package、提出台帳、GCS/BQ/Vertex の接続を作り直す必要はない。

次のボトルネックは、機能不足ではなく **同じ run を構成するデータ・分割・前処理・モデル・GCP resource が、経路ごとに別々に再構成されること**である。特に優先すべきなのは次の4点。

1. OOF / test prediction / blend を配列位置ではなく安定した row identity で結ぶ。
2. 学習時の feature・前処理・モデルを、Kaggle package / local replay / Vertex Batch で実行可能な `InferenceBundle` にする。
3. config、コード、依存、入力、image digest、成果物 hash を持つ `run_manifest.json` を置き、同じ run_id の意味を不変にする。
4. CV split を一度だけ materialize し、trainer、metrics、fold manifest、HPO が同じ `SplitPlan` / `CvResult` を使う。

`train.py` が794行あること自体は本質ではない。問題は、その中と周辺モジュールで同じ split、config、row order、推論処理、run identity を再計算していることである。先に契約を固め、その結果として runner を薄くするのが安全である。

## 2. 調査方法と確認結果

確認対象:

- `AGENTS.md` と `docs/00_index.md`〜`docs/08_release_runbook.md`
- ADR 0001 / 0002
- `docs/tasks/idea/` と過去の完了 task
- `Makefile`, `configs/`, `env/`, `infra/terraform/`
- `src/runner/experiment`, `src/runner/model`, `src/runner/ops`
- `src/pipelines`, `src/models`, `src/features`, `src/competitions`, `src/serving`, `src/utils`
- 全テスト

実測:

| 指標 | 値 | 読み取り |
|---|---:|---|
| `train.py` | 794 lines | CLI、staging、CV、成果物、監査、推論、永続化が集中 |
| `src/**/*.py` | 5,255 lines | `train.py` が全 source の約15% |
| `yaml.safe_load` | 20 sites | config 解決が各 CLI に分散 |
| `from config import ...` 利用 module | 8 | import-time global が runner core に残る |
| GCP project/bucket 等の解決 module | 10 | control-plane 設定の重複 |
| runtime `CREATE TABLE IF NOT EXISTS` | 3 sites | Terraform 正本と application DDL が競合 |
| unit tests | 24 | 現行テストは全件成功 |

検証:

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -v tests
# Ran 24 tests ... OK
```

外部 GCP/Kaggle resource の作成・更新は行っていない。調査と本 idea 文書の追加だけを対象とした。

## 3. 維持する設計判断

以下は健全であり、今回のリファクタリングで崩さない。

| 維持するもの | 理由 |
|---|---|
| `runner.experiment.train` の local / Vertex 共通契約 | smoke から full run へ昇格しやすい |
| Makefile の1コマンド UX | 個人 Kaggle 運用の認知負荷を抑える |
| GCS = blob、BigQuery = tabular metadata | ADR 0002 と用途が一致 |
| config の base64 配送 | config 変更だけで image rebuild しなくてよい |
| CPU / LightGBM 主軸、CatBoost / XGBoost は補助 | ブロンズ目標に対して妥当 |
| 粗い KFP `train -> register` | component 間の不要な GCS 往復を避ける |
| special competition は小さい escape hatch | 巨大な CompetitionPlugin は不要 |
| Endpoint は任意・即 teardown | 常駐費用を正当化できる場合だけ使う |
| Batch Prediction は managed inference 検証用 | Kaggle 提出の主経路にはしない |

## 4. 完了済みで再提案しない項目

過去レビューから次は実装済み。新しい task として再包装しない。

- runner config の単一正本化の止血
- config 駆動 CV strategy と GroupKFold
- split / metric direction / feature の registry 最小導入
- trained mask の fold index 化
- fold score / std の永続化
- CatBoost / XGBoost の runner signature 統一
- OOF blend と fold manifest compatibility check
- `sample_submission.csv` 正本化と `submission_contract.json`
- ROGII directory loader と package-kernel 最小経路
- interim cache metadata による stale 検知
- BigQuery JOIN の `(competition, run_id)` 化
- Kaggle submissions ledger / LB sync

今回の提案は、これらを否定せず、その上で見えた次の契約不足を扱う。

## 5. 現状の構造上の圧力点

```text
configs/*.yaml
  ├─ raw dict を train.py が読む
  ├─ KBC_CONFIG_PATH 経由で config.py の import-time global に変換
  └─ 各 CLI が project/config YAML を個別に再読込
             │
             ▼
train.py (794 lines)
  ├─ data / feature / preprocess
  ├─ model trainer が split と BQ write を所有
  ├─ runner が mask / score / manifest 用に split を再生成
  ├─ artifact を既存 run directory に直接書く
  └─ GCS prefix へ逐次 upload
             │
             ▼
model/ + run artifacts
  ├─ package-kernel: LightGBM 固定の生成 script + 処理の複製
  ├─ batch-input: 現在の config/raw/code から特徴量を再生成
  ├─ serving: LightGBM の位置配列を推論
  └─ registry/batch/deploy: exact model version を固定しない経路がある
```

この結果、学習成功、Kaggle 推論成功、Vertex 推論成功、BQ 登録成功が、同一の versioned contract ではなく個別の成功条件になっている。

## 6. 優先順位

優先度は「Kaggle の評価値を誤る可能性」「再現できない高額 run を作る可能性」「変更頻度」を基準にした。

| ID | 優先度 | 提案 | 主な効果 | 規模 | 前提 |
|---|---|---|---|---|---|
| A | P0 | 安定した row identity と key-based blend | 誤った行同士の blend を防止 | S-M | なし |
| B | P0 | versioned `InferenceBundle` と共通 inference runtime | 学習 / Kaggle / Vertex の推論一致 | M | A と並行可 |
| C | P0 | immutable run manifest / image / input / artifact | run_id の再現性と完成判定 | M | local skeletonは単独可、Vertex identityはE1 |
| D | P0-P1 | `SplitPlan` / `CvResult` と fold-aware transform 境界 | CV・HPO・artifact の一致 | M-L | A の row key を利用 |
| E1 | P0-platform | `ProjectContext` / Vertex policy の共通化 | image/input identity と resource labels の統一 | S-M | C/F より先 |
| E2 | P1 | `ResolvedRunSpec` の明示渡し | ambient experiment config の縮小 | M | D と段階移行 |
| F | P1 | run attempt と GCP operation lifecycle / BQ/IaC 一本化 | 失敗・再実行・trial・非同期jobの追跡 | M-L | C, E1 |
| G | P0-S / P1 | exact Model Registry version guard / promotion | Batch / Endpoint のモデル取り違え防止 | S-M | guard は次回managed inference前、promotionはF後 |
| H | P0-doc | artifact / inference / CLI contract test と docs 同期 | 経路 drift の回帰防止 | M | 各提案と同時 |
| I | P2 | HPO space、loader、model runtime の小 registry 完成 | 次のコンペ・model 追加コスト削減 | M | E2 |
| J | P2 | package namespace / dependency / legacy 整理 | import 衝突と build drift の縮小 | M-L | 競技中の論理変更と分離 |

## 7. 提案 A: 安定した row identity と key-based blend

### 根拠

- `src/runner/experiment/train.py:538-546` の OOF `row_id` は DataFrame index。
- `src/runner/experiment/train.py:549-555` の test `row_id` は `range(len(preds))`。
- `src/runner/experiment/train.py:612-619` の fold hash は `y_train.index` の hash。
- `src/runner/experiment/train.py:558-570` の dataset snapshot は row count と schema hash だけ。
- `src/competitions/rogii.py:24` はロード後に index を reset する。
- `src/runner/ops/blend.py:61-69,132-143` は `row_id` を使わず配列位置で source run を比較・合成する。
- `src/pipelines/score.py:94-102` は sample submission の行と予測値を配列位置で対応させる。

多くの run では index が `0..N-1` なので、異なる raw 版や異なる行順でも fold hash が一致し得る。test 順が変わった run を blend すると、別 ID の予測を平均し、最初の run の submission ID に書く余地がある。

### 到達形

- 一意性を確認できた `data.id_col` を既定の `row_key` とし、複合キーには `data.row_key_cols` を許可する。
- OOF / test prediction の両方に `row_key` を保存する。
- fold manifest の validation hash は index ではなく validation row key sequence を hash する。
- blend は `row_key` で join / reorder し、重複、欠損、集合差を拒否する。
- submission 生成も prediction と sample submission を row key で joinし、単一 run と blend run を同じ alignment contract に載せる。
- `dataset_snapshot.json` に train/test の row-key set hash と sequence hash を追加する。
- ID がない場合だけ、`source_fingerprint + original_position` または raw row hash を使う。

これは全 config を cache key にする提案ではない。prediction alignment に必要な identity だけを強化する。

### 段階移行

1. 新 artifact に `row_key` を追加し、旧 `row_id` は互換用に残す。
2. 新 artifact 同士は key joinとし、legacy positional mode は既定で拒否する。必要な一時移行だけ `--allow-positional-legacy` のような明示 opt-in + warning を要求する。
3. test 行順を入れ替えた source run の再整列 / 拒否テストを追加する。
4. submission formatter にも sample ID reorder / duplicate / missing の contract test を追加する。
5. 移行期間後、legacy positional mode を削除する。

### 受入条件

- 同一 row set・異なる順序の prediction は正しい key へ再整列される。
- row の欠落、重複、余剰がある source run は blend 前に失敗する。
- sample submission の行順が prediction と異なっても、単一 run / blend run とも正しい ID に値が入る。
- fold compatibility は RangeIndex 一致ではなく row identity 一致を検証する。

## 8. 提案 B: versioned `InferenceBundle`

### 根拠

- 学習は `src/pipelines/featurize.py:34-49` で feature registry 適用後に preprocessor を fit する。
- `src/runner/experiment/train.py:684-716` は framework と model files を保存するが、実行可能な feature recipe は保存しない。
- `src/runner/ops/package_kernel.py:221-228` は raw test に feature registry を再適用せず、直接 `preprocess.json` を適用する。
- generated kernel script は `src/runner/ops/package_kernel.py:27,110-118` で LightGBM 固定。
- package 内に ROGII loader、preprocessor、submission formatting の複製がある。
- `src/runner/ops/batch_input.py:26-48` は対象 run の bundle ではなく、現在の config/raw train/code で features と preprocessor を再生成する。
- `src/serving/predictor.py:54-65` は LightGBM と位置配列を前提にする。
- `tests/test_package_kernel.py` は生成 script の compile だけを確認する。

`features: ["base"]` の間は偶然一致しやすいが、非 base FE を使うと学習時に生成した派生列が kernel 側に存在しない。FE が強くなるほど提出経路が不安定になる構造である。

### 到達形

`model/` を単なる booster 置き場ではなく、versioned inference bundle にする。

```yaml
# model/bundle.yaml v1 の概念例
schema_version: 1
framework: lgbm
input_boundary: post_loader_raw_frame
feature_recipe:
  version: 1
  names: [base]
  source_hash: "..."
  state_file: feature_state.json
feature_schema:
  names: [feature_a, feature_b]
  hash: "..."
preprocess:
  mode: shared
  file: preprocess.json
target:
  objective: regression
  class_order: null
members:
  - model_file: booster_000.txt
    seed: 42
    fold: 0
prediction:
  aggregation: mean
files:
  booster_000.txt: "sha256:..."
runtime:
  path: inference_runtime/
  hash: "sha256:..."
self_test:
  fixture: self_test_input.json
  expected: self_test_output.json
```

原則:

- data boundary は「competition loader 後、feature 適用前の名前付き raw frame」、model boundary は「feature名・順序・schema hashを持つ prepared matrix」とする。
- `raw frame -> transform_from_bundle() -> prepared matrix -> predict_prepared()` の2段階を正規経路にする。
- local replay / package-kernel は両段階を行う。batch-input は transform までを行い matrix contract と一緒に upload、現行 Vertex serving は prepared matrix の検証と predict を行う。
- raw frame の列順は名前で正規化し、順序変更だけでは予測を変えない。missing column、型不整合、prepared matrix の schema hash / order 不一致を拒否する。
- training finalize 時に、選択 feature / loader と最小 runtime の source snapshot または immutable wheel reference を bundle に固定する。後日 package する時に現在の working tree から取り直さない。
- package-kernel は巨大な raw string に処理を複製せず、最小 inference runtime と必要な feature / loader 実装を同梱する。
- Batch input は現在の train dataへ再 fitせず、指定 run の保存済み recipe / preprocessor を使う。
- 現行 feature API は train/test pair を要求するため、inference-safe recipe は `fit(train) -> state` と `transform(frame, state)`、または stateless `transform(frame)` を持つ。`stellar` の `qcut` のような処理は training bin edges を state として保存するまで packageable と宣言しない。
- 未対応 framework は generic に見せず、bundle capability check で明示的に拒否する。
- まず LightGBM を完全にし、CatBoost / XGBoost は実際に kernel/serving で必要になった時に追加する。

bundle v1 は現行挙動に合わせて top-level shared preprocess を持つ。提案 D の fold-local transform 導入後、bundle v2 で各 `member` を `model file + preprocess state + seed/fold` の組にする。v1から member別 preprocess を先取りしない。

### 段階移行

1. 現行 `manifest.json` / top-level `preprocess.json` を読める bundle v1 compatibility loader を置く。
2. `base` の feature recipe、shared preprocess、prepared matrix schema を保存する。
3. local replay と学習時 `test_pred.parquet` の一致テストを追加する。
4. batch-input を run bundle 参照へ変更する。
5. package-kernel に共通 runtime を同梱し、stateless または state保存済みの非 base FE 1件で E2E を通す。
6. serving は同じ bundle loader を使い、input width / schema version / framework を検証する。
7. 提案 D2 の後に member別 preprocess を持つ bundle v2 へ追加移行する。

### 受入条件

- 学習直後の `test_pred.parquet`、bundle local replay、生成 kernel の予測が許容誤差内で一致する。
- `base` と最低1つの inference-safe な非 base FE で一致する。
- raw input の列順変更は名前で正規化され同じ予測になり、missing/type mismatch は失敗する。
- prepared matrix の feature order / schema hash 不一致は serving 前に失敗する。
- bundle が対応しない framework を `register-servable` / package 時点で拒否できる。

## 9. 提案 C: immutable `run_manifest.json`

### 根拠

- `Makefile:18-21,47-49` と `env/project.yaml:22` は既定で可変の `:latest` image を使う。
- `requirements.txt` は下限指定のみで lockfile がない。
- `infra/Dockerfile:1,8,12` は可変 base image、`uv:latest`、未 lock dependencies を使う。
- `Makefile:63-64` は既存 GCS raw prefix へ copy する。
- `src/runner/experiment/train.py:132-164` は既存 run directory / GCS prefix の再利用を許す。
- `src/utils/artifact_store.py:29-42` は file を逐次 upload し、完成 marker や全体 checksum がない。
- `src/runner/model/register.py:66-67` は可変 GCS prefix を Registry artifact URI にする。

同じ run_id と config snapshot があっても、code、dependency、image、raw object、残存 artifact が変わり得る。`config.yaml` だけでは再現性の証明にならない。

### 到達形

run top-level に、run kind と capability を含む manifest を置く。

```json
{
  "schema_version": 1,
  "competition": "...",
  "run_id": "...",
  "attempt_id": "...",
  "run_kind": "train",
  "status": "succeeded",
  "capabilities": ["oof", "prediction", "submission", "model"],
  "parents": [],
  "resolved_config_sha256": "...",
  "git_commit": "...",
  "git_dirty": false,
  "image_uri": "...@sha256:...",
  "dependency_lock_sha256": "...",
  "input_snapshot": {"prefix": "...", "object_manifest_sha256": "..."},
  "vertex_resource": "...",
  "artifacts": {"metrics.json": "sha256:..."}
}
```

`train`, `blend`, `tune`, `hpt` は同じ file list を無理に持たせない。`run_kind` と `capabilities` を正本にし、consumer が必要 capability を検証する。

- submit は `submission` capability を要求。
- blend source は `oof` と row identity contract を要求。
- register は `model` と完成 manifest を要求。
- collect は全 artifact hash と `_SUCCESS` を検証。

### 書き込み契約

1. exact payload の正規 path は local / GCS とも `runs/<competition>/<run_id>/attempts/<attempt_id>/` とする。
2. local は一時 attempt directory に書く。
3. artifact hash を計算し、manifest を finalise する。
4. GCS は exact attempt prefix へ upload する。
5. 全 upload 後に `_SUCCESS` を最後に置く。
6. collect は一時 directory へ download / verify 後に rename する。
7. 同一 `(competition, run_id, attempt_id)` の上書きは拒否する。

consumer は `--attempt-id` を受け取る。run_id に成功 attempt が1つだけなら省略可能だが、複数ある場合は BQ で明示選択された attempt または CLI 指定を必須にする。Registry artifact URI も exact attempt の `model/` を指し、論理 run_id だけの可変 prefix を登録しない。

`resolved_config_sha256` は default と CLI/HPT override 適用後の config を指す。入力が複数 GCS object の prefix なら、各 object の name、generation、size、CRC/checksum を列挙した immutable object manifest を保存する。単一の曖昧な prefix timestamp や schema hash だけを input identity にしない。

識別できるだけでなく再取得できる必要がある。`stage-data` は `data/<competition>/snapshots/<dataset_id>/raw/` の content-addressed immutable prefix を作り、同じ dataset snapshot はrun間で再利用する。代替として bucket versioning を有効化する場合は generation指定downloadと保護 lifecycle を契約に含める。可変 `data/<competition>/raw/` の generationを記録するだけで、上書き・削除後に取得不能な設計にはしない。

再実行を禁止するのではなく、同じ論理 run の再試行を `attempt_id` で表現する。

### image / dependency

- 正規 image tag は git SHA または content hash とし、実行時は digest を記録する。
- `latest` は人間向け alias に限定する。
- `uv.lock` または同等の lock を追加する。
- base image と uv image も digest / 明示 version を固定する。
- 再現対象の Vertex/full run は原則 clean git tree を要求する。dirty local smokeを許す場合は `source_tree_sha256` と patch artifact/hash をmanifestへ残し、`git_dirty: true` だけで済ませない。

### 受入条件

- 同じ run_id を再実行しても既存成功 artifact を黙って変更しない。
- GCS upload 中断を完成 run として collect / register できない。
- manifest が指す input snapshot と source revisionを後日再取得できる。
- 任意の提出候補から、config、code revision、image digest、input version、artifact checksum を逆引きできる。

## 10. 提案 D: `SplitPlan` / `CvResult` と fold-aware transform 境界

この提案は2段階に分ける。`SplitPlan` / `CvResult` による実分割の共有は P0、fitted transform の fold 内移動は target-aware / stateful FE を追加する前の P1 とする。

### 根拠

- trainer 内で split を作る: `src/models/lgbm.py:54-57`, `catboost_.py:50-60`, `xgboost_.py:57-67`。
- runner は trained mask と fold scores のため再生成する: `src/runner/experiment/train.py:215-251,476-535`。
- fold manifest のためさらに再生成する: `src/runner/experiment/train.py:575-631`。
- Optuna は独立経路を持つ: `src/runner/experiment/tune.py:65-77`。
- feature / preprocessor は split 前に全 train で fit する: `src/runner/experiment/train.py:190-192`, `src/pipelines/featurize.py:34-46`。
- 一方 `docs/06_error_policy.md:17-32` は fitted transform を fold 内で fit する契約を記載している。

小さな実装差より、分割と学習結果の所有者が不明確なことが問題である。将来 target encoding や学習統計を使う FE を追加すると、現構造では fold leakage を避けながら推論 state を保存できない。

### 到達形

- seed ごとの `SplitPlan` を runner が一度だけ作る。
- `SplitPlan` は row-key vector を一度だけ保持し、各 fold は positional train/valid indices、count、row-key hash を持つ。全 row key を foldごとに複製しない。
- trainer は materialized splits を受け取る。
- trainer は最低限 `CvResult(oof, members, fold_scores, trained_mask)` を返す。`member` が model、seed、fold、将来の preprocess reference を持ち、`models` と二重保持しない。
- metrics、OOF、fold manifest は同じ plan/result から生成する。
- model module は framework 固有 fit loop を維持する。Trainer 基底クラスや汎用 adapter は作らない。
- tune / HPT worker は通常 train と同じ preparation / SplitPlan を使う。

transform は2種類だけに分ける。

1. stateless row feature: split 前に適用可能。
2. fitted transform: 各 fold の train 部分だけで fit し、その fold の valid/test に適用。

初期段階で汎用 sklearn Pipeline や feature graph は不要。現在の median / ordinal state を fold member ごとに保存できる最小 contract でよい。target-aware transform は実需要が出るまで実装せず、追加時にこの境界へ載せる。

### 段階移行

1. `SplitPlan` を導入し、trainer へ optional `splits` を渡す。未指定時だけ現行 fallback。
2. `CvResult` を追加し、tuple return は互換期間だけ残す。
3. train path の mask / score / manifest 再生成を削除する。
4. tune path を同じ plan/result へ移す。
5. D1（SplitPlan / CvResult）は予測・score parity を確認後、旧 helper を削除する。
6. D2として fitted preprocessing を fold member に移し、bundle v2 の member と対応付ける。
7. D2はリーク除去により予測値・CVが意図的に変わり得るため、旧score一致ではなく determinism、fold隔離、bundle replay一致を検証する。

### 受入条件

- GroupKFold の train、Optuna、artifact manifest が同じ row-key-based split を使う。
- metrics の fold score は trainer が実際に学習した validation rows から作られる。
- fitted transform は validation group / row を fit に含めない。
- bundle replay は fold member ごとの transform + model を同じ順序で平均する。
- D1は現行予測と一致し、D2は同一入力・seedで再実行可能かつ学習時test predictionとbundle replayが一致する。

## 11. 提案 E: `ProjectContext` と `ResolvedRunSpec`

この2つは優先順位を分ける。GCP resource identity と共通 execution policy を担う `ProjectContext` は提案 C/F より先の P0-platform、experiment core の global config を退役させる `ResolvedRunSpec` は提案 D と段階移行する P1 とする。

### 根拠

- `src/config.py` は import 時に YAML を読み定数化する。
- ingest、featurize、models、score、logger が import-time global を参照する。
- feature 選択は `src/pipelines/featurize.py:55-67` で config file を再読込する。
- HPT override は memory 上の config を変えるが、`src/runner/experiment/train.py:423-424` は元 config file を snapshot する。
- project / region / bucket / image の解決が Vertex submit、register、pipeline、batch、deploy 等に重複する。
- `env/project.yaml` は nested `gcp` と flat keys を両方持ち、Terraform variables にも同じ値がある。

### 到達形

大きな config framework ではなく、stdlib dataclass 程度の2つの値オブジェクトに留める。

- `ResolvedRunSpec`: data/model/cv/runtime/features/seeds と CLI/HPT override 適用後の値。
- `ProjectContext`: project/region/bucket/dataset/image/service account と共通 labels / timeout / machine / spot policy。

追加で `RunRef(competition, run_id, attempt_id)` に local path / GCS prefix の導出を集める。

原則:

- runner entrypoint で parse / defaults / validation を一度だけ行う。
- `resolved_config.yaml` を実際に使用した config として保存する。
- model params は自由度が高いため dict のままにする。
- core functions へ必要値を明示的に渡す。
- `config.py` global は legacy `make run` / notebook 互換層として段階退役する。
- Makefile の1コマンド UX は維持し、内部 planner だけを共通化する。
- `make doctor CONFIG=...` は解決済み project / bucket / dataset / image digest / input URI / output URI を一括表示する。

preflight で最低限検証するもの:

- model name と framework capability
- metric scorer の実装有無
- CV strategy / group column / fold count
- feature recipe 名
- loader と raw input の存在
- submission representation
- GCP job の project/bucket/image/service account

### 段階移行

1. resolved snapshot と preflight のみ追加する。
2. 先に GCP CLI を `ProjectContext` / common Vertex policy へ移し、image/input identity、service account、labelsを揃える。
3. featurize の target/id/features を引数化する。
4. models の objective/metric/seed を引数化する。
5. ingest の loader/path を引数化する。
6. runner core から `KBC_CONFIG_PATH` 依存が消えた後に legacy 層を縮小する。

一括全面書換えはしない。config consumer を1 moduleずつ移す。

## 12. 提案 F: run attempt / GCP operation lifecycle と BQ/IaC 一本化

### 根拠

- 各 model が trainer 内から BQ に書く: `src/models/lgbm.py:85-106`, `catboost_.py:86-95`, `xgboost_.py:98-120`。
- runner は seed child ID を渡し、複数 seed 時だけ aggregate 行も書く: `src/runner/experiment/train.py:226,284-294`。
- Vertex HPT は全 trial に同じ run_id を渡す: `src/runner/experiment/hp_tune.py:52-58`。
- `src/utils/bq.py:54-65` の基本 insert は append。
- `docs/03_domain_model.md:63-74` は多くの run state を定義するが永続状態の所有者はない。
- Terraform が管理する BQ table は experiments / cost_estimates のみ。
- submissions は `src/runner/ops/submission_ledger.py:44-65` が runtime 作成する。
- experiments schema は logger と blend にも重複する。

trainer が metric row を書いた後に artifact 生成が失敗すると、BQ には成功に見える部分行が残る。一方 BQ failure 時は完成 GCS run が台帳にない。これは BQ を正本とする ADR に対して reconciliation contract が不足している状態である。

### 到達形

BigQuery の粒度を明示する。

- `runs`: `(competition, run_id, attempt_id)` ごとに1行。`run_kind`, `status`, start/end, config/code/input identity, artifact URI。
- `run_metrics` または互換 `experiments`: aggregate / seed / trial を `metric_scope`, `seed`, `trial_id`, parent key 付きで保存。
- `operations`: Custom Job / HPT / Pipeline / Registry version / Batch / Endpoint の exact resource name、state、時刻、cost linkage。
- `submissions`: 現行を維持し、exact attempt key と manifest digest に結ぶ。

worker 内の run attempt 状態はまず `RUNNING / SUCCEEDED / FAILED` の3つで十分。本格 workflow engine は作らない。一方、非同期 GCP operation は worker 起動前にも失敗・cancel されるため、所有者を分ける。

- trainer から BQ side effect を外す。
- submitter が operation の `SUBMITTED` と exact resource name を記録する。
- worker runner が run attempt の `RUNNING -> SUCCEEDED / FAILED` と finalize を所有する。
- reconciler が Vertex remote state を読み、operation を `RUNNING / SUCCEEDED / FAILED / CANCELLED` へ収束させる。
- BigQuery は tabular metadata の canonical read model / 正本を維持する。
- GCS の成功 manifest は durable reconstruction evidence / reconciliation input とし、BQの代替正本とは呼ばない。
- `make reconcile` は manifest と remote resource state から idempotent `MERGE` を行う。
- seed / trial は artifact のない擬似 run ではなく、parent run 内の明示次元として扱う。

### IaC ownership

- BQ schema は submissions、新規 runs/operations を含め Terraform のみが所有する。
- application の runtime DDL は移行後に削除する。
- 既存 `submissions` table は runtime DDL ですでに存在するため、Terraform resource追加前に import blockで現物をstateへ取り込み、schema差分がないことをplanで確認する。その後にruntime DDLを外す。新規作成扱いでapplyしない。
- 既存 table を破壊せず、dual write -> compatibility view -> consumer 切替の順に移行する。
- `bqDataset` は全 module で `ProjectContext` から取得し、hard-coded dataset を残さない。

### 受入条件

- 成功、失敗、再試行、HPT trial を一意に区別できる。
- BQ write が失敗しても完成 manifest から再同期できる。
- `cost-record` / submit / reconcile の再実行で重複行を増やさない。
- `compare` の1行が、どの attempt / artifact / Vertex job かを逆引きできる。

## 13. 提案 G: exact Model Registry version guard と promotion

優先度を分ける。`Model.list()[0]` を廃止する exact version guard と servable capability check は、次回 Batch / Endpoint 実行前の P0-S（safety）。alias / promotion 台帳は提案 F 後の P1 とする。

### 根拠

- `src/runner/model/register.py:69-87` は registry-only と servable を同じ display name / `latest` alias に積む。
- registry-only version にも placeholder serving image を設定する。
- `src/runner/model/batch_predict.py:57,80-95` と `deploy.py:111-117` は display name 検索結果から model を選べる。
- register の exact model resource/version は run artifact / BQ に保存されない。

### 到達形

- 登録後の exact `projects/.../models/...@version` は BQ `operations` または sealed run payload 外の immutable operation sidecar に保存する。完成済み attempt へ `model_ref.json` を後書きしない。
- model version に `registry_only` / `servable` capability、bundle hash、serving image digest を記録する。
- Batch / Endpoint は `--model-run-id` または exact `--model-version` を要求する。
- API上 placeholder serving image が必要な registry-only version は lineage-only として隔離し、Batch / Endpoint consumer が選択できないよう capability gate を必須にする。
- alias は `candidate`, `servable`, `champion` 等、目的別にする。
- alias 更新は `make promote-model RUN_ID=... ALIAS=...` の明示操作だけにする。
- KFP は粗い `train -> register` のまま維持する。

これは Endpoint 常用の提案ではない。任意の managed inference を使う時に、対象 model を確定させる境界である。

## 14. 提案 H: contract test と docs 同期

### 現在の不足

24 tests は既存の重要な回帰を守っているが、複数経路を同一 run contract として検証していない。

- package test は compile のみ。
- 3 model の artifact schema / replay parity test がない。
- current config から作る batch input と saved run の一致を検証しない。
- CLI dry-run plan の project/image/service-account/labels 一致を検証しない。
- BQ Terraform schema と runtime schema の一致を検証しない。

また、正本 docs に実装 drift がある。

- `docs/04_workflows.md:40` と `docs/05_data_model.md:72` は runner を LGBM-only と記載。
- `docs/04_workflows.md:14-20` と `docs/08_release_runbook.md:50-58` は `make init` 後に legacy `env/config.yaml` を手編集・copy する手順を記載。
- `docs/04_workflows.md:42-48` と `docs/07_test_strategy.md:49-51` は FE / model 切替に legacy path を案内。
- `docs/04_workflows.md:288` は ROGII package adapter 未対応と記載するがコードは対応済み。
- `docs/03_domain_model.md` の run state は実装上の persisted state ではない。

これは個々の誤記より、変更時に capability docs と contract tests が同時更新されない構造が問題である。

docs は次のように所有範囲を分ける。

- `docs/00_index.md` または `docs/02_architecture.md` に、command × run kind × model × `core / optional / legacy` の support matrix を1つだけ置く。
- README / requirements / workflows は同じ support matrix へリンクし、対応状況を重複記載しない。
- 実機 resource ID と日付付き E2E 結果は1つの case study または done taskへ集約する。
- ADR は安定した判断理由を保持し、変化する「実装済み一覧」は support matrix に任せる。
- 後続 refactor の前に現行 support matrix と stale な path / command を修正する。

### 最小 contract matrix

| Contract | Fast test | GCP E2E |
|---|---|---|
| row identity / blend | row reorder、欠落、重複 | 不要 |
| SplitPlan | GroupKFold train/tune 同一 hash | 不要 |
| inference bundle | train prediction = local replay = kernel | serving変更時のみ Batch |
| framework | 3 model の OOF shape / save / load | 提出候補 framework のみ |
| artifact manifest | file hash / capability / incomplete marker | collect / register 変更時 |
| config | 全 `configs/*.yaml` preflight | Vertex dry-run |
| GCP plan | Vertex/HPT/Pipeline/Register/Batch dry-run snapshot | resource API変更時1回 |
| BQ schema | Terraform contract / query generation | migration時のみ |

`make check` の候補:

```text
unit tests
+ all config preflight
+ artifact/inference contract tests
+ GCP CLI dry-run contract tests
+ docs link / stale command check
```

外部課金 E2E を毎回行う必要はない。GCP boundary を変更した時だけ、既存 runbook に沿って Custom Job / collect / BQ / Batch の該当範囲を実機確認する。

## 15. P2候補

### 15.1 HPO search space の単一 spec

`src/runner/experiment/tune.py:24-33` と `hp_tune.py:88-96` に同じ LightGBM space が二重定義されている。小さな declarative spec を config または1 module に置き、Optuna / Vizier へ変換する。

```yaml
tuning:
  space:
    learning_rate: {type: float, min: 0.01, max: 0.2, scale: log}
    num_leaves: {type: int, min: 31, max: 512}
```

対応型は float / int / categorical に限定し、汎用 HPO framework は作らない。HPT trial identity は提案 F に従う。

### 15.2 loader を1責務の明示 registry にする

`src/pipelines/ingest.py:16-36` は ROGII 名 / directory sniff と California Housing fallback を共通 path に持つ。次の程度で十分。

```yaml
data:
  loader: generic_csv  # generic_csv | rogii | california_demo
```

- `src/competitions/__init__.py` の小さな dict で load train/test だけを dispatch。
- production config で raw がない場合は fail closed。
- package は同じ loader 実装を同梱。
- CV、metric、features、submission まで含む巨大 CompetitionPlugin は作らない。

### 15.3 objective と submission representation を分離する

`src/pipelines/score.py:124-130` は multiclass を argmax label へ変換する一方、sample に複数 probability 列がある形式も存在し得る。sample shape から一意なら推論し、曖昧な場合だけ次を追加する。

```yaml
submission:
  mode: label  # label | probability
```

bundle / submission contract には representation と class order を保存する。次の該当コンペで P0 に繰り上げる。

### 15.4 model runtime registry の完成

`src/models/__init__.py` は空で、trainer dispatch、predict、save filename、importance が `train.py` の分岐に残る。基底クラスや Protocol ではなく、model module の小さな関数 table で `train_cv`, `predict_one`, `save_model`, `importance` を取得する。LightGBM 主軸なので第四 model または CatBoost/XGBoost kernel が必要になるまで P2。

### 15.5 package namespace と依存 layer

トップレベル名 `utils`, `models`, `pipelines`, `config` は外部 CLI と衝突し、Makefile / subprocess が `PYTHONPATH` を scrub する必要がある。競技中の論理変更とは分離した機械的 change として、次を検討する。

- `pyproject.toml` と一意な package root（例: `kaggle_bronze`）
- editable install / wheel による import、`PYTHONPATH=src` の退役
- core training、local control plane、serving の dependency group 分離
- `make run`, `env/config.yaml`, `submit-legacy` の deprecation -> removal

この移動は churn が大きい。提案 A〜H と同じ変更で実施しない。

### 15.6 GCP cost / lifecycle / IAM

ADR 0002 を維持しつつ、platform hardening として後続で行う。

- Billing Export -> BigQuery を actual cost の正本、現 estimator を速報値にする。
- labels / resource metadata が得られる範囲で actual cost を run / operation に帰属し、残りは project / service 単位で表示する。全 SKU を exact resource name に割り当てられるとは仮定しない。
- GCS prefix 別 lifecycle、Artifact Registry cleanup、public access preventionを追加する。
- cleanup は active Registry version の artifact URI、提出済み / promoted run、manifest が参照する image digest を保護し、再現性を後から壊さない。
- IAM は実利用ログを見て bucket/dataset scope へ縮小する。
- remote Terraform state は共同運用 / CI が始まるまで急がない。

## 16. 推奨実装順

大きな一括リファクタリングにせず、観察可能な contract 単位に分ける。

### Phase 0: 競技経路の安全化

1. row key を OOF / test prediction / fold manifest に追加。
2. blend を key join 化。
3. `SplitPlan` を materialize し、train artifact と同じ split を使う。
4. package inference recipe v1 を保存し、`base` + inference-safe な非 base FE の parity test を追加。
5. 次回 Batch / Endpoint 前に exact model version guard と servable capability check を入れる。

### Phase 1: run の不変性

6. `ProjectContext` / common Vertex policy で image/input identity、service account、labelsを揃える。
7. exact attempt path と `run_manifest.json`、run kind / capability / artifact hashes を追加。
8. immutable image tag、dependency lock、content-addressed input snapshot / object manifest を記録。
9. `_SUCCESS` / verified collect / no silent overwrite を追加。

### Phase 2: core の明示化

10. `ResolvedRunSpec` と preflight / resolved config snapshot を追加。
11. `CvResult` へ移行し、mask / fold score / manifest の再生成を削除。
12. fitted transform を fold member と bundle に接続。
13. 結果として `train.py` を CLI/lifecycle、execution、artifact writer へ分ける。

### Phase 3: control plane

14. 既存 submissions をTerraform stateへimportしてから、runs / operations / submissions schemaをTerraform管理へ移す。
15. submitter / worker / reconciler の state ownership、dual write、compatibility view、`make reconcile` を追加。
16. trainer 内 BQ logging を runner finalize へ移す。
17. Model Registry alias / promotion 台帳を追加。

### Phase 4: 後続整理

18. HPO search space spec、loader registry、submission representation を必要順に実装。
19. package namespace / dependency layer / legacy removal は競技ロジックと別変更で実施。
20. Billing reconciliation、保護条件付き GCS/AR lifecycle、IAM hardening を行う。

## 17. 最初に切る task 案

### Task 1: prediction row identity contract

Scope:

- `row_key` の導出
- OOF / test artifact への保存
- fold hash の row-key 化
- blend key join
- sample submission への key join
- migration compatibility

Acceptance:

- reorder / duplicate / missing row の contract tests が通る。
- sample と prediction の行順が違ってもIDと予測が一致する。
- 現行 source run の blend score が変わらない。

### Task 2: inference recipe v1

Scope:

- bundle v1 / shared preprocess / feature recipe state / prepared matrix schema
- saved preprocessor からの local replay
- package runtime の共通化
- batch-input の run bundle 参照

Acceptance:

- train = local replay = generated kernel の prediction parity。
- `base` と inference-safe な非 base FE で確認。
- raw列順は正規化し、missing/type mismatch と prepared matrix schema mismatch は拒否する。

### Task 3: SplitPlan / CvResult

Scope:

- split 一回 materialize
- trainer optional splits
- fold scores / mask / manifest を result から生成
- tune path の共通化
- D2で fold-local preprocess と bundle v2 member を接続

Acceptance:

- GroupKFold の train / tune / manifest split hash が一致。
- D1で3 modelの予測・artifact contractが維持される。
- D2でfold隔離、determinism、学習時predictionとbundle replay一致を確認する。

### Task 4: immutable run manifest

Scope:

- run kind / capability / parent / status
- exact attempt path と resolved config/code/image/input object/artifact identity
- `_SUCCESS` と verified collect

Acceptance:

- incomplete / modified artifact を collect / register できない。
- 同一成功 attempt を上書きできない。
- Registry と submission が exact attempt / manifest digest を参照する。

この4 task が終わってから、config object 化やファイル分割を行う。先に `train.py` を機械的に複数ファイルへ移しても、契約の重複は残る。

## 18. やらないこと

- Vertex/GCP を撤回して local-only に戻す。
- KFP を ingest / featurize / train / score に細分化する。
- Vertex Experiments / ML Metadata を BQ の代わりの正本にする。
- Feature Store、MLflow server、Ray、Spark、Composer、GKE を追加する。
- Endpoint を常駐させる。
- Batch Prediction を Kaggle submission の正規経路にする。
- 全責務 CompetitionPlugin、DI container、Port/Adapter 階層、Trainer 基底クラスを作る。
- 全 config / 全 data を使った重い cache framework を作る。
- CatBoost / XGBoost の kernel/serving 対応を、実需要より先に一般化する。
- package namespace 移動と学習ロジック変更を同じ差分で行う。

## 19. 判断

このプロジェクトの次の成長点は「より多くの GCP 製品」でも「より深い抽象化」でもない。既にある local / Vertex / Kaggle / BQ / GCS の各経路を、versioned data identity、split identity、inference bundle、run manifest で同じ run に結び直すことである。

特に、row-key-based blend と executable inference recipe は Kaggle のスコアそのものを守る。immutable provenance と run lifecycle は、高価な Vertex run を再利用可能な資産に変える。`ResolvedRunSpec` や runner 分割は、その契約を導入した後の結果として行うのが妥当である。
