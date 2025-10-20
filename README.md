Rearc Data Quest
========
## Overview
This is Rearc Data Quest that automates the data sync from the bls.gov public dataset and DATA USA API using AWS Lambda, AWS S3 buckets and uses pandas to do data analytics and store the reports back into AWS S3 Bucket.

## Key Features

- **Cloud-based Infrastructure**: Uses Amazon Web Services(AWS S3 bucket and AWS Lambda) 
- **Terraform** - To define, build and manage Infrastructure as Code.

## Table of Contents

 1. [Architecture](#Architecture)
 2. [Project Structure](#Project-Structure)
 3. [Installation Guide](#Installation-Guide)
 4. [Submission](#Submission)

## Architecture
 ![Architecture](/Images/Rearc_Data_Quest.png)

## Project Structure

This project contains the following files and folders:
```
    /REARC_DATA_QUEST
    ├── Access_Key              # To store Access key for AWS account              
    ├── Images                  # Architecture Image
    ├── Lambda  
        ├── bls_sync            # Lamnda handler function for bls data sync
            ├──requirements.txt # list of required packages
        ├── generate_reports    # Lamnda handler function to do data analysis and generate reports
            ├──requirements.txt # list of required packages

    ├── Submissions             # This folder contains the ipynb file and reports
    ├── Terraform               # Terraform .tf files
    ├── .gitignore              # .gitignore file 
    └── README.md               # project overview and instructions
```
## Installation Guide
Prerequisites - you will need the following installed on your local machine
- AWS CLI - install aws cli as per instrustion here https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- Terraform - install Terraform( use hashicorp terraform from your visual studio code) and validate it by running command: terraform --version 
- AWS account 

1. **Clone the respository**:
```
git clone https://github.com/TejalK14/Rearc_Data_Quest.git
```
2. Create AWS account 
3. Create an IAM role and create access key 
4. Download and store access key and secret key
5. Update the Terraform file main.tf. Find "update s3 bucket here" in the main.tf file and update with the S3 bucket names you want to create one for input bucket for the data sync and another for output bucket to store reports. Save the main.tf file and run the following commands one at a time.
```
terraform init
terraform plan
terraform apply
```
6. Now log into your AWS console and you should see the following resources created 
    - S3 bucket for data sync
    - S3 bucket to store output reports
    - Lambda function to extract and store data into S3 bucket
    - Lambda function to do data analysis and output reports
    - Lambda Role (with permission to s3 access)
7. Run lambda function "bls_sync_lambda" to test the Lambda. It should run succesfully and you should be able to view the logs. The S3 data sync bucket should now have the files downloaded from the BLS.gov site and Data USA API into a json file.
8. Run Lambda generate_reports_lambda. This Lambda will read files from data sync S3 buckets perform data analysis and store the output reports into the output S3 bucket.
8. You can now empty the S3 buckets and run the following command to destroy your AWS resources.
```
terraform destroy
```
## Submission
1. Link to S3 bucket 
Input Data Sync Bucket https://us-east-1.console.aws.amazon.com/s3/buckets/bls-public-dataset-sync 
Output Reports Bucket https://us-east-1.console.aws.amazon.com/s3/buckets/bls-output-reports
2. /Lambda/bls_sync/sync_data_lambda.py
3. /Submissions/S01_extract_data_generate_reports.ipynb
4. /Terraform/main.tf


