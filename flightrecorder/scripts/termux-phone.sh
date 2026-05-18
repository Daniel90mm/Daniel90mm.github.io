#!/usr/bin/env bash
set -euo pipefail

PHONE_HOST="${PHONE_HOST:-192.168.8.112}"
PHONE_USER="${PHONE_USER:-u0_a265}"
PHONE_PORT="${PHONE_PORT:-8022}"
PHONE_KEY="${PHONE_KEY:-$HOME/.ssh/codex_flint2_temp}"

FLIGHTRECORDER_CHECKOUT="${FLIGHTRECORDER_CHECKOUT:-$HOME/hugo-site}"
FLIGHTRECORDER_SOURCE="${FLIGHTRECORDER_SOURCE:-$FLIGHTRECORDER_CHECKOUT/flightrecorder}"
FLIGHTRECORDER_HOME="${FLIGHTRECORDER_HOME:-$HOME/flightrecorder}"
FLIGHTRECORDER_HOST="${FLIGHTRECORDER_HOST:-127.0.0.1}"
FLIGHTRECORDER_PORT="${FLIGHTRECORDER_PORT:-8000}"
FLIGHTRECORDER_PID="${FLIGHTRECORDER_PID:-$HOME/flightrecorder-backend.pid}"
FLIGHTRECORDER_LOG="${FLIGHTRECORDER_LOG:-$HOME/logs/flightrecorder-backend.log}"
FLIGHTRECORDER_BOOT="${FLIGHTRECORDER_BOOT:-$HOME/.termux/boot/start-flightrecorder.sh}"


usage() {
    cat <<EOF
Usage: $(basename "$0") <command> [args...]

Laptop-side helper for flightrecorder on the Termux phone.

Environment overrides:
  PHONE_HOST=$PHONE_HOST
  PHONE_USER=$PHONE_USER
  PHONE_PORT=$PHONE_PORT
  PHONE_KEY=$PHONE_KEY
  FLIGHTRECORDER_CHECKOUT=$FLIGHTRECORDER_CHECKOUT
  FLIGHTRECORDER_SOURCE=$FLIGHTRECORDER_SOURCE
  FLIGHTRECORDER_HOME=$FLIGHTRECORDER_HOME
  FLIGHTRECORDER_HOST=$FLIGHTRECORDER_HOST
  FLIGHTRECORDER_PORT=$FLIGHTRECORDER_PORT

Commands:
  shell          Open an interactive Termux SSH shell
  exec <cmd...>  Run a command in Termux
  start-backend  Start the backend with nohup and a wake lock
  stop-backend   Stop the backend pid if present
  status         Print backend pid and recent log lines
  install-boot   Install Termux:Boot script for the backend only
EOF
}


ssh_phone() {
    ssh -i "$PHONE_KEY" -p "$PHONE_PORT" \
        -o IdentitiesOnly=yes \
        -o StrictHostKeyChecking=accept-new \
        "${PHONE_USER}@${PHONE_HOST}" "$@"
}


remote_start_backend_script() {
    cat <<'REMOTE'
set -e
mkdir -p "$HOME/logs" "$FLIGHTRECORDER_HOME"
if [ -f "$FLIGHTRECORDER_PID" ]; then
    old=$(cat "$FLIGHTRECORDER_PID" 2>/dev/null || true)
    [ -n "$old" ] && kill "$old" 2>/dev/null || true
fi
termux-wake-lock 2>/dev/null || true
cd "$FLIGHTRECORDER_SOURCE"
if [ ! -x ".venv/bin/uvicorn" ]; then
    python -m venv .venv
    .venv/bin/python -m pip install -e ".[dev]"
fi
nohup env FLIGHTRECORDER_HOME="$FLIGHTRECORDER_HOME" \
    .venv/bin/uvicorn "flightrecorder.app:create_app" \
    --factory \
    --host "$FLIGHTRECORDER_HOST" \
    --port "$FLIGHTRECORDER_PORT" \
    >"$FLIGHTRECORDER_LOG" 2>&1 &
echo $! > "$FLIGHTRECORDER_PID"
sleep 1
ps -ef | grep 'uvicorn .*flightrecorder.app:create_app' | grep -v grep || true
REMOTE
}


