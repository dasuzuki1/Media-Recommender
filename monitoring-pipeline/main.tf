locals {
  name = "${var.project_name}-${var.environment}"
}

# --- SNS alert topic ---

resource "aws_sns_topic" "alerts" {
  name = "${local.name}-alerts"
}

resource "aws_sns_topic_subscription" "alerts_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# --- Lambda IAM ---

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${local.name}-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "lambda_publish" {
  statement {
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.alerts.arn]
  }
}

resource "aws_iam_role_policy" "lambda_publish" {
  name   = "${local.name}-publish"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda_publish.json
}

# --- Lambda function ---

data "archive_file" "monitor" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/build/monitor.zip"
}

resource "aws_lambda_function" "monitor" {
  function_name    = "${local.name}-monitor"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  handler          = "monitor.handler"
  filename         = data.archive_file.monitor.output_path
  source_code_hash = data.archive_file.monitor.output_base64sha256
  timeout          = var.lambda_timeout_seconds
  memory_size      = var.lambda_memory_mb

  environment {
    variables = {
      ALERT_TOPIC_ARN = aws_sns_topic.alerts.arn
      TARGETS         = jsonencode(var.monitor_targets)
    }
  }
}

# --- EventBridge schedule ---

resource "aws_cloudwatch_event_rule" "monitor" {
  name                = "${local.name}-schedule"
  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "monitor" {
  rule = aws_cloudwatch_event_rule.monitor.name
  arn  = aws_lambda_function.monitor.arn
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.monitor.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.monitor.arn
}

# --- API Gateway (HTTP API) ---

resource "aws_apigatewayv2_api" "monitor" {
  name          = "${local.name}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "monitor" {
  api_id                 = aws_apigatewayv2_api.monitor.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.monitor.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "monitor" {
  api_id    = aws_apigatewayv2_api.monitor.id
  route_key = "POST /trigger"
  target    = "integrations/${aws_apigatewayv2_integration.monitor.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.monitor.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.monitor.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.monitor.execution_arn}/*/*"
}
