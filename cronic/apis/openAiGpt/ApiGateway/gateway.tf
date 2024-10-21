
# API Gateway
resource "aws_api_gateway_rest_api" "example" {
  name        = "AI_PENTEST"
  description = "API Gateway with two POST routes"
}

data "aws_caller_identity" "current" {}

# Get Command Resource
resource "aws_api_gateway_resource" "get_command" {
  rest_api_id = aws_api_gateway_rest_api.example.id
  parent_id   = aws_api_gateway_rest_api.example.root_resource_id
  path_part   = "get_command"
}
resource "aws_api_gateway_resource" "ext_information" {
  rest_api_id = aws_api_gateway_rest_api.example.id
  parent_id   = aws_api_gateway_rest_api.example.root_resource_id
  path_part   = "ext_information"
}

# Get Packages Resource
resource "aws_api_gateway_resource" "get_packages" {
  rest_api_id = aws_api_gateway_rest_api.example.id
  parent_id   = aws_api_gateway_rest_api.example.root_resource_id
  path_part   = "get_packages"
}

# Method for Get Command
resource "aws_api_gateway_method" "get_command" {
  rest_api_id   = aws_api_gateway_rest_api.example.id
  resource_id   = aws_api_gateway_resource.get_command.id
  http_method   = "POST"
  authorization = "NONE"
}

# Method for Get Packages
resource "aws_api_gateway_method" "get_packages" {
  rest_api_id   = aws_api_gateway_rest_api.example.id
  resource_id   = aws_api_gateway_resource.get_packages.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_method" "ext_information" {
  rest_api_id   = aws_api_gateway_rest_api.example.id
  resource_id   = aws_api_gateway_resource.ext_information.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integration for Get Command
resource "aws_api_gateway_integration" "get_command" {
  rest_api_id             = aws_api_gateway_rest_api.example.id
  resource_id             = aws_api_gateway_resource.get_command.id
  http_method             = aws_api_gateway_method.get_command.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.lambda_gc_arn}/invocations"
}

# Integration for Get Packages
resource "aws_api_gateway_integration" "get_packages" {
  rest_api_id             = aws_api_gateway_rest_api.example.id
  resource_id             = aws_api_gateway_resource.get_packages.id
  http_method             = aws_api_gateway_method.get_packages.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.lambda_gp_arn}/invocations"
}
resource "aws_api_gateway_integration" "ext_information" {
  rest_api_id             = aws_api_gateway_rest_api.example.id
  resource_id             = aws_api_gateway_resource.ext_information.id
  http_method             = aws_api_gateway_method.ext_information.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.lambda_ei_arn}/invocations"
}
# Permissions for Lambda Functions
# Permissions for Lambda Function: Get Command
resource "aws_lambda_permission" "apigateway_get_command" {
  statement_id  = "AllowInvokeFromAPIGatewayGetCommand"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_gc_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.example.id}/*/POST/get_command"
}

# Permissions for Lambda Function: Get Packages
resource "aws_lambda_permission" "apigateway_get_packages" {
  statement_id  = "AllowInvokeFromAPIGatewayGetPackages"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_gp_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.example.id}/*/POST/get_packages"
}
resource "aws_lambda_permission" "apigateway_ext_information" {
  statement_id  = "AllowInvokeFromAPIGatewayGetPackages"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_ei_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.example.id}/*/POST/ext_information"
}

# Deployment
resource "aws_api_gateway_deployment" "apideploy" {
  depends_on = [
    aws_api_gateway_integration.get_command,
    aws_api_gateway_integration.get_packages,
    aws_api_gateway_integration.ext_information
  ]
  rest_api_id = aws_api_gateway_rest_api.example.id
  stage_name  = "prod"
}
