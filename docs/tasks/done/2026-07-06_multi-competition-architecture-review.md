# 複数コンペ切替アーキテクチャ再評価（2026-07-06）

> 依頼: 他 AI エージェントによるアーキテクチャ調査（旧 `backlog/2026-07-06_multi_competition_architecture.md`。本レビューに統合済みのため削除、原文は git 履歴にあり）と、[idea/2026-07-06_bronze-strategy-review.md](../idea/2026-07-06_bronze-strategy-review.md)（前回レビュー）を鵜呑みにせず、コードを読み直して再評価したもの。
> 主眼: ROGII 単発対応ではなく、**ブロンズ取得まで複数コンペを渡り歩ける低切替コスト基盤**にするためのリファクタリング。
> 本文の主張はすべて 2026-07-06 時点のコードで実際に確認済み（セクション4に根拠）。

---

## 1. 結論

> 2026-07-07 更新: 本レビューから切り出した実装 task [done/2026-07-07_multi-competition-switching-hardening.md](../done/2026-07-07_multi-competition-switching-hardening.md) は完了済み。P0-D、feature registry の最小導入、BigQuery JOIN 固定、interim cache stale 検知、`submission_contract.json` 永続化は実装・テスト済み。

**「config 駆動」は半分だけ本物である。** ローカル経路（smoke / train-local）は渡した config が正本として機能するが、**Vertex 経路では import 順序バグにより、イメージにベイクされた `env/config.yaml` が target / objective / metric / データパスの正本になり、`--config-b64` で渡した新コンペの data セクションは実質無視される**。`full_gcp_lgbm_001` が成功したのは、ベイクされた env/config.yaml と渡した config が同一コンペだったからにすぎない。

つまり現状のコンペ切替の実手順は「env/config.yaml を書き換えて **docker イメージを再ビルド**」であり、これはどこにも文書化されておらず、vertex_run.py のコメント（「config をイメージにベイクせず引数で渡す＝再ビルド不要」）と真逆である。切替コストが高い最大の原因は FE でも CV でもなく、**この二重正本と import-time global** にある。

方向性は「大きな MLOps 化」ではなく次の3手:

1. **止血（1日）**: `train.run()` 冒頭で `KBC_CONFIG_PATH` を設定し、`stage-data` を CONFIG 由来にする。これだけで「渡した config が常に正本」になる
2. **registry 化（各1日）**: CV / metric / FE / model を config から引ける辞書にし、metric 方向の3重複実装を1箇所に潰す
3. **提出形式の正本化（1日）**: `sample_submission.csv` を読んで列名・列順・形式を合わせる

CompetitionPlugin の全面導入や config オブジェクトの一括書換えは不要。generic な表形式コンペは「config 1枚 + `make init`」で済み、ROGII のような特殊コンペだけ小さな escape hatch を足す。

## 2. 前回レビューへの評価

### 2-1. 前回レビュー（bronze-strategy-review、私自身のもの）

**採用すべき点**: P0-0（ルール確認）/ P0-2（package-kernel + 前処理永続化）/ P0-3（提出台帳）/ blend の fold hash アサートは、本再調査でも有効。変更不要。

**甘かった点（認める）**:

