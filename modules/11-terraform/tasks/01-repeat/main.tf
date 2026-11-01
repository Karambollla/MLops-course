terraform {
  required_version = "= 1.11.4"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
}

variable "docker_host" {
  type        = string
  description = "Docker endpoint from docker context inspect"
  default     = "unix:///var/run/docker.sock"
}

provider "docker" {
  host = var.docker_host
}

resource "docker_image" "web" {
  name         = "nginx:1.27.5-alpine"
  keep_locally = true
}

resource "docker_container" "web" {
  name         = "mlops-course-terraform"
  image        = docker_image.web.image_id
  network_mode = "bridge"
  ports {
    internal = 80
    external = 8099
    ip       = "127.0.0.1"
  }
}

output "endpoint" {
  value = "http://127.0.0.1:8099"
}
