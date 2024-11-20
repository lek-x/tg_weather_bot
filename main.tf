variable "DOCKER_USERNAME" {}
variable "DOCKER_PASSWORD" {}
variable "IMAGE_NAME" {}
variable "REPO" {}
variable "VERSION" {}
variable "JOB_ENV" {}
variable "BOT_TOKEN" {}
variable "POSTGRES_PASSWORD" {}
variable "POSTGRES_USER" {}
variable "POSTGRES_DB" {}
variable "POSTGRES_PORT" {}

locals {
  compose_filename = var.JOB_ENV == "prod" ? "docker_compose_weather_bot_prod.yml" : "docker_compose_weather_bot_dev.yml"
}


resource "local_file" "compose" {
  content = templatefile(
    "${path.module}/docker_compose.yml.tpl",
    {
      user              = var.DOCKER_USERNAME
      pass              = var.DOCKER_PASSWORD
      image_name        = var.IMAGE_NAME
      ver               = var.VERSION
      repo              = var.REPO
      JOB_ENV           = var.JOB_ENV
      POSTGRES_USER     = var.POSTGRES_USER
      POSTGRES_PORT     = var.POSTGRES_PORT
      POSTGRES_PASSWORD = var.POSTGRES_PASSWORD
      POSTGRES_DB       = var.POSTGRES_DB
      BOT_TOKEN         = var.BOT_TOKEN

    }
  )
  filename = "./${local.compose_filename}"
}
