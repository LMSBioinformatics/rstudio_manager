#! /bin/bash

################################################################################
# RStudio SLURM job submission template
################################################################################
# Environmental variables available via SLURM:
#     RSTUDIO_SIF: singularity .sif image location
#     PASSWORD: password token for the RStudio server
#     BIND_PATHS: (can be blank) additional bind paths for singularity
#     CONDA_ENV: (can be blank) conda env supplying R
################################################################################

BASH_PID=$$

################################################################################
# Functions
################################################################################

#
# Trap function to handle job teardown
#

cleanup() {
    # Search for this bash process' `rserver` child and kill it
    RSERVER_PID=$(ps -C rserver -o ppid,pid --no-headers | awk "\$1==$BASH_PID {print \$2}")
    if [[ -n "${RSERVER_PID}" ]]; then
        kill ${RSERVER_PID}
    fi
    # Clean up temporary directories
    sleep 2
    rm -rf ${SESSION_TMP}
}

#
# Function to retrieve an unused port from the OS, restricted to a given range
#

freeport() {
    comm -23 \
        <(seq 44000 44099) \
        <(ss -Htan | awk '{gsub(/.*:/, "", $4); print $4}' | sort -u) \
    | shuf \
    | head -1
}

################################################################################

#
# Acquire an available port from the OS
#

IP=$(hostname -i)
PORT=$(freeport)
echo "${IP}:${PORT}"

#
# Load required modules from Lmod
#

module load singularityce

#
# Setup the execution environment
#

# Create temporary working area within scratch
SESSION_TMP="${TMPDIR}/rstudio_${SLURM_JOB_ID}"
mkdir -p ${SESSION_TMP}/{tmp/rstudio-server,run,lib}

# If required, point RStudio at a conda env
if [[ -n "${CONDA_ENV}" ]]; then
    module load miniconda3
    export RSTUDIO_WHICH_R=$(conda run -n "${CONDA_ENV}" which R)
    export SINGULARITYENV_LD_LIBRARY_PATH="/home/${USER}/.conda/envs/${CONDA_ENV}/lib"
fi

# Prevent OpenMP over-allocation
export OMP_NUM_THREADS=${SLURM_CPUS_ON_NODE}
# Don't suspend idle sessions
export SINGULARITYENV_RSTUDIO_SESSION_TIMEOUT=0


#
# Launch RStudio
#

# Wrapped with the exit trap ...
trap cleanup EXIT
# ... start the containerised RStudio Server
singularity exec \
    --bind "${SESSION_TMP}/tmp:/tmp" \
    --bind "${SESSION_TMP}/run:/run" \
    --bind "${SESSION_TMP}/lib:/var/lib/rstudio-server" \
    --bind "/opt" \
    $([[ -n "${BIND_PATHS}" ]] && echo "--bind ${BIND_PATHS}") \
    $([[ $(hostname) == gpu* ]] && echo "--nv") \
    "${RSTUDIO_SIF}" \
    rserver \
    --server-user ${USER} \
    --auth-none 0  \
    --auth-pam-helper-path pam-helper \
    --www-port ${PORT} \
    --server-data-dir /tmp \
    --rsession-memory-limit-mb ${SLURM_MEM_PER_NODE}
