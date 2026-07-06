.PHONY: setup run nb logs clean init download submit smoke train-local train-vertex collect register-model register-servable pipeline build-push build-push-serving batch-input batch-predict endpoint-deploy endpoint-teardown gcp-bootstrap submit-legacy package-kernel lb-sync stage-data cost cost-record cost-notify sweep tune hp-tune compare blend terraform-init terraform-plan

VENV   := .venv
PYTHON := $(VENV)/bin/python
UV     := uv
# entrypoints は src/runner/ パッケージ。runner 実行時のみ src を import パスに通す
# （gcloud/bq/kaggle 等の外部 Python CLI に PYTHONPATH=src を渡すと自身の utils を
#   こちらの src/utils で shadow され壊れるため、グローバル export はしない）。
PYRUN  := PYTHONPATH=src $(PYTHON) -m
CONFIG ?= configs/lgbm_baseline.yaml
RUN_ID ?= $(shell date -u +%Y%m%d_%H%M%S)
PROJECT_CONFIG ?= env/project.yaml
GCP_PROJECT ?= $(shell $(PYTHON) -c 'import yaml; c=yaml.safe_load(open("$(PROJECT_CONFIG)")) or {}; print(c.get("gcpProject") or c.get("gcp", {}).get("project") or "")' 2>/dev/null)
GOOGLE_CLOUD_QUOTA_PROJECT ?= $(GCP_PROJECT)
REGION ?= $(shell $(PYTHON) -c 'import yaml; c=yaml.safe_load(open("$(PROJECT_CONFIG)")) or {}; print(c.get("gcpRegion") or c.get("gcp", {}).get("region") or "us-central1")' 2>/dev/null)
AR_REPO ?= $(shell $(PYTHON) -c 'import yaml; print((yaml.safe_load(open("$(PROJECT_CONFIG)")) or {}).get("artifactRegistryRepo") or "kaggle")' 2>/dev/null)
IMAGE_NAME ?= $(shell $(PYTHON) -c 'import yaml; print((yaml.safe_load(open("$(PROJECT_CONFIG)")) or {}).get("imageName") or "kaggle-bronze-gcp")' 2>/dev/null)
IMAGE_TAG ?= $(shell $(PYTHON) -c 'import yaml; print((yaml.safe_load(open("$(PROJECT_CONFIG)")) or {}).get("imageTag") or "latest")' 2>/dev/null)
GCS_BUCKET ?= $(shell $(PYTHON) -c 'import yaml; print((yaml.safe_load(open("$(PROJECT_CONFIG)")) or {}).get("gcsBucket") or "")' 2>/dev/null)
COMP_DATA ?= $(shell $(PYTHON) -c 'import yaml; c=yaml.safe_load(open("$(CONFIG)")) or {}; print(c.get("comp") or c.get("competition", {}).get("slug") or c.get("data", {}).get("comp") or "")' 2>/dev/null)
IMAGE ?= $(REGION)-docker.pkg.dev/$(GCP_PROJECT)/$(AR_REPO)/$(IMAGE_NAME):$(IMAGE_TAG)
SERVING_IMAGE ?= $(REGION)-docker.pkg.dev/$(GCP_PROJECT)/$(AR_REPO)/$(IMAGE_NAME)-serving:$(IMAGE_TAG)
# overnight バッチ既定で Spot（約1/3以下）。on-demand にするには: make train-vertex SPOT=
SPOT ?= --spot
VERTEX_MAX_LOG_SILENCE_MINUTES ?= 10
VERTEX_CANCEL_ON_SILENCE ?= --cancel-on-silence

# 初期セットアップ: venv 作成 + 依存インストール
setup:
	$(UV) venv $(VENV)
	$(UV) pip install -r requirements.txt --python $(VENV)/bin/python
	@echo "Setup complete. Run: make run"

# 現在の実験を実行 (run.py)
run:
	$(PYRUN) runner.run

# Vertex-ready runner: quick one-fold local check
smoke:
	$(PYRUN) runner.experiment.train --config $(CONFIG) --run-id $(RUN_ID) --smoke

# Vertex-ready runner: full local training
train-local:
	$(PYRUN) runner.experiment.train --config $(CONFIG) --run-id $(RUN_ID)

# Build and push the training image to Artifact Registry
build-push:
	gcloud auth configure-docker $(REGION)-docker.pkg.dev --quiet
	docker buildx build --platform linux/amd64 -f infra/Dockerfile -t $(IMAGE) --push .

