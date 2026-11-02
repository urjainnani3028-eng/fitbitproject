variable "kubeconfig_path" {
  description = "Path to your kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "kubectl context to deploy to (Docker Desktop's is \"docker-desktop\")"
  type        = string
  default     = "docker-desktop"
}

variable "app_image" {
  description = "Container image for the app. Use the GHCR image to deploy what CI built."
  type        = string
  default     = "fitbit-app:latest"
}

variable "app_image_pull_policy" {
  description = "IfNotPresent for a locally built image, Always for a registry image"
  type        = string
  default     = "IfNotPresent"

  validation {
    condition     = contains(["Always", "IfNotPresent", "Never"], var.app_image_pull_policy)
    error_message = "Must be Always, IfNotPresent or Never."
  }
}

variable "prometheus_stack_version" {
  description = "Version of the kube-prometheus-stack Helm chart"
  type        = string
  default     = "92.17.0"
}

variable "grafana_admin_user" {
  description = "Grafana admin username"
  type        = string
  default     = "admin"
}
