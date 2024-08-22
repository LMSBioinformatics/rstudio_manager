# rstudio_manager

`rstudio_manager`: launch and manage `RStudio` servers as HPC jobs

`rstudio.py` controls the creation, deletion, and listing of `RStudio` server
sessions for the user.

`RStudio` is launched from a
[custom container](https://hub.docker.com/r/lmsbio/rstudio/)
based on the popular
[rocker/rstudio](https://hub.docker.com/r/rocker/rstudio/)
`docker` image. Various additional system, maths, and compression libraries are
added for enhanced compatibility, as well as the `renv` and `rmarkdown` libraries
for `R` to streamline immediate use.

Three subcommands are exposed to the user:

- `rstudio start`
  Launches an `RStudio` server session, returning the URL and password token
  needed to connect. To prevent in-browser conflict between concurrent sessions,
  jobs are spread across available nodes

- `rstudio stop`
  Runs `scancel` for a running session or for all active sessions

- `rstudio list`
  Lists the user's active sessions, their URLs, and password tokens
