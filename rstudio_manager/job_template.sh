#! /bin/bash

################################################################################
# RStudio SLURM job submission template
################################################################################
# args exported to SLURM:
#     RSTUDIO_SIF: singularity .sif image location
#     PASSWORD: password token for the RStudio server
#     BIND_PATHS: (can be blank) additional bind paths for singularity
#     CONDA_ENV: (can be blank) conda env supplying R
################################################################################

BASH_PID=$$

cleanup() {
    # Trap function to handle job teardown

    # Search for this bash process' `rserver` child and kill it
    RSERVER_PID=$(ps -C rserver -o ppid,pid --no-headers | awk "\$1==$BASH_PID {print \$2}")
    if [[ -n "${RSERVER_PID}" ]]; then
        kill ${RSERVER_PID}
    fi
    # Clean up temporary directories
    sleep 2
    rm -rf ${SESSION_TMP}
}

# Get the node's IP and an open PORT (assigned by the OS)
IP=$(hostname -i)
PORT=$(python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1])')
echo "${IP}:${PORT}"

# Load required modules from Lmod
module load singularityce

# If required, switch RSTUDIO_WHICH_R to point to a conda env
if [[ -n "${CONDA_ENV}" ]]; then
    module load miniconda3
    export RSTUDIO_WHICH_R=$(conda run -n "${CONDA_ENV}" which R)
fi

# Setup the execution environment
SESSION_TMP="${TMPDIR}/rstudio_${SLURM_JOB_ID}"
mkdir -p ${SESSION_TMP}/{tmp,run,lib}
BINDS="${SESSION_TMP}/tmp:/tmp,${SESSION_TMP}/run:/run,${SESSION_TMP}/lib:/var/lib/rstudio-server"
BINDS="${BINDS}"$([[ -n "${BIND_PATHS}" ]] && echo ",${BIND_PATHS}")

# Wrapped with the exit trap ...
trap cleanup EXIT
# ... start the containerised RStudio Server
singularity exec \
    --bind "${BINDS}" \
    $([[ $(hostname) == gpu* ]] && echo "--nv") \
    "${RSTUDIO_SIF}" \
    rserver \
    --server-user ${USER} \
    --auth-none=0  \
    --auth-pam-helper-path=pam-helper \
    --www-port ${PORT} \
    --server-data-dir /tmp
