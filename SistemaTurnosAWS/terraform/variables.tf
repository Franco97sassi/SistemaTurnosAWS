variable "region" {
  description = "AWS region used by the project"
  type        = string
  default = "us-east-1"
}
variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default = "turnosdb"
}

variable "db_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default = "postgres"
}

variable "cors_origins" {
  description = "Comma-separated origins allowed to call the API"
  type        = string
  default     = "http://localhost:5173"
}
