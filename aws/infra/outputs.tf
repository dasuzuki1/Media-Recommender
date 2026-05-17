output "api_url" {
  description = "Public HTTPS URL of the API Gateway"
  value       = aws_apigatewayv2_api.api.api_endpoint
}

output "frontend_url" {
  description = "Public HTTPS URL of the CloudFront-fronted dashboard"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "frontend_bucket" {
  description = "S3 bucket name to sync the built frontend into"
  value       = aws_s3_bucket.frontend.id
}

output "users_table" {
  value = aws_dynamodb_table.users.name
}

output "anime_table" {
  description = "Name of the Anime catalog table (target for bootstrap_anime_table.py)"
  value       = aws_dynamodb_table.anime.name
}

output "user_anime_table" {
  value = aws_dynamodb_table.user_anime.name
}

output "recommendations_table" {
  value = aws_dynamodb_table.recommendations.name
}

output "compute_function_name" {
  description = "Compute Lambda name (invoke manually with: aws lambda invoke --function-name ...)"
  value       = aws_lambda_function.compute.function_name
}
