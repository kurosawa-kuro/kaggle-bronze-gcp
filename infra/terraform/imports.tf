# Existing resources observed before Terraform adoption. Keep these import blocks
# until the first successful `terraform plan` / state import, then remove them in
# the follow-up state hygiene commit if desired.

import {
  to = google_storage_bucket.runs
  id = "mlops-dev-a-kaggle-bronze-runs"
}

import {
  to = google_artifact_registry_repository.kaggle
  id = "projects/mlops-dev-a/locations/us-central1/repositories/kaggle"
}

import {
  to = google_bigquery_dataset.ops
  id = "projects/mlops-dev-a/datasets/kaggle_ops"
}

import {
  to = google_bigquery_table.experiments
  id = "projects/mlops-dev-a/datasets/kaggle_ops/tables/experiments"
}

import {
  to = google_bigquery_table.cost_estimates
  id = "projects/mlops-dev-a/datasets/kaggle_ops/tables/cost_estimates"
}
