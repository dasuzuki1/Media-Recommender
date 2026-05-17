data "archive_file" "compute" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/compute"
  output_path = "${path.module}/build/compute.zip"
  excludes    = ["__pycache__", "*.pyc", ".pytest_cache"]
}

# scikit-learn + numpy + pandas exceed the 250MB unzipped limit when packaged
# inline. The AWS-managed SciPy layer ships numpy + scipy + scikit-learn;
# pandas is pulled in as a small dependency in requirements.txt and bundled
# via the archive. For a production setup, pre-build a custom layer.
resource "aws_lambda_function" "compute" {
  function_name    = "${local.name}-compute"
  role             = aws_iam_role.compute.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.compute.output_path
  source_code_hash = data.archive_file.compute.output_base64sha256
  timeout          = var.compute_timeout_seconds
  memory_size      = var.compute_memory_mb

  environment {
    variables = {
      USERS_TABLE           = aws_dynamodb_table.users.name
      USER_ANIME_TABLE      = aws_dynamodb_table.user_anime.name
      ANIME_TABLE           = aws_dynamodb_table.anime.name
      RECOMMENDATIONS_TABLE = aws_dynamodb_table.recommendations.name
      TOP_N                 = tostring(var.top_n_recommendations)
      CONTENT_WEIGHT        = tostring(var.content_weight)
    }
  }
}

resource "aws_cloudwatch_log_group" "compute" {
  name              = "/aws/lambda/${aws_lambda_function.compute.function_name}"
  retention_in_days = 14
}

resource "aws_cloudwatch_event_rule" "compute_schedule" {
  name                = "${local.name}-compute-schedule"
  schedule_expression = var.compute_schedule
}

resource "aws_cloudwatch_event_target" "compute" {
  rule = aws_cloudwatch_event_rule.compute_schedule.name
  arn  = aws_lambda_function.compute.arn
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.compute.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.compute_schedule.arn
}
