variable "aws_region" {
	description = "AWS region to deploy resources"
	type				= string
	default			= "eu-central-1"
}

variable "discord_token" {
	description = "Discord Bot Token"
	type				= string
	sensitive		= true
}

variable "sms_activate_api_key" {
	description = "SMS-Activate API Key"
	type				= string
	sensitive		= true
}

variable "channel_id" {
	description = "Discord Channel ID"
	type				= string
}
