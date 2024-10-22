provider "aws" {
  region = "us-west-2"
}

module "get_packages" {
  source      = "./GetPackages"
  OPEN_AI_KEY = var.OPEN_AI_KEY
}


module "get_command" {
  source      = "./GetCommand"
  OPEN_AI_KEY = var.OPEN_AI_KEY
}
module "ext_information" {
  source      = "./ExtInformation"
  OPEN_AI_KEY = var.OPEN_AI_KEY
}

module "api_gateway" {
  source        = "./ApiGateway"
  aws_region    = "us-west-2"
  lambda_gc_arn = module.get_command.lambda_gc_arn
  lambda_gp_arn = module.get_packages.lambda_gp_arn
  lambda_ei_arn = module.ext_information.lambda_ei_arn
  depends_on = [ 
    module.get_command,
    module.get_packages,
    module.ext_information
  ]

}


resource "aws_ssm_parameter" "my_api_endpoint" {
  name  = "openaiEndpoint"
  type  = "String"
  value = module.api_gateway.lambda_gc_arn


  tags = {
    "Environment" = "prod"
    "Service"     = "AiAssesment"
  }
}
