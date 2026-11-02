output "grafana_admin_user" {
  value = var.grafana_admin_user
}

output "grafana_admin_password" {
  description = "Show it with: terraform output -raw grafana_admin_password"
  value       = random_password.grafana_admin.result
  sensitive   = true
}

output "next_steps" {
  value = <<-EOT

    Open each of these in its own terminal tab:

      App:        kubectl -n fitbit port-forward svc/fitbit-app 8502:80
                  -> http://localhost:8502

      Grafana:    kubectl -n ${local.monitoring_namespace} port-forward svc/monitoring-grafana 3000:80
                  -> http://localhost:3000  (dashboard: "Fitbit Activity Clustering")

      Prometheus: kubectl -n ${local.monitoring_namespace} port-forward svc/prometheus-operated 9090:9090
                  -> http://localhost:9090

    Grafana login: ${var.grafana_admin_user} / run `terraform output -raw grafana_admin_password`
  EOT
}
