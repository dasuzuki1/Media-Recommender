locals {
  name = "${var.project_name}-${var.environment}"
}

resource "aws_dynamodb_table" "users" {
  name         = "${local.name}-users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"

  attribute {
    name = "user_id"
    type = "N"
  }
}

resource "aws_dynamodb_table" "user_anime" {
  name         = "${local.name}-user-anime"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "anime_id"

  attribute {
    name = "user_id"
    type = "N"
  }
  attribute {
    name = "anime_id"
    type = "N"
  }
}

resource "aws_dynamodb_table" "anime" {
  name         = "${local.name}-anime"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "anime_id"

  attribute {
    name = "anime_id"
    type = "N"
  }
}

resource "aws_dynamodb_table" "recommendations" {
  name         = "${local.name}-recommendations"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "rank"

  attribute {
    name = "user_id"
    type = "N"
  }
  attribute {
    name = "rank"
    type = "N"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}
