output "lambda_gc_arn" {
  description = "The instance ID from the module"
  value       = aws_api_gateway_deployment.apideploy.invoke_url
}
