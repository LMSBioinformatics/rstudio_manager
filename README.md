# rstudio_manager

`rstudio_manager`: launch and manage `RStudio` servers as HPC jobs

`rstudio.py` controls the creation, deletion, and listing of `RStudio` server sessions
for the user. `RStudio`, launched from a `singularity`-converted
[rocker/rstudio](https://hub.docker.com/r/rocker/rstudio/)
`docker` image, links to `R` installed within an existing named `conda` environment.

Three subcommands are exposed:

- `rstudio start`
  launches an `RStudio` server session, returning the URL and password token
  needed to connect

- `rstudio stop`
  runs `scancel` for a running session or for all active sessions

- `rstudio list`
  lists the user's active sessions, their URLs, and password tokens
