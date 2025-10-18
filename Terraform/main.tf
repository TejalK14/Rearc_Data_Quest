terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.15.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Create an S3 bucket for bls dataset
resource "aws_s3_bucket" "bls_dataset" {
  bucket = "bls-public-dataset-sync" # update s3 bucket here
}

# Create an S3 bucket for output reports
resource "aws_s3_bucket" "bls_reports" {
  bucket = "bls-output-reports" # update s3 bucket here
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "bls_sync_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# Lambda Function - to sync bls data
resource "aws_lambda_function" "bls_sync" {
  function_name = "bls_sync_lambda"
  handler       = "sync_data_lambda.lambda_handler"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_role.arn

  timeout          = 30       # seconds
  memory_size      = 256      # MB

  filename         = "../Lambda/bls_sync.zip"  # zip of Python code + dependencies (requests, bs4)
  source_code_hash = filebase64sha256("../Lambda/bls_sync.zip")

  environment {
    variables = {
      S3_BUCKET = "bls-public-dataset-sync" # update s3 bucket here
      BLS_URL   = "https://download.bls.gov/pub/time.series/pr/"
    }
  }
}

# Lambda Function to generate reports
resource "aws_lambda_function" "generate_reports" {
  function_name = "generate_reports_lambda"
  handler       = "generate_reports_lambda.lambda_handler"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_role.arn

  timeout          = 30       # seconds
  memory_size      = 256      # MB

  layers = [
    "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python311:1"
  ]

  filename         = "../Lambda/generate_reports.zip"  # zip of Python code + dependencies
  source_code_hash = filebase64sha256("../Lambda/generate_reports.zip")

  environment {
    variables = {
      INPUT_BUCKET = "bls-public-dataset-sync" # update s3 bucket here
      OUTPUT_BUCKET   = "bls-output-reports" # update s3 bucket here
    }
  }
}
