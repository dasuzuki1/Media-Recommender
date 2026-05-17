data "archive_file" "api" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/api"
  output_path = "${path.module}/build/api.zip"
  excludes    = ["__pycache__", "*.pyc", ".pytest_cache"]
}

resource "aws_lambda_function" "api" {
  function_name    = "${local.name}-api"
  role             = aws_iam_role.api.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.api.output_path
  source_code_hash = data.archive_file.api.output_base64sha256
  timeout          = var.api_timeout_seconds
  memory_size      = var.api_memory_mb

  environment {
    variables = {
      USERS_TABLE           = aws_dynamodb_table.users.name
      USER_ANIME_TABLE      = aws_dynamodb_table.user_anime.name
      ANIME_TABLE           = aws_dynamodb_table.anime.name
      RECOMMENDATIONS_TABLE = aws_dynamodb_table.recommendations.name
      ANILIST_CLIENT_ID     = var.anilist_client_id
      ANILIST_CLIENT_SECRET = var.anilist_client_secret
      SESSION_SECRET        = var.session_secret
      FRONTEND_ORIGIN       = var.frontend_origin
      REDIRECT_URI          = "${aws_apigatewayv2_api.api.api_endpoint}/callback"
    }
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = 14
}
