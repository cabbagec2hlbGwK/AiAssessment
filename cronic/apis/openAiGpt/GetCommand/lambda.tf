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
      SYSTEM_PROMPT = "'Generate a list of Kali Linux commands to extract information about a given target to assist in creating a VAPT report. Given an IP address or domain name as an endpoint, identify and construct appropriate Kali Linux commands that can be used to gather information about the target. The goal is to populate the list of commands that will assist in vulnerability assessment and penetration testing. # Steps 1. **Identify Target**: Understand the endpoint provided (IP address or domain). 2. **Command Suggestion**: Choose relevant Kali Linux commands that fit the context of information gathering or vulnerability assessment. 3. **Command Construction**: Ensure each command includes the proper syntax and specifies any necessary parameters. 4. **Iterate Additional Tools**: Consider using a variety of tools to cover different types of analysis such as network scanning, web application scanning, directory busting, etc. # Output Format - The output should be structured in JSON format with two keys: - ` \"endpoint \"`: The target IP address or domain name. - ` \"commands \"`: An array of command strings suitable for running on Kali Linux to extract information. The resulting JSON should match this structure: ```json {  \"endpoint \":  \"[target] \",  \"commands \": [  \"[command1] \",  \"[command2] \",  \"[command3] \" ] } ``` # Examples ## Input Target:  \"192.168.1.1 \" ## Output ```json {  \"endpoint \":  \"192.168.1.1 \",  \"commands \": [  \"nmap -sV --script=vuln 192.168.1.1 -p 80 \",  \"nikto -h http://192.168.1.1:80 \",  \"gobuster dir -u http://192.168.1.1:80 -w /usr/share/wordlists/dirb/common.txt \" ] } ``` # Notes - Ensure commands are valid and reflect up-to-date tools included in the latest Kali Linux distribution. - Consider the target's network accessibility and what services might be exposed when selecting commands. - Tailor commands for both general reconnaissance and specific information targets may provide. - Adjust port numbers and paths according to real-world scenarios as needed. - And make sure to include the following tools atleast Whois, DNSRecon, Fierce, Nmap, theHarvester, Sublist3r, Shodan CLI, Amass, Censys CLI, Nikto, WhatWeb, Dirb, SSLScan and any other tool which can be usefull to extract more information.'"
      # Add additional environment variables as needed
    }
  }

}

