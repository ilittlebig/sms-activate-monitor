resource "aws_apigatewayv2_api" "discord_api" {
  name          = "DiscordBotAPI"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.discord_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = aws_apigatewayv2_api.discord_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.discord_bot.invoke_arn
}

resource "aws_apigatewayv2_route" "discord_command" {
  api_id    = aws_apigatewayv2_api.discord_api.id
  route_key = "POST /"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_lambda_permission" "apigw" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.discord_bot.function_name
  principal     = "apigateway.amazonaws.com"
}

resource "aws_dynamodb_table" "discord_monitoring_config" {
  name           = "DiscordMonitoringConfig"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "GuildID"

  attribute {
    name = "GuildID"
    type = "S"
  }

  tags = {
    Environment = var.environment
  }
}

resource "aws_iam_policy" "dynamodb_policy" {
  name        = "lambda_dynamodb_policy"
  description = "Policy for Lambda to access DynamoDB"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Scan"
        ],
        Resource = aws_dynamodb_table.discord_monitoring_config.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.dynamodb_policy.arn
}

resource "aws_iam_role" "lambda_role" {
  name = "discord_bot_lambda_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "discord_bot_lambda_policy"
  description = "Policy for Lambda to access logs and secrets"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/discord_bot:*"
      },
      {
        Effect   = "Allow",
        Action   = [
          "secretsmanager:GetSecretValue"
        ],
        Resource = aws_secretsmanager_secret.discord_bot_secrets.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_secretsmanager_secret" "discord_bot_secrets" {
  name = "discord_bot_secrets"
}

resource "aws_secretsmanager_secret_version" "discord_bot_secrets_version" {
  secret_id     = aws_secretsmanager_secret.discord_bot_secrets.id
  secret_string = jsonencode({
    DISCORD_TOKEN        = var.discord_token,
    SMS_ACTIVATE_API_KEY = var.sms_activate_api_key
  })
}

resource "aws_lambda_function" "discord_bot" {
  function_name    = "discord_bot"
  role             = aws_iam_role.lambda_role.arn
  handler          = "bot.lambda_handler"
  runtime          = "python3.9"
  filename         = "../bot.zip"
  source_code_hash = filebase64sha256("../bot.zip")
  timeout          = 15

  environment {
    variables = {
      SECRETS_ARN        = aws_secretsmanager_secret.discord_bot_secrets.arn,
      DISCORD_PUBLIC_KEY = var.discord_public_key,
      LOCAL_TESTING      = var.local_testing
    }
  }
}

resource "aws_cloudwatch_event_rule" "every_10_minutes" {
  name                = "every_10_minutes"
  schedule_expression = "rate(10 minutes)"
}

resource "aws_cloudwatch_event_target" "trigger_lambda" {
  rule      = aws_cloudwatch_event_rule.every_10_minutes.name
  target_id = "lambda"
  arn       = aws_lambda_function.discord_bot.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.discord_bot.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_10_minutes.arn
}
