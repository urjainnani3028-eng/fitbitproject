locals {
  k8s_dir              = "${path.module}/../k8s"
  monitoring_namespace = "monitoring"

  # The app is described once, in ../k8s, so `kubectl apply -f k8s/` and
  # Terraform deploy exactly the same thing. Terraform only swaps the image.
  deployment_yaml = replace(
    replace(
      file("${local.k8s_dir}/10-deployment.yaml"),
      "image: fitbit-app:latest",
      "image: ${var.app_image}",
    ),
    "imagePullPolicy: IfNotPresent",
    "imagePullPolicy: ${var.app_image_pull_policy}",
  )
}

# ---------------------------------------------------------------------------
# App: namespace, Deployment and Service from ../k8s
# ---------------------------------------------------------------------------
resource "kubernetes_manifest" "app_namespace" {
  manifest = yamldecode(file("${local.k8s_dir}/00-namespace.yaml"))
}

resource "kubernetes_manifest" "app_deployment" {
  manifest = yamldecode(local.deployment_yaml)

  # Don't finish until the new pods are ready
  wait {
    rollout = true
  }

  timeouts {
    create = "5m"
    update = "5m"
  }

  depends_on = [kubernetes_manifest.app_namespace]
}

resource "kubernetes_manifest" "app_service" {
  manifest = yamldecode(file("${local.k8s_dir}/20-service.yaml"))

  depends_on = [kubernetes_manifest.app_namespace]
}

# ---------------------------------------------------------------------------
# Monitoring: Prometheus + Grafana (kube-prometheus-stack)
# ---------------------------------------------------------------------------
resource "kubernetes_namespace_v1" "monitoring" {
  metadata {
    name = local.monitoring_namespace
  }
}

resource "random_password" "grafana_admin" {
  length  = 20
  special = false
}

# Grafana reads its login from this Secret (see monitoring/values.yaml)
resource "kubernetes_secret_v1" "grafana_admin" {
  metadata {
    name      = "grafana-admin"
    namespace = local.monitoring_namespace
  }

  data = {
    "admin-user"     = var.grafana_admin_user
    "admin-password" = random_password.grafana_admin.result
  }

  depends_on = [kubernetes_namespace_v1.monitoring]
}

# Grafana's sidecar loads any ConfigMap labelled grafana_dashboard=1
resource "kubernetes_config_map_v1" "fitbit_dashboard" {
  metadata {
    name      = "fitbit-dashboard"
    namespace = local.monitoring_namespace
    labels = {
      grafana_dashboard = "1"
    }
  }

  data = {
    "fitbit-dashboard.json" = file("${path.module}/../monitoring/fitbit-dashboard.json")
  }

  depends_on = [kubernetes_namespace_v1.monitoring]
}

resource "helm_release" "monitoring" {
  name       = "monitoring"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  version    = var.prometheus_stack_version
  namespace  = local.monitoring_namespace

  values = [file("${path.module}/../monitoring/values.yaml")]

  timeout = 900 # first install downloads several images

  depends_on = [
    kubernetes_namespace_v1.monitoring,
    kubernetes_secret_v1.grafana_admin,
  ]
}
