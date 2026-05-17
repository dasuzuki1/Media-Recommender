output "api_endpoint" {
  value       = aws_apigatewayv2_api.monitor.api_endpoint
  description = "Base URL of the monitor HTTP API"
}

output "lambda_function_name" {
  value = aws_lambda_function.monitor.function_name
}

output "alert_topic_arn" {
  value = aws_sns_topic.alerts.arn
}
