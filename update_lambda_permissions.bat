@echo off
echo ========================================
echo Updating Lambda IAM Permissions for Real AWS Scanning
echo ========================================

set ROLE_NAME=upcloud-lambda-role-dev
set REGION=ap-southeast-2

echo.
echo Adding EC2 read permissions to Lambda role...
echo.

aws iam put-role-policy --role-name %ROLE_NAME% --policy-name EC2ReadOnlyPolicy --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"ec2:DescribeInstances\",\"ec2:DescribeVolumes\",\"ec2:DescribeSnapshots\",\"ec2:DescribeAddresses\",\"ec2:DescribeRegions\"],\"Resource\":\"*\"}]}"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Permissions updated successfully!
    echo Lambda can now scan real AWS resources
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ERROR: Failed to update permissions
    echo ========================================
    exit /b 1
)

echo.
pause
