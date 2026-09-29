.PHONY: deploy

deploy:
	AWS_PROFILE=saharaid AWS_CLIENT_TIMEOUT=10000 SLS_AWS_REQUEST_MAX_RETRIES=0 NODE_OPTIONS='--require $(CURDIR)/scripts/s3-path-style.cjs' sls deploy --region ap-southeast-1 --stage production --verbose
