# Get AWS account ID for a unique bucket name
data "aws_caller_identity" "current" {}

# Create private S3 bucket
resource "aws_s3_bucket" "ai_news" {
  bucket = "${var.project_name}-${data.aws_caller_identity.current.account_id}-ap-south-1"

  tags = {
    Name        = "AI News Storage"
    Environment = "DevOps"
    Project     = "AI News Aggregator"
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "ai_news" {
  bucket = aws_s3_bucket.ai_news.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "ai_news" {
  bucket = aws_s3_bucket.ai_news.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Enable versioning
resource "aws_s3_bucket_versioning" "ai_news" {
  bucket = aws_s3_bucket.ai_news.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Give the existing EC2 role access to this bucket only
resource "aws_iam_role_policy" "s3_access" {
  name = "ai-news-s3-access"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.ai_news.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.ai_news.arn}/*"
      }
    ]
  })
}
