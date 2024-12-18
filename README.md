# rstudio_manager

`rstudio_manager`: launch and manage `RStudio` servers as HPC jobs

`rstudio.py` controls the creation, deletion, and listing of `RStudio` server
sessions for the user.

`RStudio` is launched from a
[custom container](https://hub.docker.com/r/lmsbio/rstudio/)
based on the popular
[rocker/rstudio](https://hub.docker.com/r/rocker/rstudio/)
`docker` image. Various additional system, maths, and compression libraries are
added for enhanced compatibility from the
[bioconductor/bioconductor_docker](https://hub.docker.com/r/bioconductor/bioconductor_docker/)
image, as well as a few extras. To provide some extra initial functionality, the
`renv`, `devtools`, `rmarkdown`, and `tidyverse` `R` packages are pre-installed.

Three subcommands are exposed to the user:

- `rstudio start`
  Launches an `RStudio` server session, returning the URL needed to connect

- `rstudio stop`
  Runs `scancel` for a running session or for all active sessions

- `rstudio list`
  Lists the user's active sessions, their URLs, and password tokens
