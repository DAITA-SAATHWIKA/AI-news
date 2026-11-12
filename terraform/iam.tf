
resource "aws_iam_role" "ec2_role" {
  name = "ai-news-devops-ec2-role"

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

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ai-news-devops-instance-profile"
  role = aws_iam_role.ec2_role.name
}

resource "aws_key_pair" "project_key" {
  key_name   = "ai-news-devops-key"
  public_key = file(pathexpand("~/.ssh/ai-news-key.pub"))
}

resource "aws_key_pair" "teammate_key" {
  key_name   = "ai-news-teammate-key"
  public_key = file("${path.module}/teammate.pub")
}
