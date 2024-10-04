provider "aws" {
  region = "us-west-2"
}

module "get_packages" {
  source = "./GetPackages"
  OPEN_AI_KEY= var.OPEN_AI_KEY
}


module "get_command" {
  source = "./GetCommand"
  OPEN_AI_KEY= var.OPEN_AI_KEY
}
