#! /bin/bash

################################################################################
# RStudio SLURM job submission template
################################################################################
# Environmental variables available via SLURM:
#     RSTUDIO_SIF: singularity .sif image location
#     PASSWORD: password token for the RStudio server
#     BIND_PATHS: (can be blank) additional bind paths for singularity
################################################################################

BASH_PID=$$

################################################################################
# Functions
################################################################################

# Trap function to handle job teardown
cleanup() {
    # Search for this bash process' `rserver` child and kill it
    RSERVER_PID=$(ps -C rserver -o ppid,pid --no-headers | awk "\$1==$BASH_PID {print \$2}")
    if [[ -n "${RSERVER_PID}" ]]; then
        kill ${RSERVER_PID}
    fi
    # Clean up temporary directories
    sleep 5
    rm -rf ${SESSION_TMP}
}

# Function to retrieve an unused port from the OS, restricted to a given range
freeport() {
    comm -23 \
        <(seq 44000 44099) \
        <(ss -Htan | awk '{gsub(/.*:/, "", $4); print $4}' | sort -u) \
    | shuf \
    | head -1
}

################################################################################
# Setup the execution environment
################################################################################

module load singularityce

# Acquire an available port from the OS
IP=$(hostname -i)
PORT=$(freeport)
echo "${IP}:${PORT}"

# Create temporary working area within scratch
SESSION_TMP="${TMPDIR}/rstudio_${SLURM_JOB_ID}"
mkdir -p ${SESSION_TMP}/{etc/rstudio,tmp,run,var/lib/rstudio-server}

# Create session cookie token
uuidgen -x | tr -d '-' > "${SESSION_TMP}/etc/rstudio/secure-cookie-key"
chmod 600 "${SESSION_TMP}/etc/rstudio/secure-cookie-key"

# Write database.conf
cat > ${SESSION_TMP}/etc/rstudio/database.conf <<EOF
provider=sqlite
directory=/var/lib/rstudio-server
EOF

# Write logging.conf
cat > ${SESSION_TMP}/etc/rstudio/logging.conf <<EOF
[*]
log-level=warn
logger-type=syslog
EOF

# Write rserver.conf
cat > ${SESSION_TMP}/etc/rstudio/rserver.conf <<EOF
www-port=${PORT}
auth-none=0
auth-pam-helper-path=pam-helper
auth-timeout-minutes=0
server-data-dir=/tmp
server-user=${USER}
secure-cookie-key-file=/etc/rstudio/secure-cookie-key
EOF

# Write rsession.conf
cat > ${SESSION_TMP}/etc/rstudio/rsession.conf <<EOF
session-timeout-minutes=0
session-quit-child-processes-on-exit=1
session-default-working-dir=${SLURM_SUBMIT_DIR}
session-default-new-project-dir=/home/${USER}
EOF

# Prevent OpenMP over-allocation
export OMP_NUM_THREADS=${SLURM_CPUS_ON_NODE}

################################################################################
# Launch RStudio
################################################################################

# Wrapped with the exit trap ...
trap cleanup EXIT
# ... start the containerised RStudio Server
singularity exec \
    --bind "${SESSION_TMP}/etc/rstudio/secure-cookie-key:/etc/rstudio/secure-cookie-key" \
    --bind "${SESSION_TMP}/etc/rstudio/database.conf:/etc/rstudio/database.conf" \
    --bind "${SESSION_TMP}/etc/rstudio/logging.conf:/etc/rstudio/logging.conf" \
    --bind "${SESSION_TMP}/etc/rstudio/rserver.conf:/etc/rstudio/rserver.conf" \
    --bind "${SESSION_TMP}/etc/rstudio/rsession.conf:/etc/rstudio/rsession.conf" \
    --bind "${SESSION_TMP}/tmp:/tmp" \
    --bind "${SESSION_TMP}/run:/run" \
    --bind "${SESSION_TMP}/var/lib/rstudio-server:/var/lib/rstudio-server" \
    --bind "/opt" \
    $([[ -n "${BIND_PATHS}" ]] && echo "--bind ${BIND_PATHS}") \
    $([[ $(hostname) == gpu* ]] && echo "--nv") \
    "${RSTUDIO_SIF}" \
    rserver
