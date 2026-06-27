#############################################
# S3 Bucket
#############################################

resource "aws_s3_bucket" "frontend" {
  bucket = "turnos-frontend-851725347003"

  tags = {
    Name = "turnos-frontend"
  }
}

#############################################
# Static Website
#############################################

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

#############################################
# Public Access Block
#############################################

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "frontend_bucket" {

  statement {

    principals {
      type = "Service"
      identifiers = [
        "cloudfront.amazonaws.com"
      ]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.frontend.arn}/*"
    ]

    condition {
      test = "StringEquals"

      variable = "AWS:SourceArn"

      values = [
        aws_cloudfront_distribution.frontend.arn
      ]
    }
  }
}

resource "aws_s3_bucket_policy" "frontend" {

  bucket = aws_s3_bucket.frontend.id

  policy = data.aws_iam_policy_document.frontend_bucket.json
}