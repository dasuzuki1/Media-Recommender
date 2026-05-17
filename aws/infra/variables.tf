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
  default     = "media-recommender"
}

variable "anilist_client_id" {
  type        = string
  description = "AniList OAuth client ID"
  sensitive   = true
}

variable "anilist_client_secret" {
  type        = string
  description = "AniList OAuth client secret"
  sensitive   = true
}

variable "session_secret" {
  type        = string
  description = "Secret used to sign session cookies (32+ random bytes)"
  sensitive   = true
}

variable "frontend_origin" {
  type        = string
  description = "Origin of the frontend (CloudFront URL or custom domain). Used for CORS and OAuth redirect."
}

variable "compute_schedule" {
  type        = string
  description = "EventBridge schedule for batch recommendation compute"
  default     = "rate(1 hour)"
}

variable "compute_memory_mb" {
  type    = number
  default = 1024
}

variable "compute_timeout_seconds" {
  type    = number
  default = 300
}

variable "api_memory_mb" {
  type    = number
  default = 256
}

variable "api_timeout_seconds" {
  type    = number
  default = 10
}

variable "top_n_recommendations" {
  type        = number
  description = "Number of recommendations to precompute per user"
  default     = 20
}

variable "content_weight" {
  type        = number
  description = "Weight for content-based score in hybrid blend (0-1)"
  default     = 0.6
}
