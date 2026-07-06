variable "project_id" {
  type    = string
  default = "mlops-dev-a"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "gcs_bucket_name" {
  type    = string
  default = "mlops-dev-a-kaggle-bronze-runs"
}

variable "artifact_registry_repo" {
  type    = string
  default = "kaggle"
}

variable "bq_dataset_id" {
  type    = string
  default = "kaggle_ops"
}

variable "vertex_service_account_id" {
  type    = string
  default = "kaggle-bronze-vertex"
}

variable "vertex_submitter_email" {
  type    = string
  default = "kurokawa81toshifumi@gmail.com"
}

variable "budget_amount_jpy" {
  type    = number
  default = 5000
}

variable "billing_account_id" {
  type        = string
  default     = "010F21-EF2363-604E56"
  description = "Set to enable google_billing_budget. Empty keeps budget alerts disabled."
}
