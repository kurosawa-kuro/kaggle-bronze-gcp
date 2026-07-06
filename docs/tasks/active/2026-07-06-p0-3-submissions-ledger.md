# P0-3: 提出台帳（BigQuery `kaggle_ops.submissions`）と LB 同期

## Goal

どの run_id をいつ提出し public LB が何点だったかを BigQuery に記録し、CV↔LB の相関を `make compare` 系で見られるようにする。public LB 過学習を防ぐ判断材料と、final 2 提出の選定根拠を作る。

## Context

- 出典: [2026-07-06 銅メダル戦略レビュー](../idea/2026-07-06_bronze-strategy-review.md) P0-4（守りの要）。
- 現状 `src/runner/ops/submit.py` は Kaggle CLI を叩くだけで台帳が残らない。experiments × cost_estimates の run_id JOIN は既にあるので、submissions が入れば 3-way JOIN が完成する。
- 前提タスクなし（P0-1/P0-2 と並行可。半日規模なので SPEC 省略可の小規模修正に近いが、テーブル DDL は ADR 0002 の BQ 統一方針に従う）。

## Scope

- In: `submissions` テーブル新設、`make submit` 成功時の INSERT、`make lb-sync` による public LB 回収、`make compare` への CV↔LB 表示
- Out: private LB（コンペ終了後に手動追記）、Web UI 提出の自動検知（lb-sync が CLI 経由で全提出を吸うことで補完）

## Plan

1. `kaggle_ops.submissions` DDL: `run_id, competition, submitted_at TIMESTAMP, message, cv_score FLOAT64, public_lb FLOAT64, selected_final BOOL, notes`。`utils/logger.py` と同型の ensure パターンで `utils/bq.py` 系に実装
2. `submit.py`: 提出成功（returncode==0）時に run_dir の `metrics.json` から cv_score を読んで INSERT（BQ 失敗で提出自体は止めない — logger.py と同じ warning 方針）
3. `src/runner/ops/lb_sync.py` 新設: `kaggle competitions submissions -c <comp> -v` を parse し、message/日時で突合して `public_lb` を MERGE。台帳に無い提出（Web UI 手動分）は run_id=NULL で挿入して穴を可視化
4. `compare.py` に submissions を LEFT JOIN し、`cv_score` と `public_lb` を並べる列を追加
5. Makefile に `lb-sync` 追加、README 更新

## Acceptance Criteria

- [x] `make submit`（playground-series-s6e6 の既存 run_id）成功後、BQ `kaggle_ops.submissions` に 1 行入る
- [x] `make lb-sync` 実行後、その行の `public_lb` が Kaggle 上のスコアと一致する
- [x] `make compare` で run_id ごとに cv_score / public_lb / est_jpy が 1 行で見える
- 検証コマンド: `make submit CONFIG=configs/lgbm_baseline.yaml RUN_ID=full_gcp_lgbm_001 MSG="ledger check"` → `make lb-sync` → `make compare`

## 破綻条件

- Kaggle CLI の submissions 出力の parse が形式変更で壊れる → `--csv` 等の機械可読出力を使い、parse 失敗時は明示エラー（黙って 0 件にしない）
- message での突合が重複 message で曖昧になる → submit 時に message へ run_id を自動サフィックスする規約を submit.py 側で強制
- BQ 書込失敗で提出まで失敗する → logger.py と同じ「警告して続行 + warnings/ 成果物」方針を踏襲

## Result

2026-07-06 完了。

実装:

- `src/runner/ops/submission_ledger.py`: `kaggle_ops.submissions` の ensure / submit記録 / Kaggle履歴CSV parse / sync merge を実装。
- `src/runner/ops/submit.py`: Kaggle提出成功時にBQへ記録。messageへ `[run_id=<run_id>]` を自動付与。
- `src/runner/ops/lb_sync.py`: `kaggle competitions submissions --csv` をBQへ同期。
- `src/runner/ops/compare.py`: `experiments` / `cost_estimates` / `submissions` を `(competition, run_id)` で表示。
- `Makefile`: `lb-sync` 追加、`submit` の Doppler project/config 明示化。
- `tests/test_submission_ledger.py`: message run_id tag と Kaggle submissions CSV parser のテスト追加。

検証:

```bash
python3 -m py_compile src/runner/ops/submission_ledger.py src/runner/ops/lb_sync.py src/runner/ops/submit.py src/runner/ops/compare.py
PYTHONPATH=src .venv/bin/python -m unittest tests.test_submission_ledger tests.test_splits
make submit CONFIG=configs/lgbm_baseline.yaml RUN_ID=p02_package_smoke MSG="ledger check"
make lb-sync CONFIG=configs/lgbm_baseline.yaml
make compare CONFIG=configs/lgbm_baseline.yaml COMP=playground-series-s6e6 RUN_LIKE=p02% LIMIT=5
```

結果:

- `make submit`: Kaggle提出成功。message は `ledger check [run_id=p02_package_smoke]`。
- `make lb-sync`: 4 submissions synced。
- `kaggle_ops.submissions`: `submission_ref=54398292`, `run_id=p02_package_smoke`, `public_lb=0.89905`, `private_lb=0.89841`。
- `make compare`: `cv_score=0.3276377551043895` / `public_lb=0.89905` / `private_lb=0.89841` / `est_jpy` を1行で表示。

実装メモ:

- BigQuery streaming buffer 中はMERGE/UPDATE不可のため、`lb-sync` はその場合だけappendへfallbackする。
- `compare` 側は同じ `(competition, run_id, message)` の重複行をdedupeし、score付き行を優先表示する。
