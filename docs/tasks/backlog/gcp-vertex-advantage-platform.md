# GCP/Vertex 優位性基盤への再設計

## Goal

Kaggle ブロンズ取得に向けて、GCP/Vertex を「ただの外部実行先」ではなく、普通のローカル参加者が得にくい計算量・再現性・リーク防止・実験比較の優位性に変える。

最低限の期待仕様:

```text
ローカル = 指揮所・EDA・smoke・実験比較・提出判断
GCP/Vertex = 重い訓練・seed平均・複数config sweep・HPOの加速装置
GCS/BigQuery = 再現性・成果物・実験台帳の共通基盤
Terraform = GCP土台を再現可能にする設計図
```

## Context

現状は GCP 連携コード自体はあるが、Terraform によるリソース定義ではなく、Makefile から `gcloud` / `bq` / Vertex SDK / GCS SDK を手続き的に呼ぶ構造になっている。

実装済みの前提（本タスクの対象外。検証 2026-07-06）:

- 重い訓練 / 並列 sweep / managed HPO / seed averaging は実装済み。
  `make train-vertex` / `make sweep` / `make hp-tune`（Vizier）、`src/runner/experiment/train.py` の `seeds` ループ（`configs/*.yaml` の `seeds: [42, 777, 2026]`）、`tune.py --final` の seed-averaged run。
- 期待仕様とのギャップの本体は「重い計算を Vertex へ」ではなく、**実験台帳の信頼性・IaC・比較導線**。

現状の主なズレ:

- `make gcp-bootstrap` は API enable / Artifact Registry repo / GCS bucket 作成のみ。
- BigQuery dataset / tables / IAM / Service Account / Budget alert は IaC 管理されていない。
- BigQuery 実験ログは `bq` CLI 経由（`src/utils/bq.py` が subprocess で呼ぶ）だが、Vertex 学習イメージ（`infra/Dockerfile`、python:3.12-slim ベース）に `bq` が存在しない。
- `logger.py:64` は `except SystemExit` しか捕捉しないため、`bq` バイナリ不在時の `FileNotFoundError` は未捕捉。**Vertex 実行時は「ログ欠落」ではなく訓練プロセス自体が末尾でクラッシュし得る。**
- GCP/Vertex の目的が「ブロンズ獲得の非対称優位」ではなく「外部に投げられる runner」に留まっている。

## Scope

含む:

- Terraform による GCP 基盤定義
  - API enable
  - GCS bucket
  - Artifact Registry
  - BigQuery dataset / tables
  - Vertex 実行用 Service Account
  - IAM roles
  - Budget alert / cost guardrail
- BigQuery logger の実運用化
  - `bq` CLI 依存をやめ、`google-cloud-bigquery` Python client に変更
  - Vertex コンテナ内から Service Account 権限で実験ログを書けるようにする
  - BigQuery 記録失敗を完全握りつぶしにせず、warning artifact / log に残す
- ローカル → GCP 実験導線の明確化
  - `make smoke`
  - `make stage-data`
  - `make build-push`
  - `make train-vertex`
  - `make sweep`
  - `make hp-tune`
  - `make collect`
  - `make compare`
  - `make submit`
- Vertex を優位性基盤として使う設計
  - ※ heavy full training / seed averaging / parallel config sweep / managed HPO は**実装済み**（Context 参照）。本タスクでは変更しない
  - immutable dataset snapshot
  - fold manifest 固定
  - leakage audit
  - experiment / cost / feature lineage の BigQuery 集約
- ADR 0002 の改訂と CLAUDE.md 作業ルールの同時更新
  - 「新しい infra lib を足さない（`bq` CLI 経由）」の決定を「`google-cloud-bigquery` Python client 経由」へ改訂する
  - `src/utils/bq.py` docstring も同一変更で更新し drift を作らない

含まない:

- DL / GPU / LLM / RAG 前提の方針転換
- GKE / Cloud Composer / MLflow server / Ray cluster など、ブロンズ目的に対して運用負荷が大きい常駐基盤
- **Vertex AI Feature Store（製品）**。オンライン serving が無い本用途では設計・権限・運用コストに見合わない。Feature Store 的なオフライン特徴量管理（feature lineage / snapshot / fold-aware transform / leakage audit）は BigQuery + GCS で実装する
- Kaggle token を Vertex 側へ持ち込む提出自動化

## Plan

1. 現状棚卸し
   - Makefile / `env/project.yaml` / `src/utils/bq.py` / `src/utils/logger.py` / Vertex runner の責務を整理する。
   - 「ローカルだけで動くもの」「Vertex 内で動くもの」「既存GCPリソース前提のもの」を表にする。

2. Terraform skeleton
   - `infra/terraform/` を追加する。
   - project / region / bucket / dataset / repository / service account を variables 化する。
   - まず `terraform plan` が通る最小構成を作る。

