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

# Install all dependencies needed to run the application
install-deps:
	pip3 install -r discord_bot/requirements.txt --target discord_bot/vendor/ --upgrade

# Run the project locally before deploying to production
local-run:
	sam local invoke DiscordBotFunction

# Package the project for deployment
package:
	cd discord_bot && zip -r ../bot.zip . && cd ..

# Deploy the project to the cloud
deploy: package
	terraform apply -auto-approve
