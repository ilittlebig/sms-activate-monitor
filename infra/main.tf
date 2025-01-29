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
    SMS_ACTIVATE_API_KEY = var.sms_activate_api_key,
    CHANNEL_ID           = var.channel_id
  })
}

resource "aws_lambda_function" "discord_bot" {
  function_name    = "discord_bot"
  role             = aws_iam_role.lambda_role.arn
  handler          = "bot.lambda_handler"
  runtime          = "python3.9"
  filename         = "bot.zip"
  source_code_hash = filebase64sha256("bot.zip")
  timeout          = 15

  environment {
    variables = {
      SECRETS_ARN = aws_secretsmanager_secret.discord_bot_secrets.arn
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
