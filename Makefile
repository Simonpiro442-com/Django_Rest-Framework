.PHONY: install shell activate clean help run run-cloud setup-env

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using Poetry
	poetry install --no-root

activate: ## Activate Poetry environment (in current shell)
	@echo "To activate the Poetry environment, run:"
	@echo "source $$(poetry env info --path)/bin/activate"

shell: ## Install shell plugin and activate Poetry shell (deprecated)
	poetry self add poetry-plugin-shell
	poetry shell

setup-env: ## Create a sample .env file (if it doesn't exist)
	@if [ ! -f .env ]; then \
		echo "Creating sample .env file..."; \
		echo "# Uncomment and set GCS_BUCKET_NAME to use Google Cloud Storage" > .env; \
		echo "# GCS_BUCKET_NAME=your-bucket-name" >> .env; \
		echo "# If GCS_BUCKET_NAME is not set, files will be saved locally in the 'output' directory" >> .env; \
		echo ".env file created successfully!"; \
	else \
		echo ".env file already exists. Skipping."; \
	fi

run: ## Run the scraper locally (without Flask dependency)
	@echo "Running the scraper locally..."
	@echo "If GCS_BUCKET_NAME is not set in .env, files will be saved to the 'output' directory"
	python3 local_run.py

run-cloud: ## Run with Flask (for Cloud Function testing)
	@echo "Running with Flask (for Cloud Function testing)..."
	@echo "This requires Flask to be installed"
	python3 main.py

clean: ## Clean up cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.DEFAULT_GOAL := help 