provider "aws" {
  region = "us-west-2"  # Change this to your desired AWS region
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lamda_get_command_role"

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
  name = "lambda_get_command_pollicy"

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

resource "aws_lambda_function" "gc_lambda" {
  function_name = "get_command_orc"
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
      SYSTEM_PROMPT = "Generate a JSON response containing one or more Kali Linux commands to investigate a given endpoint or port for vulnerabilities. The commands should be designed to gather more information and identify potential vulnerabilities, taking into account any results from previously executed commands that are provided. The goal is to progressively move towards finding vulnerabilities in the specified target. Make sure the model cover all kinds of commands that can be used to find more information.\n\n# Steps\n\n1. **Analyze the Input**: Determine the type of endpoint or port and any provided results from a commands.\n2. **Select Appropriate Tools**: Choose Kali Linux tools that are suited for detailed information gathering and vulnerability assessment based on the input.\n3. **Formulate Commands**: Construct command lines that effectively leverage the selected tools to uncover weaknesses or gather further data about the target.\n4. **Consider Progression**: Ensure that each command logically builds on the results or the nature of the endpoint provided.\n\n# Output Format\n\nThe output should be a JSON object containing the following fields:\n- `endpoint`: The target endpoint being investigated.\n- `commands`: An array of strings, each representing a Kali Linux command to be executed.\n\n# Example\n\n**Input**:  \n```\nEndpoint: 192.168.1.1, Port: 80, PreviousResults: [Output from a prior scan]\n```\n\n**Output**:\n{\n  \"endpoint\": \"192.168.1.1\",\n  \"commands\": [\n    \"nmap -sV --script=vuln 192.168.1.1 -p 80\",\n    \"nikto -h http://192.168.1.1:80\",\n    \"gobuster dir -u http://192.168.1.1:80 -w /usr/share/wordlists/dirb/common.txt\"\n  ]\n}\n\n\n# Notes\n\n- Ensure commands are tailored to exploit the details in any prior results given.\n- Prioritize accuracy and relevance of the tools selected for the specific endpoint or port.\n- Avoid overly generic commands if specific results have been provided that suggest more targeted approaches."
      # Add additional environment variables as needed
    }
  }

}

