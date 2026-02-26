variable "service_account_key_file" {
  description = "Path to service account key file"
  type        = string
}

variable "cloud_id" {
  type = string
}

variable "folder_id" {
  type = string
}

variable "zone" {
  default = "ru-central1-a"
}

variable "public_ssh_key" {
  description = "Path to public SSH key"
  type        = string
}

variable "my_ip" {
  description = "Your IP in CIDR format"
  type        = string
}