- **二重 config 正本と Vertex の config 無視バグを見逃した**。「同一 runner の local/Vertex 二重実行契約 ◎」と評価したが、実際には data セクションに関して契約は Vertex 側で破れている。コンペを切り替えた瞬間に顕在化する時限バグで、ROGII 参戦の前提を壊す。
- **P0-1（CV config 駆動化）の実装コストを「小」と過小評価**。models/*.py が global config を import する構造のまま `cv.strategy` を足すと、train.py 経路は直っても catboost_.py の独自 `_splits`（重複実装）が残り、P0-4 で再手術になる。
- **P0-4 の前提が誤り**。catboost_.py の docstring「lgbm.py と同じシグネチャ」は嘘で、実際は `n_folds/seed/max_folds/log_run_id` を受けない。統合コストは見積もりより大きい。

**修正すべき点**: P0-1 と P0-4 は、下記 P0-A（config 単一正本化）と splits 一本化を前提に置き直す。

### 2-2. backlog の調査（他 AI エージェントによる architecture 調査）

**採用すべき点（検証の結果、事実認定はほぼ全部正確）**: config.py の import-time 定数、train.py の staging 順序バグ、Makefile `COMP_DATA`、sample_submission 不使用、ingest の train.csv 固定、metric 3種、init の下書き止まり — すべてコードで確認できた。「問題は GCP ではなくコンペ仕様が共通パイプラインに漏れていること」という診断も正しい。

**甘い点・過剰な点**:

- **CompetitionPlugin の5責務（load_raw / build_features / make_cv / metric / make_submission）全面プラグイン化は過剰**。CV と metric は config + registry で表現でき、plugin に逃がすとコンペごとに Python を書く方向へ誘導されて切替コストがむしろ上がる。plugin は「loader と submission 形式」だけの escape hatch に絞るべき。
- **Phase 2（config オブジェクト全面化）が 1〜2 日粒度に割れていない**。ROGII 締切（entry 7/29）と突き合わせると、Phase 1 の止血だけ先行させ、オブジェクト化は P1 で段階移行にすべき。
- **cache の config_hash 化は過剰**（本人も代替案を書いている通り）。`make init` 時の interim 自動削除 + ingest 側の schema hash 照合で足りる。
- **YAML 変数展開（`${competition.slug}`）は実装コスト増**。パスは comp から関数導出で済んでいる。
- **見えていない穴が2つ**: (a) BQ の experiments×cost_estimates JOIN が `run_id` のみで結合しており、コンペを跨いで run_id が衝突すると誤 JOIN する（sweep は config stem を run_id にするので衝突は現実に起きる）。(b) metric 方向（maximize/minimize）が tune.py / hp_tune.py / compare.py の3箇所に別実装されており、metric を足すたび3箇所直す必要がある。

## 3. コンペ切替コストが高い原因（構造）

1. **正本が3つある**: `env/config.yaml`（global 定数の既定）/ `configs/*.yaml`（runner 用）/ `src/config.py` の import-time 定数。しかもどれが効くかが「経路 ×import 順序」で変わる
2. **import-time global**: pipelines / models が `from config import TARGET, METRIC...` する構造は、プロセス内で config を切り替えられず、import 順に敏感（Vertex バグの根源）
3. **コンペ仕様の漏れ**: 提出形式（ID+target 決め打ち）、multiclass=argmax 固定、metric 方向、CV 分割、FE 配線が共通コードに埋まっている
4. **解消済み: init が半自動**: `make init` は runner 用 `configs/<comp>_baseline.yaml` を生成し、`make smoke` / `make train-local` の現行経路を案内する
5. **重複実装**: CV 分割（lgbm/catboost）、metric 方向（3箇所）、成果物ログ（train.py と各 model の `_log`）

## 4. コード上の根拠

| # | ファイル:箇所 | 内容 | なぜ問題か |
|---|---|---|---|
| 1 | `src/config.py:7-8` | module import 時に `KBC_CONFIG_PATH` または `env/config.yaml` を読み、`COMP/TARGET/METRIC/OBJECTIVE/DATA_RAW` を確定 | 一度 import されるとプロセス内で変更不能。以後の全 import はキャッシュ値を読む |
| 2 | `src/runner/experiment/train.py:140-145` vs `:168` | `--input-uri` staging で `from config import DATA_RAW`（140-145）が、`os.environ["KBC_CONFIG_PATH"]=...`（`_train_lgbm` 冒頭 168）より**先に**実行される | **Vertex 経路の致命バグ**。config module が env/config.yaml で確定・キャッシュされ、ingest.py:8 / featurize.py:7 / evaluate.py:6 / lgbm.py:9 の `from config import ...` が全部ベイク値を読む。渡した config の target/objective/metric は無視される。新コンペでは target 列不在の KeyError（良くて）、列名が偶然一致すれば誤った目的関数で silent mis-train（最悪） |
| 3 | `infra/Dockerfile:14` | `COPY env ./env` で env/config.yaml をイメージにベイク | #2 と合わさり「コンペ切替＝イメージ再ビルド」が実際の運用になるが未文書化。`vertex_run.py:76` のコメント（再ビルド不要）と矛盾 |
| 4 | `Makefile` `COMP_DATA` 定義 | `env/config.yaml` の comp を読む | `make stage-data CONFIG=configs/new.yaml` が旧コンペの raw を GCS へ上げる。#2 と合わせ「パスは新コンペ・中身は旧コンペ」の混線が可能 |
| 5 | `src/pipelines/score.py` / `src/runner/experiment/train.py` / `src/runner/ops/blend.py` / `src/runner/ops/package_kernel.py` | ✅ 2026-07-07 解消済み。提出生成は `sample_submission.csv` を正本にし、`submission_contract.json` を保存する | 確率提出・複数列・列順指定のコンペで提出形式ミスを防ぐ |
| 6 | `src/pipelines/featurize.py:11,35` | `LABEL_CLASSES` が module global の可変状態。`score.py:26` が読む | プロセス内の暗黙結合。FE 差し替えも「run.py の import を手編集」が正規手順（docstring）で、config から選べない |
| 7 | `src/pipelines/ingest.py` / `src/competitions/rogii.py` | ✅ 2026-07-07 部分解消済み。ROGII directory adapter と interim metadata stale 検知を実装済み | loader 変更時に別コンペ cache を黙って再利用しない。特殊 loader は `src/competitions/` escape hatch に限定 |
| 8 | `src/pipelines/evaluate.py` | ✅ 2026-07-07 解消済み。metric registry と direction-only metric を追加 | metric 追加時の方向判定漏れを防ぎ、scorer 未実装 metric は明示エラー |
| 9 | `src/pipelines/evaluate.py` / `src/runner/experiment/tune.py` / `src/runner/experiment/hp_tune.py` / `src/runner/ops/compare.py` / `src/runner/ops/blend.py` | ✅ 2026-07-07 解消済み。metric 関数と maximize/minimize 判定を `evaluate.py` の registry に一元化し、Optuna / Vertex HPT / compare / blend が参照する | metric 追加時の修正点を registry 1箇所に縮小し、HPO 逆最適化と比較順序ミスを防止 |
| 10 | `src/pipelines/splits.py` / `src/models/lgbm.py` / `src/models/catboost_.py` / `src/models/xgboost_.py` | ✅ 2026-07-07 解消済み。CV 分割は `pipelines.splits.make_splits` に一本化 | cv.strategy 追加時にモデルごとの重複修正を避ける |
| 11 | `src/models/catboost_.py` / `src/models/xgboost_.py` | ✅ 2026-07-07 解消済み。runner signature を LGBM と統一 | P0-4 のマルチモデル統合と Vertex 実行契約に接続済み |
| 12 | `src/ports.py` | ✅ 2026-07-07 解消済み。importer ゼロかつ dead spec のため削除 | 実契約は trainer signature / feature registry / tests を正とし、未使用 Protocol による誤誘導を排除 |
| 13 | `scripts/init_competition.py` | ✅ 2026-07-07 解消済み。runner 用 `configs/<comp>_baseline.yaml` を生成し、現行 `make smoke` / `make train-local` を案内する | 新コンペ初日の手作業とミスを削減 |
| 14 | `src/runner/ops/compare.py` | ✅ 2026-07-07 解消済み。experiments / cost_estimates / submissions は `(competition, run_id)` で JOIN | コンペ跨ぎの同名 run_id で比較・費用・提出履歴が混ざらない |
| 15 | `src/serving/predictor.py` | P0-2 で `model/preprocess.json` 永続化は完了。serving predictor の生配列前提は Endpoint/Batch 用の将来整理対象 | Kaggle ブロンズ主経路は package kernel / batch input で前処理を再現するため、常駐 Endpoint 優先度は低い |

**健全な部分（変えない）**: GCS `runs/<comp>/<run_id>` と `data/<comp>/raw` の名前空間、BQ の competition 列、Model Registry `kaggle-<comp>`、run_id 成果物契約、Makefile UX、Terraform。複数コンペ横断で破綻しない設計が既にできている。

## 5. リファクタリング方針

- **止血と構造移行を分ける**。Vertex バグは1行級の修正で殺せる（`train.run()` の先頭、staging より前に `os.environ["KBC_CONFIG_PATH"] = str(config_path)` を置く。config.py:14 以降は nested schema も読めるので configs/*.yaml がそのまま正本になる）。構造移行（cfg 明示渡し）はその後に段階実施
- **registry は「dict + config キー」で最小に**。class 階層や plugin 基盤は作らない。CV / metric（+ lower_is_better）/ FE / model の4つ
- **`env/config.yaml` は退役方向**。runner 経路の正本は configs/*.yaml に一本化し、env/config.yaml は legacy `make run`・notebooks 専用と明記（最終的に削除）
- **コンペ固有物の置き場を1箇所に**: `configs/<comp>/` と（必要時のみ）`src/competitions/<comp>.py`（loader / submission 形式のみ）。src/ 共通コードにコンペ名が現れたら負け、を規約にする
- **既存契約は追加のみ**: run_id 成果物・BQ スキーマ・Makefile ターゲット名は変えず、preprocess.json / submission_contract.json 等を足す

## 6. 優先順位付き改善案

- **P0-A: config 単一正本化の止血**（新規・最優先。既存 P0-1 の前に差し込む）
- **P0-B: CV strategy registry + 分割ロジック一本化**（既存 P0-1 を拡張: lgbm/catboost の `_splits` 重複を `pipelines/splits.py` に統合してから config 駆動化）
- **P0-C: metric registry + 方向の一元化**（✅ 2026-07-07 実装済み。`evaluate.py` の registry を Optuna / Vertex HPT / compare / blend が参照）
- **P0-D: sample_submission 正本化 + submission_contract.json**（✅ 2026-07-07 実装済み。`score.py` 共通 adapter、train/blend/package_kernel 対応、contract 永続化）
- 既存 P0-0（ルール確認）/ P0-2（package-kernel）/ P0-3（提出台帳）/ P0-4（マルチモデル+blend）は維持。ただし P0-4 は catboost シグネチャ統一を含むためコスト再見積もり（2〜3日）
- **P1**: init の `configs/<comp>_baseline.yaml` 自動生成（✅）/ FE registry（✅ 最小導入）/ BQ JOIN に competition 追加（✅）/ interim cache の stale 検知（✅）/ cfg 明示渡しへの段階移行（LABEL_CLASSES 排除を含む、未実施）
- **P2**: `src/competitions/` escape hatch（ROGII の loader が特殊と判明した時だけ）/ ports.py 削除（✅）/ run.py・notebooks の legacy 退役 / init_competition の `conf/` 表記修正
- **やらない**: 5責務フル CompetitionPlugin / YAML 変数展開 / cache config_hash 化 / ExperimentConfig 一括全面書換え / （従来どおり）Endpoint 常駐・Monitoring・Feature Store・KFP 細分化・分散 Optuna

## 7. 改善案ごとの表

| 改善案 | 狙い | 切替コスト効果 | ブロンズ効果 | 変更対象 | 実装コスト | 破綻条件 | 検証方法 |
|---|---|---|---|---|---|---|---|
| P0-A config 止血 | Vertex でも「渡した config が正本」を成立させる | **最大**。切替＝イメージ再ビルドを撲滅 | **大**（ROGII の Vertex 実験が正しく回る前提） | `train.py`（run() 冒頭で KBC_CONFIG_PATH 設定）、`Makefile`（COMP_DATA を CONFIG 由来に）、`utils/logger.py`（competition/metric を引数化） | 1日 | env/config.yaml 依存の legacy 経路（run.py/notebooks）を巻き込むと肥大 → runner 経路のみに限定 | 別コンペ config（titanic 等）で `--dry-run`＋smoke を Vertex イメージ内相当（KBC 未設定状態）で実行し、metrics.json の competition/metric が config 側と一致 |
| P0-B CV registry | `cv.strategy`+`group_col` を config 化し、分割実装を1本化 | 大（新コンペ＝config 1行） | **最大**（ROGII の GroupKFold。前回 P0-1 と同じ） | 新 `pipelines/splits.py`、`lgbm.py`/`catboost_.py`/`xgboost_.py`（_splits 削除）、`train.py`（fold_manifest） | 1〜2日 | 既定挙動の非互換 → strategy 未指定時の fold_manifest ハッシュ一致で担保 | `make smoke`（既存 config でハッシュ不変）+ group config で overlap=0 |
| P0-C metric registry | ✅ 2026-07-07 実装済み。metric 関数と higher_is_better を `evaluate.py` に集約し、tune/hp_tune/compare/blend が参照 | 大（metric 追加＝registry 1エントリ） | **大**（HPO 逆最適化の芽を摘む + ROGII 指標対応） | `evaluate.py`、`tune.py`、`hp_tune.py`、`compare.py`、`blend.py`、`tests/test_metrics.py` | 完了 | direction-only metric は scorer 未実装時に明示エラー | `tests/test_metrics.py` と既存 unittest で registry 方向・CV scorer・compare SQL を検証 |
| P0-D sample_submission 正本化 | ✅ 2026-07-07 実装済み。提出列名・列順・形式を sample から決め、`submission_contract.json` を残す | 大（提出形式差異を吸収） | **大**（提出形式ミス＝スコア0の防止） | `score.py`、`train.py`、`blend.py`、`package_kernel.py`、`tests/test_submission_contract.py` | 完了 | sample が無いコンペ → 現行 ID+TARGET へフォールバック | 生成 submission の列名・列順・行数が sample と一致するアサート |
| P1 init 強化 | ✅ 2026-07-07 実装済み。`make init` が runner 用 `configs/<comp>_baseline.yaml` と doc を生成し、次コマンドまで案内 | 大（切替の手作業をほぼ0に） | 中（48h 初動の速度） | `scripts/init_competition.py` | 完了 | 自動推定の誤り → 生成 YAML に `REPLACE_ME` を残し人間確認を強制 | 生成 config に `features: ["base"]` を含める |
| P1 FE registry | ✅ 2026-07-07 最小導入済み。`features: [base, ...]` で FE を宣言選択 | 大（src/ 共通コードを触らず FE 追加） | 大（sweep の弾） | `featurize.py`、`features/__init__.py`、`tests/test_features_registry.py` | 最小版完了 | encode 前/後の規約曖昧 → 「raw df を受ける」を規約化 | registry の base/unknown feature test |
| P1 BQ JOIN 修正 | ✅ 2026-07-07 検証・固定済み。`(competition, run_id)` で JOIN | 中（複数コンペ蓄積後の台帳信頼性） | 小〜中（誤った比較で判断を誤るのを防ぐ） | `compare.py:_sql`、`tests/test_submission_contract.py` | 完了 | cost_estimates に competition が無い場合 → 列追加 or run_id に comp を含める規約 | SQL に competition join が入ることをテスト |
| P1 cache 無効化 | ✅ 2026-07-07 stale 検知を実装済み。interim metadata 不一致で停止 | 中（stale cache 事故防止） | 小 | `ingest.py`、`tests/test_ingest_cache.py` | 完了 | legacy cache は metadata 無しなら警告して使用 | interim metadata mismatch test |
| P2 competitions/ escape hatch | ✅ 2026-07-07 方針確定済み。特殊 loader/提出形式だけコンペ別 module。ROGII adapter は既存 `src/competitions/rogii.py` を使用 | 中（特殊コンペ対応の逃げ道） | ROGII 次第 | `src/competitions/` | 方針完了 | generic で済むのに adapter を書き始める → 「configs で表現できない時のみ」を規約化 | generic コンペで src/ 無変更が保たれること |

## 8. 理想のアーキテクチャ案

- **competition profile** = 現行では `configs/<comp>_baseline.yaml` の `data:` セクション。`make init` が生成し、人間が target/metric を確認して確定。Python の profile クラスは作らない
- **config schema**（現行スキーマとの互換を保ち、既存キーは温存）:

```yaml
competition:            # (現 data: を改名。旧キーも当面読める互換層を残す)
  slug: "rogii-wellbore-geology-prediction"
  target: "..."
  id_col: "..."
  task_type: "regression"        # (現 objective)
  metric: "..."                  # metric registry のキー
  submission: "sample"           # sample_submission 正本 / "id_target" フォールバック
  loader: "generic_csv"          # 特殊コンペのみ "competitions.rogii"
features: ["base"]               # FE registry のキー列
cv:
  strategy: "group"              # kfold / stratified / group /（将来 time / fold_column）
  group_col: "well_id"
  n_folds: 5
  seed: 42
seeds: [42, 777, 2026]
model: {name: "lgbm", params: {...}}
runtime: {...}                   # 現行のまま
```

- **CV strategy registry** = `src/pipelines/splits.py` の `CV_STRATEGIES: dict[str, callable]`。lgbm/catboost/xgboost は自前 `_splits` を捨ててこれを呼ぶ
- **metric registry** = ✅ 実装済み。`src/pipelines/evaluate.py` の `METRICS: dict[str, MetricSpec]`（scorer + higher_is_better）。tune / hp_tune / compare / blend の方向判定はすべてここを参照
- **feature registry** = `src/features/__init__.py` の `FEATURE_REGISTRY: dict[str, fn]`。規約:「encode 前の raw df を受け、copy を返す」
- **model registry** = `src/models/__init__.py` の `TRAINERS: dict[str, train_cv]`。全 trainer を lgbm.py の拡張シグネチャ（n_folds/seed/max_folds/num_boost_round/early_stopping_rounds/log_run_id）に統一
- **submission adapter** = `score.make_submission(cfg, preds, raw)` が sample_submission の列順で書き、`submission_contract.json`（列名・行数・形式・sample の sha256）を成果物に残す
- **notebook packaging adapter** = P0-2 の package_kernel ops。model registry 対応後は manifest.json の `framework` で booster ロードを分岐（LGBM→CatBoost/XGB 拡張）
- **artifact contract**（追加のみ）: 既存（config.yaml / metrics.json / oof / test_pred / fold_manifest / dataset_snapshot / leakage_audit / feature_importance / model/ / submission.csv）+ `model/preprocess.json`（P0-2）+ `submission_contract.json`（P0-D）+ `adversarial_audit.json`（P1）
- **BigQuery schema**: `experiments`（+`status`、params 内に features/cv_strategy が入る）/ `cost_estimates`（現行）/ `submissions`（P0-3）。**JOIN キーは全テーブル `(competition, run_id)` に統一**

## 9. 最初に実装すべき active task 案

**P0-A「config 単一正本化の止血」を新規 active task とし、既存の実装順を P0-0 → P0-A → P0-1(=P0-B) → P0-C → P0-2 → P0-3 → P0-D → P0-4 に組み替える。**

P0-A の中身（1日粒度）:

1. `train.py:run()` の先頭（`--input-uri` staging より前）で `os.environ["KBC_CONFIG_PATH"] = str(config_path)` を設定（`_train_lgbm` 内の設定は残してよい）
2. `Makefile` の `COMP_DATA` を `CONFIG` の comp から読むよう変更（`stage-data` に CONFIG 引数を通す）
3. `utils/logger.log_run()` に `competition` / `metric` の明示引数を追加し、train.py から渡す（global 依存の第一段解体）
4. 受け入れ: env/config.yaml を**意図的に別コンペのままにして** `make smoke CONFIG=configs/lgbm_baseline.yaml` と `make train-vertex --dry-run`＋ローカルで KBC 未設定プロセスから train を起動し、metrics.json / staging 先 / BQ 行の competition がすべて CONFIG 側になること
5. 併せて `docs/02_architecture.md` の Vertex 実行契約に「config-b64 が data セクションも含め正本」と明記（現状の暗黙の嘘を仕様で上書き）

P0-1 / P0-4 のタスクノートには「前提: P0-A」「catboost はシグネチャ統一が必要（docstring は現状嘘）」の追記が必要。

## 10. 最終的に目指すディレクトリ構成案

```text
configs/
  <comp>/
    baseline.yaml          # make init が生成、人間が確定
    fe_*.yaml              # sweep 用バリエーション
env/
  project.yaml             # GCP 設定（全コンペ共通）
  config.yaml              # legacy（run.py / notebooks 専用と明記 → 最終削除）
src/
  config.py                # ExperimentConfig ローダ（global 定数は互換層として段階退役）
  pipelines/
    ingest.py              # generic loader（sample_submission 読込を含む）
    featurize.py           # FEATURE_REGISTRY 適用のみ
    splits.py              # CV_STRATEGIES（新規・全 trainer 共用）
    evaluate.py            # METRICS registry（fn + lower_is_better）
    score.py               # submission adapter（sample 正本）
  features/
    __init__.py            # FEATURE_REGISTRY
    stellar.py ...         # コンペ別 FE（registry 登録制）
  models/
    __init__.py            # TRAINERS registry
    lgbm.py / catboost_.py / xgboost_.py / ensemble.py   # 統一シグネチャ
  competitions/            # escape hatch（特殊 loader/提出のみ。generic なら空）
    rogii.py               # 必要になった時だけ
  runner/                  # 全コンペ共通（現行のまま + package_kernel / blend / lb_sync）
  serving/
data/<comp>/...            # 現行のまま
outputs/runs/<comp>/<run_id>/   # 現行契約 + preprocess.json + submission_contract.json
```

**規約（1行で言える形）**: 「新コンペで編集してよいのは `configs/<comp>/` と `docs/competitions/<comp>.md` と（特殊時のみ）`src/competitions/<comp>.py`。それ以外の src/ にコンペ名が現れたらリファクタ対象」。

---

## 付記: 本調査で新たに見つけた前回レビュー外の問題（再掲）

1. Vertex 経路の config 無視（セクション4 #2）— **最重要・新規**
2. metric 方向の3重複実装（#9）— HPO 逆最適化リスク
3. BQ JOIN の run_id 衝突（#14）— 複数コンペ蓄積後に顕在化
4. ✅ catboost_.py の嘘 docstring（#11）と ports.py の dead spec（#12）は 2026-07-07 に解消済み
5. ✅ init_competition の旧 config 表記 drift（#13）は 2026-07-07 に解消済み
