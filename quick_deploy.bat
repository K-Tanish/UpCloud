@echo off
echo ========================================
echo UpCloud Quick Deploy
echo ========================================
echo.

REM Set variables
set STAGE=dev
set REGION=ap-southeast-2
set TABLE_NAME=upcloud-findings-%STAGE%
set FUNCTION_NAME=upcloud-api-%STAGE%
set ROLE_NAME=upcloud-lambda-role-%STAGE%
set BUCKET_NAME=upcloud-frontend-%STAGE%-%RANDOM%

echo [1/5] Creating DynamoDB Table...
aws dynamodb create-table --table-name %TABLE_NAME% --attribute-definitions AttributeName=id,AttributeType=S AttributeName=provider,AttributeType=S AttributeName=category,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --global-secondary-indexes "[{\"IndexName\":\"ProviderCategoryIndex\",\"KeySchema\":[{\"AttributeName\":\"provider\",\"KeyType\":\"HASH\"},{\"AttributeName\":\"category\",\"KeyType\":\"RANGE\"}],\"Projection\":{\"ProjectionType\":\"ALL\"}}]" --billing-mode PAY_PER_REQUEST --region %REGION% 2>nul
timeout /t 15 /nobreak >nul
echo   OK DynamoDB created
echo.

echo [2/5] Creating S3 Bucket...
aws s3 mb s3://%BUCKET_NAME% --region %REGION% 2>nul
aws s3 website s3://%BUCKET_NAME% --index-document index.html
aws s3api delete-public-access-block --bucket %BUCKET_NAME% 2>nul
echo {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::%BUCKET_NAME%/*"}]} > policy.json
aws s3api put-bucket-policy --bucket %BUCKET_NAME% --policy file://policy.json
del policy.json
echo   OK S3 bucket created
echo.

echo [3/5] Creating Lambda Function...
echo   Packaging code...
if exist lambda_package.zip del lambda_package.zip
if exist lambda_temp rd /s /q lambda_temp
md lambda_temp
xcopy /E /I /Q lambda_handlers lambda_temp\lambda_handlers
xcopy /E /I /Q cleancloud lambda_temp\cleancloud
xcopy /E /I /Q upcloud lambda_temp\upcloud
powershell -Command "Compress-Archive -Path lambda_temp\* -DestinationPath lambda_package.zip"
rd /s /q lambda_temp
echo   OK Package created

echo   Creating IAM role...
echo {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]} > trust.json
aws iam create-role --role-name %ROLE_NAME% --assume-role-policy-document file://trust.json 2>nul
aws iam attach-role-policy --role-name %ROLE_NAME% --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>nul
echo {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["dynamodb:*"],"Resource":"*"}]} > dynamo.json
aws iam put-role-policy --role-name %ROLE_NAME% --policy-name DynamoAccess --policy-document file://dynamo.json
del trust.json
del dynamo.json
timeout /t 10 /nobreak >nul
echo   OK IAM role created

echo   Creating Lambda function...
for /f "tokens=*" %%a in ('aws iam get-role --role-name %ROLE_NAME% --query Role.Arn --output text') do set ROLE_ARN=%%a
aws lambda create-function --function-name %FUNCTION_NAME% --runtime python3.11 --role %ROLE_ARN% --handler lambda_handlers.api.handler --zip-file fileb://lambda_package.zip --timeout 30 --memory-size 512 --environment "Variables={DYNAMODB_TABLE=%TABLE_NAME%,STAGE=%STAGE%}" --region %REGION% 2>nul
echo   OK Lambda created
echo.

echo [4/5] Creating Function URL...
aws lambda create-function-url-config --function-name %FUNCTION_NAME% --auth-type NONE --cors "AllowOrigins=*,AllowMethods=*,AllowHeaders=*,MaxAge=3600" 2>nul
aws lambda add-permission --function-name %FUNCTION_NAME% --statement-id FunctionURLAllowPublicAccess --action lambda:InvokeFunctionUrl --principal "*" --function-url-auth-type NONE 2>nul
for /f "tokens=*" %%a in ('aws lambda get-function-url-config --function-name %FUNCTION_NAME% --query FunctionUrl --output text') do set API_ENDPOINT=%%a
set API_ENDPOINT=%API_ENDPOINT:~0,-1%
echo   OK Function URL: %API_ENDPOINT%

REM Update frontend config
echo window.UPCLOUD_API_URL = '%API_ENDPOINT%'; > upcloud\static\config.js
echo window.API_BASE_URL = '%API_ENDPOINT%'; >> upcloud\static\config.js
echo console.log('UpCloud API:', window.API_BASE_URL); >> upcloud\static\config.js
echo.

echo [5/5] Deploying Frontend...
aws s3 sync upcloud/static/ s3://%BUCKET_NAME%/ --delete --region %REGION%
echo   OK Frontend deployed

echo   Seeding DynamoDB...
set DYNAMODB_TABLE=%TABLE_NAME%
set AWS_REGION=%REGION%
python scripts\seed_dynamodb.py

set WEBSITE_URL=http://%BUCKET_NAME%.s3-website-%REGION%.amazonaws.com

echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Your Live Application:
echo   Website: %WEBSITE_URL%
echo   API: %API_ENDPOINT%
echo.
echo AWS Resources:
echo   Lambda: %FUNCTION_NAME%
echo   DynamoDB: %TABLE_NAME%
echo   S3: %BUCKET_NAME%
echo   IAM Role: %ROLE_NAME%
echo.
echo Cloud Concepts Demonstrated:
echo   - Serverless Computing (Lambda)
echo   - NoSQL Database (DynamoDB)
echo   - Object Storage (S3)
echo   - Infrastructure as Code
echo   - IAM Security
echo.
echo Save these URLs for your project report!
echo.
pause
