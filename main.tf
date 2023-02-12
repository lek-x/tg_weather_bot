variable "DOCKER_USERNAME" {}
variable "DOCKER_PASSWORD" {}
variable "IMAGE_NAME" {}
variable "REPO" {}
variable "VERSION" {}
variable "JOB_ENV" {}
variable "DB_PORT" {}


resource "local_file" "nomad" {
  content = templatefile(
    "${path.module}/bot.tpl",
    {
      user       = var.DOCKER_USERNAME
      pass       = var.DOCKER_PASSWORD
      image_name = var.IMAGE_NAME
      ver        = var.VERSION
      repo       = var.REPO
      job_env    = var.JOB_ENV
      dbport     = var.DB_PORT
    }
  )
  filename = "./bot.nomad"
}