remote_env_prefix() {
    printf "export FLIGHTRECORDER_SOURCE=%q FLIGHTRECORDER_HOME=%q FLIGHTRECORDER_HOST=%q FLIGHTRECORDER_PORT=%q FLIGHTRECORDER_PID=%q FLIGHTRECORDER_LOG=%q; " \
        "$FLIGHTRECORDER_SOURCE" \
        "$FLIGHTRECORDER_HOME" \
        "$FLIGHTRECORDER_HOST" \
        "$FLIGHTRECORDER_PORT" \
        "$FLIGHTRECORDER_PID" \
        "$FLIGHTRECORDER_LOG"
}


case "${1:-}" in
    shell)
        ssh_phone
        ;;
    exec)
        shift
        if [ "$#" -eq 0 ]; then
            usage
            exit 2
        fi
        ssh_phone "$@"
        ;;
    start-backend)
        ssh_phone "$(remote_env_prefix) $(remote_start_backend_script)"
        ;;
    stop-backend)
        ssh_phone "
            if [ -f '$FLIGHTRECORDER_PID' ]; then
                old=\$(cat '$FLIGHTRECORDER_PID' 2>/dev/null || true)
                [ -n \"\$old\" ] && kill \"\$old\" 2>/dev/null || true
                rm -f '$FLIGHTRECORDER_PID'
            fi
        "
        ;;
    status)
        ssh_phone "
            set +e
            echo 'pid:'
            [ -f '$FLIGHTRECORDER_PID' ] && cat '$FLIGHTRECORDER_PID' || true
            echo 'process:'
            ps -ef | grep 'uvicorn .*flightrecorder.app:create_app' | grep -v grep || true
            echo 'log:'
            tail -n 40 '$FLIGHTRECORDER_LOG' 2>/dev/null || true
        "
        ;;
    install-boot)
        ssh_phone "
            set -e
            mkdir -p ~/.termux/boot ~/logs
            cat > '$FLIGHTRECORDER_BOOT' <<'BOOT'
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock 2>/dev/null || true
sshd 2>/dev/null || true

export FLIGHTRECORDER_SOURCE=\"$FLIGHTRECORDER_SOURCE\"
export FLIGHTRECORDER_HOME=\"$FLIGHTRECORDER_HOME\"
export FLIGHTRECORDER_HOST=\"$FLIGHTRECORDER_HOST\"
export FLIGHTRECORDER_PORT=\"$FLIGHTRECORDER_PORT\"
export FLIGHTRECORDER_PID=\"$FLIGHTRECORDER_PID\"
export FLIGHTRECORDER_LOG=\"$FLIGHTRECORDER_LOG\"

mkdir -p \"\$HOME/logs\" \"\$FLIGHTRECORDER_HOME\"
cd \"\$FLIGHTRECORDER_SOURCE\"

if [ -f \"\$FLIGHTRECORDER_PID\" ]; then
  old=\$(cat \"\$FLIGHTRECORDER_PID\" 2>/dev/null || true)
  if [ -n \"\$old\" ] && kill -0 \"\$old\" 2>/dev/null; then
    exit 0
  fi
fi

if ps -ef | grep 'uvicorn .*flightrecorder.app:create_app' | grep -v grep >/dev/null 2>&1; then
  exit 0
fi

nohup .venv/bin/uvicorn \"flightrecorder.app:create_app\" \
  --factory \
  --host \"\$FLIGHTRECORDER_HOST\" \
  --port \"\$FLIGHTRECORDER_PORT\" \
  >\"\$FLIGHTRECORDER_LOG\" 2>&1 &
echo \$! > \"\$FLIGHTRECORDER_PID\"
BOOT
            chmod 700 '$FLIGHTRECORDER_BOOT'
            sed -n '1,220p' '$FLIGHTRECORDER_BOOT'
        "
        ;;
    ""|-h|--help|help)
        usage
        ;;
    *)
        usage
        exit 2
        ;;
esac
