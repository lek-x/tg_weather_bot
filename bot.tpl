job "wtbot-${job_env}" {
  datacenters = ["dc1"]
  type        = "service"
   update {
    stagger      = "30s"
    max_parallel = 1
  }
  vault {
    policies = ["nomad"]
    change_mode   = "signal"
    change_signal = "SIGUSR1"
  }
  group "botgr-${job_env}" {
    network {
      port "botapp" {
	      to = 80
	    }
      port "db-${job_env}" {
        static = ${dbport}
      }
    }

    volume "postgres-${job_env}" {
      type      = "host"
      read_only = false
      source    = "postgres-${job_env}"
    }
    restart {
      attempts = 10
      interval = "5m"
      delay    = "25s"
      mode     = "delay"
    }
    update {
        max_parallel = 1
        min_healthy_time = "5s"
        healthy_deadline = "3m"
        auto_revert = false
        canary = 0
    }

    task "db-${job_env}" {
      driver = "docker"
      volume_mount {
        volume      = "postgres-${job_env}"
        destination = "/var/lib/postgresql/data"
        read_only   = false
      }
      lifecycle {
        sidecar = true
        hook = "prestart"
      }
      logs {
        max_files     = 2
        max_file_size = 3
      }
      config {
        image = "postgres:15.2-alpine"
        ports = ["db-${job_env}"]
      }
      env {
        POSTGRES_DB = "$${POSTGRES_DB}"
        POSTGRES_PASSWORD = "$${POSTGRES_PASSWORD}"
        POSTGRES_USER = "$${POSTGRES_USER}"
        PGPORT = "$${PGPORT}"
      }
      service {
	      name = "db-${job_env}"
	      port = "db-${job_env}"
        check {
           name ="alive"
           type     = "tcp"
           interval = "10s"
           timeout  = "2s"
        }
	    }

      template {
          destination = "secrets/db-${job_env}.env"
          env         = true
          change_mode = "restart"
          data        = <<EOF
            {{ with secret  "secrets/creds/nst-bot"}}
          POSTGRES_PASSWORD = {{.Data.db_pass}}
          POSTGRES_USER = {{.Data.db_user}}
          POSTGRES_DB = {{.Data.dbname_${job_env}}}
          PGPORT = {{.Data.POSTGRES_PORT_${job_env}}}
            {{end}}
          EOF
        }

      resources {
        cpu    = 350
        memory = 350
        }
      restart {
        attempts = 10
        interval = "5m"
        delay = "25s"
        mode = "delay"
      }
    }


    task "bot" {
      driver = "docker"
      logs {
        max_files     = 2
        max_file_size = 3
      }
      config {
        image = "${repo}/lek-x/${image_name}:${ver}"
        ports = ["botapp"]
        auth {
          username = "${user}"
          password = "${pass}"
        }
      }
	    env {
        bottoken = "$${bottoken}"
        weathertok = "$${weathertok}"
        PPWD = "$${PPWD}"
        POSTGRES_PASSWORD = "$${PPWD}"
        POSTGRES_USER = "$${POSTGRES_USER}"
        PDB = "$${PDB}"
        PGPORT = "$${PGPORT}"
        POSTGRES_HOST = "$${NOMAD_IP_db-${job_env}}"
		  }

	    service {
	      name = "mybot"
	      port = "botapp"
        check {
           name ="alive"
           type     = "tcp"
           interval = "10s"
           timeout  = "2s"
        }
	    }

     template {
          destination = "secrets/app-${job_env}.env"
          env         = true
          change_mode = "restart"
          data        = <<EOF
            {{ with secret  "secrets/creds/nst-bot"}}
          bottoken = {{.Data.token_${job_env}}}
          weathertok = {{.Data.weathertoken}}
          PPWD = {{.Data.db_pass}}
          POSTGRES_USER = {{.Data.db_user}}
          PDB = {{.Data.dbname_${job_env}}}
          PGPORT = {{.Data.POSTGRES_PORT_${job_env}}}
            {{end}}
          EOF
        }


      resources {
        cpu    = 150
        memory = 150
        }
      }
  }
}
