output "vertex_service_account_email" {
  value = google_service_account.vertex_runner.email
}

output "gcs_bucket" {
  value = google_storage_bucket.runs.name
}

output "artifact_registry_repository" {
  value = google_artifact_registry_repository.kaggle.name
}

output "bigquery_dataset" {
  value = google_bigquery_dataset.ops.dataset_id
}
