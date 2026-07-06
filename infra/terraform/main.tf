locals {
  services = toset([
    "aiplatform.googleapis.com",
    "artifactregistry.googleapis.com",
    "bigquery.googleapis.com",
    "cloudbilling.googleapis.com",
    "billingbudgets.googleapis.com",
    "storage.googleapis.com",
  ])
}

resource "google_project_service" "apis" {
  for_each = local.services

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_storage_bucket" "runs" {
  name                        = var.gcs_bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = false

  labels = {
    app     = "kaggle-bronze-gcp"
    purpose = "runs"
  }
}

resource "google_artifact_registry_repository" "kaggle" {
  location      = var.region
  repository_id = var.artifact_registry_repo
  format        = "DOCKER"
  description   = "Kaggle Bronze training and serving images"

  labels = {
    app = "kaggle-bronze-gcp"
  }
}

resource "google_bigquery_dataset" "ops" {
  dataset_id                 = var.bq_dataset_id
  location                   = var.region
  description                = "Kaggle bronze ops: cost tracking"
  delete_contents_on_destroy = false

  labels = {
    app     = "kaggle-bronze-gcp"
    purpose = "ops"
  }
}

resource "google_bigquery_table" "experiments" {
  dataset_id          = google_bigquery_dataset.ops.dataset_id
  table_id            = "experiments"
  deletion_protection = true

  schema = jsonencode([
    { name = "run_id", type = "STRING", mode = "NULLABLE" },
    { name = "recorded_at", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "cv_score", type = "FLOAT", mode = "NULLABLE" },
    { name = "metric", type = "STRING", mode = "NULLABLE" },
    { name = "competition", type = "STRING", mode = "NULLABLE" },
    { name = "params", type = "STRING", mode = "NULLABLE" },
    { name = "notes", type = "STRING", mode = "NULLABLE" },
    { name = "source", type = "STRING", mode = "NULLABLE" }
  ])
}

resource "google_bigquery_table" "cost_estimates" {
  dataset_id          = google_bigquery_dataset.ops.dataset_id
  table_id            = "cost_estimates"
  description         = "GCP cost estimates (any service). source=estimate|billing_export"
  deletion_protection = true

  schema = jsonencode([
    { name = "recorded_at", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "service", type = "STRING", mode = "NULLABLE" },
    { name = "resource_type", type = "STRING", mode = "NULLABLE" },
    { name = "resource_id", type = "STRING", mode = "NULLABLE" },
    { name = "detail", type = "STRING", mode = "NULLABLE" },
    { name = "region", type = "STRING", mode = "NULLABLE" },
    { name = "usage_qty", type = "FLOAT", mode = "NULLABLE" },
    { name = "usage_unit", type = "STRING", mode = "NULLABLE" },
    { name = "unit_price_usd", type = "FLOAT", mode = "NULLABLE" },
    { name = "est_usd", type = "FLOAT", mode = "NULLABLE" },
    { name = "jpy_per_usd", type = "FLOAT", mode = "NULLABLE" },
    { name = "est_jpy", type = "FLOAT", mode = "NULLABLE" },
    { name = "start_time", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "end_time", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "labels", type = "STRING", mode = "NULLABLE" },
    { name = "run_id", type = "STRING", mode = "NULLABLE" },
    { name = "competition", type = "STRING", mode = "NULLABLE" },
    { name = "source", type = "STRING", mode = "NULLABLE" }
  ])
}

resource "google_service_account" "vertex_runner" {
  account_id   = var.vertex_service_account_id
  display_name = "Kaggle Bronze Vertex runner"
  description  = "Runs Vertex Custom Jobs and writes offline experiment metadata to BigQuery."
}

resource "google_project_iam_member" "vertex_runner_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/artifactregistry.reader",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/storage.objectAdmin",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.vertex_runner.email}"
}

resource "google_service_account_iam_member" "vertex_submitter_act_as" {
  service_account_id = google_service_account.vertex_runner.name
  role               = "roles/iam.serviceAccountUser"
  member             = "user:${var.vertex_submitter_email}"
}

resource "google_billing_budget" "monthly_guardrail" {
  count = var.billing_account_id == "" ? 0 : 1

  billing_account = var.billing_account_id
  display_name    = "kaggle-bronze-gcp monthly guardrail"

  budget_filter {
    calendar_period = "MONTH"
  }

  amount {
    specified_amount {
      currency_code = "JPY"
      units         = tostring(var.budget_amount_jpy)
    }
  }

  threshold_rules {
    threshold_percent = 0.5
  }

  threshold_rules {
    threshold_percent = 1.0
  }
}
