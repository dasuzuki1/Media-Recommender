# Partial backend config. Bucket, table, and region are supplied at init time:
#   terraform init \
#     -backend-config="bucket=$TF_STATE_BUCKET" \
#     -backend-config="dynamodb_table=$TF_STATE_LOCK_TABLE" \
#     -backend-config="region=$AWS_REGION"
# Or via TF_CLI_ARGS_init (see .envrc.example).
terraform {
  backend "s3" {
    key     = "monitoring-pipeline/terraform.tfstate"
    encrypt = true
  }
}
