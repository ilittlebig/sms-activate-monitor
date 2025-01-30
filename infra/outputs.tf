output "api_gateway_url" {
	description = "The URL of the API Gateway endpoint"
	value				= aws_apigatewayv2_stage.default.invoke_url
}

output "lambda_function_arn" {
	description = "The ARN of the Lambda function"
	value				= aws_lambda_function.discord_bot.arn
}

output "dynamodb_table_name" {
	description = "The name of the DynamoDB table"
	value				= aws_dynamodb_table.discord_monitoring_config.name
}
