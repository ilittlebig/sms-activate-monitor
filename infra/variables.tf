variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-central-1"
}

variable "discord_token" {
  description = "Discord Bot Token"
  type        = string
  sensitive   = true
}

variable "sms_activate_api_key" {
  description = "SMS-Activate API Key"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "The environment in which resources are deployed (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "discord_public_key" {
  description = "The public key from the Discord developer portal for signature verification"
  type        = string
  sensitive   = true
}

variable "local_testing" {
  description = "Flag to indicate local testing mode"
  type        = string
  default     = "false"
}
