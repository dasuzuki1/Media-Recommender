data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# --- API Lambda role ---

resource "aws_iam_role" "api" {
  name               = "${local.name}-api-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "api_basic" {
  role       = aws_iam_role.api.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "api_dynamodb" {
  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:Query",
      "dynamodb:BatchWriteItem",
      "dynamodb:BatchGetItem",
    ]
    resources = [
      aws_dynamodb_table.users.arn,
      aws_dynamodb_table.user_anime.arn,
      aws_dynamodb_table.anime.arn,
      aws_dynamodb_table.recommendations.arn,
    ]
  }
}

resource "aws_iam_role_policy" "api_dynamodb" {
  name   = "${local.name}-api-dynamodb"
  role   = aws_iam_role.api.id
  policy = data.aws_iam_policy_document.api_dynamodb.json
}

# --- Compute Lambda role ---

resource "aws_iam_role" "compute" {
  name               = "${local.name}-compute-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "compute_basic" {
  role       = aws_iam_role.compute.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "compute_dynamodb" {
  statement {
    actions = [
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:GetItem",
      "dynamodb:BatchGetItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:PutItem",
    ]
    resources = [
      aws_dynamodb_table.users.arn,
      aws_dynamodb_table.user_anime.arn,
      aws_dynamodb_table.anime.arn,
      aws_dynamodb_table.recommendations.arn,
    ]
  }
}

resource "aws_iam_role_policy" "compute_dynamodb" {
  name   = "${local.name}-compute-dynamodb"
  role   = aws_iam_role.compute.id
  policy = data.aws_iam_policy_document.compute_dynamodb.json
}
