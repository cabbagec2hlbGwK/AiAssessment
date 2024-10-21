provider "aws" {
  region = "us-west-2"  # Change this to your desired AWS region
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lamda_ext_information_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_exec_policy" {
  name = "lambda_ext_information_pollicy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_exec_policy_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_exec_policy.arn
}

resource "aws_lambda_function" "ei_lambda" {
  function_name = "ext_information_orc"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "lambda_function.lambda_handeler" 
  runtime       = "python3.10"                    
  timeout       = 500

  # Path to your ZIP file
  filename         = "${path.module}/lambda_function.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_function.zip")

  environment {
    variables = {
      OPENAI_API_KEY = var.OPEN_AI_KEY
      MASTER_ENDPOINT = "value2"
      # Add additional environment variables as needed
    }
  }

}

