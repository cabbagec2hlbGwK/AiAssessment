provider "aws" {
  region = "us-west-2"  # Change this to your desired AWS region
}

resource "aws_iam_role" "lambda_exec_gp_role" {
  name = "lamda_get_packages_role"

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

resource "aws_iam_policy" "lambda_exec_gp_policy" {
  name = "lambda_get_packages_pollicy"

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

resource "aws_iam_role_policy_attachment" "lambda_exec_policy_attach_gp" {
  role       = aws_iam_role.lambda_exec_gp_role.name
  policy_arn = aws_iam_policy.lambda_exec_gp_policy.arn
}

resource "aws_lambda_function" "gp_lambda" {
  function_name = "get_packages_orc"
  role          = aws_iam_role.lambda_exec_gp_role.arn
  handler       = "lambda_function.lambda_handeler" 
  runtime       = "python3.10"                    
  timeout       = 500

  # Path to your ZIP file
  filename         = "${path.module}/lambda_function.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_function.zip")

  environment {
    variables = {
      OPENAI_API_KEY = var.OPEN_AI_KEY
      SYSTEM_PROMPT = "Create a model that can identify the necessary packages to install via `apt` for executing a given bash command or task, tailored for Kali Linux.\n\nThe model will receive a bash command or task and should output a JSON object listing all the required packages that need to be installed using `apt`. Ensure compatibility and support for Kali Linux in the backend.\n\n# Steps\n\n1. **Input Parsing**: Receive and parse the given bash command or task.\n2. **Requirement Analysis**: Determine which packages are necessary to execute the command on a Kali Linux system.\n3. **Package Identification**: Identify the exact package names that provide the required functionalities.\n4. **Output Construction**: Format the result in a JSON object containing the relevant package names.\n\n# Output Format\n\n- The output should be in JSON format.\n- Include key-value pairs, with the key as `\"packages\"` and value as a list of package names.\n  \nExample:\n```json\n{\n  \"packages\": [\"package1\", \"package2\"]\n}\n```\n\n# Examples\n\n**Example 1:**\n- **Input:** `lsblk`\n- **Reasoning:**\n  - `lsblk` is a command for listing block devices.\n  - On Kali Linux, `lsblk` is provided by the `util-linux` package.\n- **Output:**\n  ```json\n  {\n    \"packages\": [\"util-linux\"]\n  }\n  ```\n\n**Example 2:**\n- **Input:** `nmap -sP`\n- **Reasoning:**\n  - `nmap` is a network scanning tool.\n  - It requires the `nmap` package to be available on the system.\n- **Output:**\n  ```json\n  {\n    \"packages\": [\"nmap\"]\n  }\n  ```\n\n# Notes\n\n- Ensure the package list is specific to Kali Linux repositories and aligns with its package management system.\n- Handle edge cases where the command exists in multiple packages by selecting the most common or recommended package.\nalso just give the json no markdown formating\n"
      # Add additional environment variables as needed
    }
  }

}
