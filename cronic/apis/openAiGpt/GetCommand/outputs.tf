
output "lambda_gc_arn" {
  description = "The instance ID from the module"
  value       = aws_lambda_function.gc_lambda.arn
}