# Terraform is the source of truth for GCP resources.
terraform-init:
	GOOGLE_CLOUD_QUOTA_PROJECT=$(GOOGLE_CLOUD_QUOTA_PROJECT) terraform -chdir=infra/terraform init

terraform-plan:
	GOOGLE_CLOUD_QUOTA_PROJECT=$(GOOGLE_CLOUD_QUOTA_PROJECT) terraform -chdir=infra/terraform plan

# Legacy wrapper: keep the old command discoverable, but manage resources via Terraform.
gcp-bootstrap:
	@echo "GCP bootstrap is now Terraform-managed. Run: make terraform-init && make terraform-plan"

# Stage local raw data to GCS so the Vertex container can fetch it (train.py --input-uri)
stage-data:
	gcloud storage cp --recursive data/$(COMP_DATA)/raw gs://$(GCS_BUCKET)/data/$(COMP_DATA)/

# Submit the same train.py contract to Vertex Custom Job (Spot by default).
# Wait for completion with: make train-vertex SYNC=--sync
train-vertex:
	$(PYRUN) runner.experiment.vertex_run --config $(CONFIG) --run-id $(RUN_ID) --image-uri $(IMAGE) $(SPOT) $(SYNC) $(DRY) --max-log-silence-minutes $(VERTEX_MAX_LOG_SILENCE_MINUTES) $(VERTEX_CANCEL_ON_SILENCE)

# Optuna 探索（1マシン）。best params を run_id 成果物に保存。N_TRIALS / FINAL=--final
# make tune CONFIG=configs/lgbm_baseline.yaml RUN_ID=tune01 N_TRIALS=30
tune:
	$(PYRUN) runner.experiment.tune --config $(CONFIG) --run-id $(RUN_ID) --n-trials $(or $(N_TRIALS),30) $(FINAL)

# Vertex Hyperparameter Tuning (Vizier) — マネージド並列探索。MAX_TRIALS / PARALLEL
# make hp-tune CONFIG=configs/lgbm_baseline.yaml RUN_ID=hpt01 MAX_TRIALS=20 PARALLEL=4
hp-tune:
	$(PYRUN) runner.experiment.hp_tune --config $(CONFIG) --run-id $(RUN_ID) --image-uri $(IMAGE) --max-trials $(or $(MAX_TRIALS),20) --parallel-trials $(or $(PARALLEL),4)

# Fan out multiple configs as parallel Vertex Custom Jobs (Spot by default)
# make sweep CONFIGS="configs/a.yaml configs/b.yaml" TAG=exp01
sweep:
	$(PYRUN) runner.experiment.sweep --configs $(CONFIGS) $(if $(TAG),--tag $(TAG),) --image-uri $(IMAGE) $(SPOT)

# Collect artifacts from gs://<bucket>/runs/<competition>/<run_id>
collect:
	$(PYRUN) runner.ops.collect --config $(CONFIG) --run-id $(RUN_ID)

# Register a run's model into Vertex AI Model Registry (gs://<bucket>/runs/<comp>/<run_id>/model)
register-model:
	$(PYRUN) runner.model.register --config $(CONFIG) --run-id $(RUN_ID)

# Register WITH the real serving container so the model is batch/online predictable
register-servable:
	$(PYRUN) runner.model.register --config $(CONFIG) --run-id $(RUN_ID) --serving-image $(SERVING_IMAGE)

# Submit a Vertex AI Pipeline (KFP): train -> register. DRY=--dry-run for compile-only.
pipeline:
	$(PYRUN) runner.model.pipeline --config $(CONFIG) --run-id $(RUN_ID) $(DRY)

# Build + push the serving image (infra/Dockerfile.serving) to Artifact Registry
build-push-serving:
	gcloud auth configure-docker $(REGION)-docker.pkg.dev --quiet
	docker buildx build --platform linux/amd64 -f infra/Dockerfile.serving -t $(SERVING_IMAGE) --push .

# Submit a Vertex Batch Prediction job. SRC=gs://.../instances.jsonl. DRY=--dry-run.
batch-input:
	$(PYRUN) runner.ops.batch_input --config $(CONFIG) --run-id $(RUN_ID) $(if $(LIMIT),--limit $(LIMIT),)

batch-predict:
	$(PYRUN) runner.model.batch_predict --config $(CONFIG) --run-id $(RUN_ID) --gcs-source $(SRC) $(DRY)