3. GCP resource IaC 化
   - **既存リソースの import を先に行う**: GCS bucket / Artifact Registry repo / `kaggle_ops` dataset は `gcp-bootstrap` 実行済みで実在する（2026-06-15 に全パイプライン SUCCEEDED）。Terraform の `import` ブロックで state に取り込み、`terraform plan` が既存リソースの「新規作成」差分を出さないことを確認してから管理下に置く。
   - GCS bucket / Artifact Registry / BigQuery dataset / tables / Service Account / IAM を Terraform 管理へ移す。
   - `make gcp-bootstrap` は Terraform への案内または軽量 wrapper に縮退する。

4. BigQuery logger 修正
   - `google-cloud-bigquery` を依存に追加する（ADR 0002 改訂・CLAUDE.md 更新と同一変更で行う）。
   - `src/utils/bq.py` を Python client 実装へ差し替える。
   - 例外処理を `SystemExit` 限定から見直す。記録失敗（クライアント例外・権限不足・ライブラリ不在を含む）で訓練本体を落とさず、warning を run artifact / log に残す。
   - Vertex Custom Job 内の Service Account で `experiments` へ書けることを確認する。

5. 実験優位性機能
   - `make compare` を追加し、BigQuery から run_id / score / params / cost を比較する。
   - dataset snapshot / fold manifest / leakage audit の成果物を run_id 配下に保存する。
   - Vertex sweep / HPT の結果を BigQuery で横断比較できるようにする。

6. ドキュメント更新
   - **ADR 0002 を改訂する（必須）**: tabular メタデータの正本は BigQuery のまま、アクセス手段を `bq` CLI から `google-cloud-bigquery` Python client へ変更する判断と理由（Vertex コンテナ内で CLI が使えない）を記録する。
   - **CLAUDE.md 作業ルールの「新しい infra lib を足さない（`bq` CLI 経由）」を同一変更で更新する（必須）**。
   - `docs/01_requirements.md`
   - `docs/02_architecture.md`
   - `docs/04_workflows.md`
   - `docs/05_data_model.md`
   - `docs/08_release_runbook.md`

## Acceptance Criteria

- 既存リソース（GCS bucket / Artifact Registry repo / `kaggle_ops` dataset）が Terraform state に import 済みで、`terraform plan` が「新規作成」ではなく No changes または意図した差分のみを表示する。
- Terraform で以下が管理される:
  - GCS bucket
  - Artifact Registry repo
  - BigQuery dataset
  - `experiments` table
  - `cost_estimates` table
  - Vertex 実行 Service Account
  - 必要 IAM
  - Budget alert
- `make train-vertex CONFIG=... RUN_ID=...` 実行後、Vertex 内から BigQuery `experiments` に run が記録される。
- `make hp-tune` / `make sweep` の結果を `make compare` で比較できる。
- BigQuery ログ失敗時（`bq` バイナリ不在・クライアント例外・権限不足の各ケースを含む）に、学習本体がクラッシュせず、warning が run artifact か log に残る。
- dataset snapshot / fold manifest / leakage audit の成果物が `outputs/runs/<comp>/<run_id>/` 配下（および GCS の run_id 配下）に保存され、run_id から追跡できる。
- ADR 0002 の改訂と CLAUDE.md 作業ルールの更新が同一変更に含まれる（`bq` CLI → Python client）。
- `docs/04_workflows.md` を読めば、ローカル指揮所 + GCP加速装置の実験導線が迷わず分かる。

## Verification

```bash
terraform -chdir=infra/terraform fmt -check
terraform -chdir=infra/terraform validate
terraform -chdir=infra/terraform plan

make smoke CONFIG=configs/lgbm_baseline.yaml RUN_ID=smoke_check
make stage-data
make build-push
make train-vertex CONFIG=configs/lgbm_baseline.yaml RUN_ID=vertex_bq_check
make collect CONFIG=configs/lgbm_baseline.yaml RUN_ID=vertex_bq_check
make logs
make compare
```

追加確認:

```bash
bq query --use_legacy_sql=false \
  'SELECT run_id, cv_score, metric, competition, recorded_at
   FROM `kaggle_ops.experiments`
   WHERE run_id LIKE "vertex_bq_check%"
   ORDER BY recorded_at DESC'
```

## Notes

- 期待仕様は「全部GCP化」ではない。
- Kaggle token は local に留め、提出は local CLI で行う。
- GCP は重い計算を並列に逃がす加速装置として使う。
- Terraform は GCP 経験を再現可能な優位性に変えるための土台。
- **Feature Store 方針**: Vertex AI Feature Store（製品）は採用しない。オンライン serving が無い Kaggle 用途では、効くのは製品ではなく feature registry / lineage / point-in-time な snapshot / fold-aware transform であり、これらは BigQuery + GCS で軽く実装する。必要が生じたら（オンライン推論が要件になったら）採用を再検討する。
- heavy training / sweep / HPO / seed averaging は実装済みのため本タスクの作業項目ではない。Context の「実装済みの前提」を棚卸し（Plan step 1）の起点にする。
- 2026-07-06 レビュー反映: Terraform import 手順の明記、ADR 0002 改訂の必須化、logger の未捕捉例外（FileNotFoundError）による訓練クラッシュリスクの明記、Feature Store 不採用方針の追記。
