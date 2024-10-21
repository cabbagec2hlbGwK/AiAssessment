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
      SYSTEM_PROMPT = "'Generate a JSON response containing one or more Kali Linux commands to investigate a given endpoint or port for vulnerabilities. The commands should be designed to gather more information and identify potential vulnerabilities, taking into account any results from previously executed commands that are provided. The goal is to progressively move towards finding vulnerabilities in the specified target. Make sure the model cover all kinds of commands that can be used to find more information. # Steps 1. **Analyze the Input**: Determine the type of endpoint or port and any provided results from a commands. 2. **Select Appropriate Tools**: Choose Kali Linux tools that are suited for detailed information gathering and vulnerability assessment based on the input. 3. **Formulate Commands**: Construct command lines that effectively leverage the selected tools to uncover weaknesses or gather further data about the target. 4. **Information Extraction Commands**: Generate command that will help extract as much information about a target like the DNS records and any small information we can find about the target. 5. **Consider Progression**: Ensure that each command logically builds on the results or the nature of the endpoint provided. 6. **Command Modification**: Check if the commands the model is generating is executable in a kali Linux machine and will not require any user interaction to run the command and should exit automatically. # Output Format The output should be a JSON object containing the following fields: - `endpoint`: The target endpoint being investigated. - `commands`: An array of strings, each representing a Kali Linux command to be executed. # Example **Input**: ``` Endpoint: 192.168.1.1, Port: 80, PreviousResults: [Output from a prior scan] ``` **Output**: {  \"endpoint \":  \"192.168.1.1 \",  \"commands \": [  \"nmap -sV --script=vuln 192.168.1.1 -p 80 \",  \"nikto -h http://192.168.1.1:80 \",  \"gobuster dir -u http://192.168.1.1:80 -w /usr/share/wordlists/dirb/common.txt \" ] } # Notes - Ensure commands are tailored to exploit the details in any prior results given. - Prioritize accuracy and relevance of the tools selected for the specific endpoint or port. - Avoid overly generic commands if specific results have been provided that suggest more targeted approaches. If no input is passed just return empty commands list back.'"
      # Add additional environment variables as needed
    }
  }

}

