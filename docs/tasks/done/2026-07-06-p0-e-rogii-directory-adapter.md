# P0-E: ROGII directory adapter + sample_submission 正本化

## Goal

ROGII の `train/*.csv` / `test/*.csv` / `sample_submission.csv` 形式を既存 runner と package kernel に接続し、初回 Kaggle Notebook 提出の手前まで詰まりをなくす。

## Context

- P0-0 で ROGII は Code Competition / hidden test 置換型 / directory dataset と確認済み。
- P0-1 で `cv.strategy: group` / `cv.group_col: well_id` は実装済み。
- P0-2 で標準 `test.csv` コンペ向け package kernel は実装済み。
- ROGII は学習targetが `TVT`、提出列が `tvt` なので sample_submission 正本化も同時に必要。

## Scope

- In: ROGII loader、`well_id` / `row_index` / `id` 生成、target zone抽出、sample_submission順のtest生成、`submission_target`対応、ROGII config、package kernel のROGII test adapter
- Out: Typewell特徴量、地質画像、精密FE、full Vertex training

## Result

2026-07-06 完了。

実装:

- `src/competitions/rogii.py`: ROGII directory loader を追加。
- `src/pipelines/ingest.py`: ROGII directory adapter を自動選択。
- `src/config.py`: `SUBMISSION_TARGET` を追加。
- `src/pipelines/score.py`: 提出列名に `submission_target` を使用。
- `src/runner/ops/package_kernel.py`: 生成される `kernel_inference.py` に ROGII test adapter を埋め込み。
- `configs/rogii_lgbm_baseline.yaml`: ROGII用LGBM baseline configを追加。
- `tests/test_rogii_loader.py`: target zone抽出と sample_submission順のテストを追加。

検証:

```bash
python3 -m py_compile src/competitions/rogii.py src/pipelines/ingest.py src/pipelines/score.py src/config.py src/runner/ops/package_kernel.py
PYTHONPATH=src .venv/bin/python -m unittest tests.test_rogii_loader tests.test_submission_ledger tests.test_splits
PYTHONPATH=src KBC_CONFIG_PATH=configs/rogii_lgbm_baseline.yaml .venv/bin/python - <<'PY'
from pipelines.ingest import load_data
train_df, test_df = load_data()
print(train_df.shape, test_df.shape)
PY
make smoke CONFIG=configs/rogii_lgbm_baseline.yaml RUN_ID=rogii_adapter_smoke
make package-kernel CONFIG=configs/rogii_lgbm_baseline.yaml RUN_ID=rogii_adapter_smoke
.venv/bin/python outputs/kernel_packages/rogii-wellbore-geology-prediction/rogii_adapter_smoke/kernel_inference.py \
  --package-dir outputs/kernel_packages/rogii-wellbore-geology-prediction/rogii_adapter_smoke \
  --data-dir data/rogii-wellbore-geology-prediction/raw \
  --output /tmp/kbc_rogii_kernel/submission.csv
cmp -s outputs/runs/rogii-wellbore-geology-prediction/rogii_adapter_smoke/submission.csv /tmp/kbc_rogii_kernel/submission.csv
```

結果:

- loader: `train=(200000, 10)`, `test=(14151, 9)`（configのlocal guardrailによりtrainは200k sample）
- train wells: 773、visible test wells: 3
- submission columns: `id,tvt`
- `fold_manifest.strategy`: `group`
- `fold_manifest.group_col`: `well_id`
- group overlap: 0
- smoke CV RMSE: `184.86839178738845`
- package kernel再推論: `rogii_package_submission_exact_match=1`

## Notes

- `configs/rogii_lgbm_baseline.yaml` はローカル安全用に `data.train_row_limit: 200000` を入れている。Vertex full run ではこの上限を外すか、別configを作る。
- 現baselineは Typewell / geology /画像特徴量をまだ使わない。提出可能性を先に通すための最小adapter。
