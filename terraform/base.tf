data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/../lambda/contador.py"
  output_path = "${path.module}/contador.zip"
}

resource "aws_iam_role" "counter" {
  name = "ej7-contador-lambda-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}
resource "aws_iam_role_policy_attachment" "logs" {
  role       = aws_iam_role.counter.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_dynamodb_table" "ireland" {
  provider     = aws.ireland
  name         = "ej7-mensajes-irlanda"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  attribute {
    name = "id"
    type = "S"
  }
  tags = {
    Project = "IFCD0078-Ejercicio7"
  }
}
resource "aws_dynamodb_table" "virginia" {
  provider     = aws.virginia
  name         = "ej7-mensajes-virginia"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  attribute {
    name = "id"
    type = "S"
  }
  tags = {
    Project = "IFCD0078-Ejercicio7"
  }
}
resource "aws_dynamodb_table" "tokyo" {
  provider     = aws.tokyo
  name         = "ej7-mensajes-tokio"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  attribute {
    name = "id"
    type = "S"
  }
  tags = {
    Project = "IFCD0078-Ejercicio7"
  }
}

resource "aws_iam_role_policy" "read_tables" {
  name = "ej7-read-regional-tables"
  role = aws_iam_role.counter.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:Scan"]
      Resource = [aws_dynamodb_table.ireland.arn, aws_dynamodb_table.virginia.arn, aws_dynamodb_table.tokyo.arn]
    }]
  })
}

resource "aws_cloudwatch_log_group" "ireland" {
  provider          = aws.ireland
  name              = "/aws/lambda/ej7-hashtags-irlanda"
  retention_in_days = 1
}
resource "aws_cloudwatch_log_group" "virginia" {
  provider          = aws.virginia
  name              = "/aws/lambda/ej7-hashtags-virginia"
  retention_in_days = 1
}
resource "aws_cloudwatch_log_group" "tokyo" {
  provider          = aws.tokyo
  name              = "/aws/lambda/ej7-hashtags-tokio"
  retention_in_days = 1
}

resource "aws_lambda_function" "ireland" {
  provider         = aws.ireland
  function_name    = "ej7-hashtags-irlanda"
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  role             = aws_iam_role.counter.arn
  handler          = "contador.handler"
  runtime          = "python3.12"
  timeout          = 20
  memory_size      = 128
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.ireland.name
    }
  }
  depends_on = [aws_iam_role_policy.read_tables, aws_iam_role_policy_attachment.logs, aws_cloudwatch_log_group.ireland]
}
resource "aws_lambda_function" "virginia" {
  provider         = aws.virginia
  function_name    = "ej7-hashtags-virginia"
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  role             = aws_iam_role.counter.arn
  handler          = "contador.handler"
  runtime          = "python3.12"
  timeout          = 20
  memory_size      = 128
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.virginia.name
    }
  }
  depends_on = [aws_iam_role_policy.read_tables, aws_iam_role_policy_attachment.logs, aws_cloudwatch_log_group.virginia]
}
resource "aws_lambda_function" "tokyo" {
  provider         = aws.tokyo
  function_name    = "ej7-hashtags-tokio"
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  role             = aws_iam_role.counter.arn
  handler          = "contador.handler"
  runtime          = "python3.12"
  timeout          = 20
  memory_size      = 128
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tokyo.name
    }
  }
  depends_on = [aws_iam_role_policy.read_tables, aws_iam_role_policy_attachment.logs, aws_cloudwatch_log_group.tokyo]
}
output "base_tables" {
  value = [aws_dynamodb_table.ireland.name, aws_dynamodb_table.virginia.name, aws_dynamodb_table.tokyo.name]
}
output "base_lambdas" {
  value = [aws_lambda_function.ireland.function_name, aws_lambda_function.virginia.function_name, aws_lambda_function.tokyo.function_name]
}
