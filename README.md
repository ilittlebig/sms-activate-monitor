# SMS-Activate Monitor
A serverless Discord bot that monitors GMX number availability on SMS-Activate and sends real-time alerts. Runs on AWS Lambda with Terraform automation. 🚀

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Usage](#usage)
- [Commands](#commands)
- [Monitoring and Logging](#monitoring-and-logging)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction
This application is a serverless Discord bot designed to monitor the availability of GMX numbers on the SMS-Activate platform. Upon detecting changes in availability, the bot sends real-time alerts to designated Discord channels. The solution leverages AWS Lambda for serverless execution and is fully automated using Terraform for infrastructure management.

## Features
- **Real-Time Monitoring**: Continuously checks the availability of GMX numbers on SMS-Activate.
- **Instant Notifications**: Sends immediate alerts to specified Discord channels upon detecting changes.
- **Serverless Architecture**: Utilizes AWS Lambda to ensure scalability and cost-effectiveness.
- **Infrastructure as Code**: Employs Terraform for consistent and repeatable infrastructure deployment.
- **Configurable Thresholds**: Allows users to set custom thresholds for stock change notifications.

## Architecture Overview
The SMS-Activate Monitor is built upon a serverless architecture, primarily utilizing AWS services:
- **AWS Lambda**: Executes the bot’s code in response to events.
- **Amazon API Gateway**: Serves as the HTTP endpoint for Discord interactions.
- **Amazon DynamoDB**: Stores configuration data for each Discord guild.
- **AWS CloudWatch Events**: Triggers the Lambda function at regular intervals for monitoring tasks.
- **AWS Secrets Manager**: Securely stores sensitive information such as API keys and tokens.

The infrastructure is defined and managed using Terraform, ensuring a consistent and reproducible deployment process.

## Prerequisites
Before setting up the SMS-Activate Monitor, ensure you have the following:
- **AWS Account**: Access to an AWS account with permissions to create the necessary resources.
- **Discord Application**: A registered Discord application with a bot token. You can create one through the Discord Developer Portal.
- **SMS-Activate API Key**: An active API key from SMS-Activate.
- **Terraform**: Installed on your local machine. Follow the official installation guide if needed.
- **Python 3.9**: Ensure Python 3.9 is installed, as the Lambda function is built for this runtime.

## Installation
**1. Clone the Repository:**
  ```bash
  git clone https://github.com/ilittlebig/sms-activate-monitor.git
  cd sms-activate-monitor
  ```

**2. Set Up a Python Virtual Environment:**
  ```bash
  python3.9 -m venv venv
  source venv/bin/activate
  ```

**3. Install Python Dependencies:**
  ```bash
  pip install -r discord_bot/requirements.txt
  ```

**4. Initialize Terraform:**
  From the root directory:
  ```bash
  make init
  ```

## Configuration
**1. Environment Variables:**
Create a .env file in the root directory with the following content:
```bash
DISCORD_TOKEN=your_discord_bot_token
DISCORD_APPLICATION_ID=your_discord_application_id
SMS_ACTIVATE_API_KEY=your_sms_activate_api_key
DISCORD_PUBLIC_KEY=your_discord_public_key
LOCAL_TESTING=true
```

**2. Terraform Variables:**
Update the `infra/variables.tf` file with appropriate values for your environment. Ensure that the `aws_region` and other variables are set correctly.

## Deployment
**1. Run the Application Locally:**
Once you’ve verified the application locally, prepare it for deployment by running:
```
make local-run
```
This command will set up and run the application in your local environment, allowing you to test and ensure everything functions as expected before deployment.

**2. Package the Application for Deployment:**
From the root directory:
```
make package
```
This command will create the necessary deployment package, typically a ZIP file containing your application code and dependencies, ready to be uploaded to AWS Lambda

**3. Deploy with Terraform:**
From the root directory:
```bash
make deploy
```
This command will utilize Terraform to provision the required AWS resources and deploy your packaged application.

**4. Register Discord Commands:**
After deploying the application, initialize the bot’s commands by running:
```bash
python3.9 discord_bot/register_commands.py
```
This script registers the bot’s commands with Discord, making them available for use in your server. Ensure that this step is performed after the deployment process to finalize the bot’s setup.

## Usage
Once deployed, the bot will automatically monitor GMX number availability on SMS-Activate and send alerts to the configured Discord channels. You can interact with the bot using the following commands:

### Commands
- `/monitor [country]`: Set the country to monitor for GMX number availability.
- `/setchannel [channel]`: Designate the Discord channel for receiving alerts.
- `/setthreshold [threshold]`: Define the minimum stock increase required to trigger an alert.

> **Note**: Ensure that you have the necessary permissions to use these commands. Typically, only users with administrative privileges can configure the bot.

### Monitoring and Logging
The application leverages AWS CloudWatch for logging and monitoring. To view logs:
1. Navigate to the `AWS CloudWatch Console`.
2. Select Logs from the sidebar.
3. Locate the log group associated with your Lambda function (e.g., `/aws/lambda/discord_bot`).

Here, you can monitor the bot’s activity and troubleshoot any issues that arise.

Security Considerations
- **API Keys and Tokens**: Store all sensitive information securely using AWS Secrets Manager. Avoid hardcoding credentials in your codebase.
- **IAM Roles and Policies**: Assign the least privilege necessary to AWS IAM roles and policies associated with the Lambda function.
- **Discord Permissions**: Ensure the bot has appropriate permissions within your Discord server to function correctly.

## Contributing
We welcome contributions to the SMS-Activate Monitor project. To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Implement your changes and ensure they are well-tested.
4. Submit a pull request with a detailed description of your changes.

Please adhere to the project’s coding standards and guidelines.

## License
This project is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for more details.

## Acknowledgements
We extend our gratitude to the developers and communities of the open-source projects that made this application possible. Special thanks to:
- **Discord.py**: A Python wrapper for the Discord API.
- **Terraform**: Infrastructure as Code tool by HashiCorp.
- **AWS Lambda**: Serverless compute service by Amazon Web Services.

For any questions or support, please open an issue in the GitHub repository or contact the maintainers directly.
