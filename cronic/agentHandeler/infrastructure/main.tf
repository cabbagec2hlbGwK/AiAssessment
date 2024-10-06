provider "aws" {
  region = "us-west-2"
}

# VPC Setup
resource "aws_vpc" "aiassessment_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "aiassessment-vpc"
  }
}

resource "aws_subnet" "aiassessment_public_subnet_1" {
  vpc_id                  = aws_vpc.aiassessment_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-west-2a"
  map_public_ip_on_launch = true
  tags = {
    Name = "aiassessment-public-subnet-1"
  }
}

resource "aws_subnet" "aiassessment_private_subnet_1" {
  vpc_id            = aws_vpc.aiassessment_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-west-2a"
  tags = {
    Name = "aiassessment-private-subnet-1"
  }
}

resource "aws_subnet" "aiassessment_public_subnet_2" {
  vpc_id                  = aws_vpc.aiassessment_vpc.id
  cidr_block              = "10.0.3.0/24"
  availability_zone       = "us-west-2b"
  map_public_ip_on_launch = true
  tags = {
    Name = "aiassessment-public-subnet-2"
  }
}

resource "aws_subnet" "aiassessment_private_subnet_2" {
  vpc_id            = aws_vpc.aiassessment_vpc.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "us-west-2b"
  tags = {
    Name = "aiassessment-private-subnet-2"
  }
}

resource "aws_internet_gateway" "aiassessment_igw" {
  vpc_id = aws_vpc.aiassessment_vpc.id
  tags = {
    Name = "aiassessment-internet-gateway"
  }
}

resource "aws_route_table" "aiassessment_public_rt" {
  vpc_id = aws_vpc.aiassessment_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.aiassessment_igw.id
  }
  tags = {
    Name = "aiassessment-public-route-table"
  }
}

resource "aws_route_table_association" "aiassessment_public_rta_1" {
  subnet_id      = aws_subnet.aiassessment_public_subnet_1.id
  route_table_id = aws_route_table.aiassessment_public_rt.id
}

resource "aws_route_table_association" "aiassessment_public_rta_2" {
  subnet_id      = aws_subnet.aiassessment_public_subnet_2.id
  route_table_id = aws_route_table.aiassessment_public_rt.id
}

# Security Groups
resource "aws_security_group" "aiassessment_rds_sg" {
  name   = "aiassessment-rds-sg"
  vpc_id = aws_vpc.aiassessment_vpc.id

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.aiassessment_public_subnet_1.cidr_block, aws_subnet.aiassessment_public_subnet_2.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "aiassessment-rds-sg"
  }
}

resource "aws_security_group" "aiassessment_ec2_sg" {
  name   = "aiassessment-ec2-sg"
  vpc_id = aws_vpc.aiassessment_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "aiassessment-ec2-sg"
  }
}

# SSM Parameter Store
resource "aws_ssm_parameter" "aiassessment_rds_creds" {
  name  = "/aiassessment/rds/mysql"
  type  = "SecureString"
  value = jsonencode({
    username = "admin"
    password = "password123"  # Ensure this is a secure password
    dbname   = "aiassessment_db"
  })

  tags = {
    Name = "aiassessment-rds-creds"
  }
}

# IAM Role & Policy for EC2 to access SSM
resource "aws_iam_role" "aiassessment_ec2_role" {
  name               = "aiassessment-ec2-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "ssm_access_policy" {
  name        = "aiassessment-ssm-access-policy"
  description = "Policy allowing EC2 instances to access values in SSM Parameter Store"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ssm:GetParameter",
        "ssm:GetParameterHistory"
      ]
      Resource = "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/aiassessment/rds/mysql"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_policy_attachment" {
  role       = aws_iam_role.aiassessment_ec2_role.name
  policy_arn = aws_iam_policy.ssm_access_policy.arn
}

resource "aws_iam_instance_profile" "aiassessment_ec2_profile" {
  role = aws_iam_role.aiassessment_ec2_role.name
}

# RDS MySQL Instance
resource "aws_db_subnet_group" "aiassessment_rds_subnet_group" {
  name       = "aiassessment-rds-subnet-group"
  subnet_ids = [
    aws_subnet.aiassessment_private_subnet_1.id,
    aws_subnet.aiassessment_private_subnet_2.id,
  ]

  tags = {
    Name = "aiassessment-rds-subnet-group"
  }
}

resource "aws_db_instance" "aiassessment_mysql" {
  identifier         = "aiassessment-mysql"
  allocated_storage  = 20
  storage_type       = "gp2"
  engine             = "mysql"
  engine_version     = "8.0.35"  # Update to a supported version, the latest available
  instance_class     = "db.c6gd.large"  # Change instance class to a supported type
  username           = "admin"
  password           = "password123"  # Initially used for setup, should sync with SSM Parameter
  vpc_security_group_ids = [aws_security_group.aiassessment_rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.aiassessment_rds_subnet_group.name
  skip_final_snapshot    = true
  publicly_accessible    = false

  tags = {
    Name = "aiassessment-mysql-instance"
  }
}

# EC2 Instance
resource "aws_instance" "aiassessment_ec2" {
  ami           = "ami-04dd23e62ed049936" # Example: Ubuntu Server 20.04 LTS (Replace with a valid AMI ID for your region)
  instance_type = "t2.small"
  subnet_id     = aws_subnet.aiassessment_public_subnet_1.id
  vpc_security_group_ids = [aws_security_group.aiassessment_ec2_sg.id]
  iam_instance_profile = aws_iam_instance_profile.aiassessment_ec2_profile.name


  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y mysql-client jq awscli

    REGION="us-west-2"

    # Fetch secret from SSM Parameter Store
    secret=$(aws ssm get-parameter --region $REGION --name "/aiassessment/rds/mysql" --with-decryption --query "Parameter.Value" --output text)
    db_username=$(echo $secret | jq -r '.username')
    db_password=$(echo $secret | jq -r '.password')
    db_name=$(echo $secret | jq -r '.dbname')
    db_endpoint="${aws_db_instance.aiassessment_mysql.endpoint}"

    mysql -h $db_endpoint -u$db_username -p$db_password <<EOSQL
      CREATE DATABASE IF NOT EXISTS $db_name;
      USE $db_name;
      CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        score INT,
        PRIMARY KEY (id)
      );
    EOSQL
  EOF

  tags = {
    Name = "aiassessment-app-server"
  }
}

data "aws_caller_identity" "current" {}
variable "aws_region" {
  description = "The AWS region to create resources in."
  default     = "us-west-2"
}

