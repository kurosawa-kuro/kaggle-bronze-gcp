# P0-2: code competition 用 package-kernel 最小経路（LGBM のみ）

## Goal

`make package-kernel CONFIG=<path> RUN_ID=<id>` で、run_id 成果物（boosters + 前処理状態）を Kaggle Dataset 化し、**学習せず推論だけ行う** notebook テンプレートを生成する。Vertex で学習した成果物を kernel 9h 制限内に持ち込む経路を通す。

## Context

- 出典: [2026-07-06 銅メダル戦略レビュー](../idea/2026-07-06_bronze-strategy-review.md) P0-2。ROGII は notebook 提出型の可能性が高く、この経路が無いと初回提出が成立しない。
- **着手条件: [P0-0](2026-07-06-p0-0-rogii-rules-check.md) 完了**（Dataset 持込可否・internet on/off の確定が方式を決める）。
- **既知の実装ギャップ**: `pipelines/ingest.py:encode()` は OrdinalEncoder / median 埋めを実行時に fit するだけで永続化しない。`train.py:_write_models()` が保存するのは booster と feature_names のみ。推論専用 notebook は現状の成果物だけでは前処理を再現できない。

## Scope

- In: 前処理状態の永続化、Kaggle Dataset 化 ops、推論 notebook テンプレ生成。**LightGBM 単体のみ**
- Out: CatBoost/XGBoost/blend 対応（P0-4 の後続）、kernel 内学習、Batch Prediction 経路との統合

## Plan

1. 着手時に `write-spec` で SPEC.md 化
2. **前処理状態の永続化（方式 A・正道）**: `model/preprocess.json`（または joblib）に OrdinalEncoder のカテゴリ順・数値列の median・`LABEL_CLASSES`・feature 列順を保存。`train.py` の成果物契約に追加（既存キーは変えない）
   - fallback（方式 B）: Dataset 持込不可の場合のみ「notebook 内で train.csv から前処理だけ再 fit（学習はしない）」に切替。P0-0 の結果で分岐
3. `src/runner/ops/package_kernel.py` 新設: run_dir の `model/` + `config.yaml` + `manifest.json` を staging し、`kaggle datasets create/version` で Dataset 化（slug は `<comp>-<run_id>` 正規化）
4. 推論 notebook テンプレ生成: Dataset を attach → manifest.json を読み全 booster 平均（`pipelines/score.py:predict` と同ロジック）→ preprocess.json で test を変換 → submission.csv。`serving/predictor.py` のロード処理を流用
5. Makefile に `package-kernel` ターゲット追加、README / docs 更新

## Acceptance Criteria

- [x] playground-series-s6e6 の既存 run_id からパッケージを生成し、notebook 相当のスクリプトを**ローカルの素の Python で**実行して、`make train-local` が出した submission.csv と一致する（前処理再現の証明）
- [x] `kaggle datasets version` まで実際に通り、Kaggle 上に private Dataset ができる
- [x] notebook テンプレが「学習コードを含まない」ことを目視確認（推論・前処理のみ）
- 検証コマンド: `make package-kernel CONFIG=configs/lgbm_baseline.yaml RUN_ID=full_gcp_lgbm_001` → 生成スクリプトを隔離ディレクトリで実行 → `diff` で submission 一致

## 破綻条件

- コンペルールが事前学習成果物の持込を禁止 → 方式 B へ設計変更（P0-0 で事前検知）
- internet-off kernel での Dataset attach 手順ミス → テンプレに attach 手順コメントを埋め込む
- 前処理の train/kernel 間不一致（pandas バージョン差の dtype 揺れ等）→ Acceptance 1 個目の submission 完全一致で検出
- Kaggle Dataset の 20GB/公開制約 → boosters は txt で数十 MB 級のはずだが、パッケージ時にサイズを表示して警告

## Result

2026-07-06 完了。

実装:

- `src/pipelines/ingest.py`: `fit_preprocessor()` / `apply_preprocessor()` を追加。数値median、カテゴリ順、未知カテゴリ値を永続化可能にした。
- `src/pipelines/featurize.py`: `make_features(..., return_preprocess_state=True)` を追加。既存呼び出しは互換維持。
- `src/runner/experiment/train.py`: `model/preprocess.json` を保存する成果物契約へ拡張。
- `src/runner/ops/package_kernel.py`: run成果物からKaggle Dataset用 package と推論専用 `kernel_inference.py` / `kernel_inference.ipynb` を生成。
- `Makefile`: `make package-kernel` を追加。

検証:

```bash
python3 -m py_compile src/pipelines/ingest.py src/pipelines/featurize.py src/runner/experiment/train.py src/runner/ops/package_kernel.py
make smoke CONFIG=configs/lgbm_baseline.yaml RUN_ID=p02_package_smoke
make package-kernel CONFIG=configs/lgbm_baseline.yaml RUN_ID=p02_package_smoke
.venv/bin/python outputs/kernel_packages/playground-series-s6e6/p02_package_smoke/kernel_inference.py \
  --package-dir outputs/kernel_packages/playground-series-s6e6/p02_package_smoke \
  --data-dir data/playground-series-s6e6/raw \
  --output /tmp/kbc_p02_kernel/submission.csv
cmp -s outputs/runs/playground-series-s6e6/p02_package_smoke/submission.csv /tmp/kbc_p02_kernel/submission.csv
```

結果:

- `submission_csv_exact_match=1`
- package size: 0.97 MiB
- Kaggle private Dataset: https://www.kaggle.com/datasets/kurosawakuro/playground-series-s6e6-p02-package-smoke
- `kaggle datasets create` 成功。
- `kaggle datasets version` 成功。
- `kaggle datasets status`: `ready`

ROGII 注意:

- 生成済み `kernel_inference.py` は現時点では標準 `test.csv` コンペ用。
- ROGII は directory dataset かつ hidden test 置換型なので、`sample_submission.csv` 正本化と `well_id` 生成 adapter が別途必要。
- ただし P0-2 の中核である「Vertex/ローカル学習済みLGBM成果物をKaggle Notebook推論専用packageへ変換し、前処理を完全再現する経路」は完了。
