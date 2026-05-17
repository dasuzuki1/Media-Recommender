terraform {
  backend "s3" {
    key     = "media-recommender/terraform.tfstate"
    encrypt = true
  }
}
