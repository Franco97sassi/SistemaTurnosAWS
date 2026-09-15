variable "region" {
  description = "AWS region used by the project"
  type        = string
  default     = "us-east-1"
}
variable "environment" {
  description = "Deployment environment used for tags and safety controls"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "environment must be dev, staging or production."
  }
}

variable "alarm_email" {
  description = "Optional email that receives operational alarms"
  type        = string
  default     = ""
}

variable "auth_secret_arn" {
  description = "Secrets Manager ARN with JWT_SECRET and ADMIN_PASSWORD JSON keys (required in production)"
  type        = string
  default     = ""
}

variable "admin_email" {
  description = "Email used by the initial operations account"
  type        = string
  default     = "admin@turnos.local"
}
variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "turnosdb"
}

variable "db_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "postgres"
}

variable "cors_origins" {
  description = "Comma-separated origins allowed to call the API"
  type        = string
  default     = "http://localhost:5173"
}
