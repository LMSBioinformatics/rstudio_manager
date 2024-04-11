# rstudio_manager

`rstudio_manager`: launch and manage `RStudio` servers as HPC jobs

`rstudio.py` controls the creation, deletion, and listing of `RStudio` server sessions
for the user. `RStudio` is launched from `singularity`-converted
[rocker/rstudio](https://hub.docker.com/r/rocker/rstudio/)
`docker` images and, optionally, is linked to an `R` installed within an existing
`conda` environment.

Three subcommands are exposed:

- `rstudio start`
  launches an `RStudio` server session, returning the URL and password token
  needed to connect.

- `rstudio stop`
  runs `scancel` for a running session

- `rstudio list`
  lists the user's active sessions, their URLs, and password tokens