# Deploy a servable model to a Vertex Endpoint. WARNING: 24/7 standing cost. DRY=--dry-run.
endpoint-deploy:
	$(PYRUN) runner.model.deploy deploy --config $(CONFIG) $(DRY)

# Undeploy + delete the Endpoint to stop the standing cost.
endpoint-teardown:
	$(PYRUN) runner.model.deploy teardown --config $(CONFIG) $(DRY)

# Record a finished Vertex job's estimated cost into BigQuery (kaggle_ops.cost_estimates)
cost-record:
	$(PYRUN) runner.ops.costs record --config $(CONFIG) --run-id $(RUN_ID)

# Show month-to-date estimated GCP cost vs ¥1000/¥5000 thresholds
cost:
	$(PYRUN) runner.ops.costs report --config $(CONFIG)

# Compare experiments and cost estimates from BigQuery
compare:
	$(PYRUN) runner.ops.compare --project-config $(PROJECT_CONFIG) $(if $(COMP),--competition $(COMP),) $(if $(RUN_LIKE),--run-like "$(RUN_LIKE)",) $(if $(LIMIT),--limit $(LIMIT),)

# Blend compatible OOF/test predictions. Example:
# make blend CONFIG=configs/lgbm_baseline.yaml RUN_IDS="lgbm001 cat001" RUN_ID=blend001
blend:
	$(PYRUN) runner.ops.blend --config $(CONFIG) --run-ids $(RUN_IDS) --run-id $(RUN_ID)

# Push the month-to-date cost summary to Discord (webhook in env/secret.yaml)
cost-notify:
	$(PYRUN) runner.ops.costs notify --config $(CONFIG)

# 特定のノートブック実験を実行: make nb NB=exp002_catboost_base
nb:
	$(PYTHON) notebooks/$(NB).py

# 実験ログを表示
logs:
	PYTHONPATH=src $(PYTHON) -c "from utils.logger import show_runs; show_runs()"

# 新コンペ初期化: make init COMP=house-prices-advanced-regression-techniques
# download → train/test 正規化 → config.yaml 下書き表示 → competition doc 生成
init:
	doppler run -- sh -c 'KAGGLE_API_TOKEN="$$ML_KAGGLE_TOKEN" $(PYTHON) scripts/init_competition.py $(COMP)'

# Kaggle データ取得: make download COMP=house-prices
# Doppler の ML_KAGGLE_TOKEN を KAGGLE_API_TOKEN にマッピングして kaggle CLI へ渡す
download:
	mkdir -p data/$(COMP)/raw
	doppler run -- sh -c 'KAGGLE_API_TOKEN="$$ML_KAGGLE_TOKEN" $(VENV)/bin/kaggle competitions download -c $(COMP) -p data/$(COMP)/raw'

# Kaggle 提出: make submit CONFIG=configs/lgbm_baseline.yaml RUN_ID=exp001 MSG="exp001 lgbm baseline"
submit:
	doppler run --project kuro-dev-k --config dev -- sh -c 'KAGGLE_API_TOKEN="$$ML_KAGGLE_TOKEN" PYTHONPATH=src $(PYTHON) -m runner.ops.submit --config $(CONFIG) --run-id $(RUN_ID) --message "$(MSG)"'

# Code Competition 用の推論専用 package/notebook 生成。
# Kaggle Dataset まで publish する場合: make package-kernel ... PACKAGE_ARGS="--create-dataset"
package-kernel:
	doppler run --project kuro-dev-k --config dev -- sh -c 'KAGGLE_API_TOKEN="$$ML_KAGGLE_TOKEN" PYTHONPATH=src $(PYTHON) -m runner.ops.package_kernel --config $(CONFIG) --run-id $(RUN_ID) $(PACKAGE_ARGS)'

# Kaggle submissions 履歴を BigQuery kaggle_ops.submissions に同期
lb-sync:
	doppler run --project kuro-dev-k --config dev -- sh -c 'KAGGLE_API_TOKEN="$$ML_KAGGLE_TOKEN" PYTHONPATH=src $(PYTHON) -m runner.ops.lb_sync --config $(CONFIG) $(if $(COMP),--competition $(COMP),)'

# 旧提出経路: repository root の submission.csv を直接提出
submit-legacy:
	doppler run -- sh -c 'KAGGLE_API_TOKEN="$$ML_KAGGLE_TOKEN" $(VENV)/bin/kaggle competitions submit -c $(COMP) -f submission.csv -m "$(MSG)"'

# 生成物を削除
clean:
	rm -f submission.csv
	find . -name "__pycache__" -type d | xargs rm -rf
