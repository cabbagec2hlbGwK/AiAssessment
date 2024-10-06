
output "lambda_gp_arn" {
  description = "The instance ID from the module"
  value       = aws_lambda_function.gp_lambda.arn
}
