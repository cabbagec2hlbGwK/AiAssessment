
output "lambda_ei_arn" {
  description = "The instance ID from the module"
  value       = aws_lambda_function.ei_lambda.arn
}
