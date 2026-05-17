variable "aws_region" {
  type        = string
  description = "AWS region for all resources"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, prod)"
}

variable "project_name" {
  type        = string
  description = "Project name used to prefix resource names"
  default     = "monitoring-pipeline"
}

variable "alert_email" {
  type        = string
  description = "Email address subscribed to the alert SNS topic"
}

variable "monitor_targets" {
  type        = list(string)
  description = "URLs the monitor Lambda checks on each run"
  default     = []
}

variable "schedule_expression" {
  type        = string
  description = "EventBridge schedule for the monitor Lambda"
  default     = "rate(5 minutes)"
}

variable "lambda_timeout_seconds" {
  type    = number
  default = 30
}

variable "lambda_memory_mb" {
  type    = number
  default = 128
}
