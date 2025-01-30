# Directory where Terraform files are located
TERRAFORM_DIR := infra

.PHONY: init plan apply destroy validate install-deps local-run package deploy

# Initialize Terraform
init:
	cd $(TERRAFORM_DIR) && terraform init

# Validate Terraform configuration
validate:
	cd $(TERRAFORM_DIR) && terraform validate

# Show the Terraform execution plan
plan:
	cd $(TERRAFORM_DIR) && terraform plan

# Apply the Terraform changes
apply:
	cd $(TERRAFORM_DIR) && terraform apply -auto-approve

# Destroy all Terraform-managed infrastructure
destroy:
	cd $(TERRAFORM_DIR) && terraform destroy -auto-approve

# Run the project locally before deploying to production
local-run:
		sam build --use-container && \
		cp discord_bot/.env .aws-sam/build/DiscordBotFunction/.env && \
		sam local invoke DiscordBotFunction

# Package the project for deployment
package:
	cd .aws-sam/build/DiscordBotFunction && zip -r ../../../bot.zip . -x "__pycache__/*" "*.pyc" "*.DS_Store" ".env"

# Deploy the project to the cloud
deploy: package
	cd infra && terraform apply -auto-approve && cd ..

# Display outputs
output:
	cd infra && terraform output && cd ..
