commander-on() {
    export COMMANDER_FIFO="/tmp/commander_$$.fifo"
    [ -p "${COMMANDER_FIFO}" ] || mkfifo "${COMMANDER_FIFO}"
    workon commander
    unset RPROMPT
    PS1="%~->"
    ~/projects/unix_shell/commander.py --in "${COMMANDER_FIFO}" &
    export COMMANDER_PID=$!
    echo commander running with pid "${COMMANDER_PID}"
}

commander-off() {
    [ -d "/proc/${COMMANDER_PID}" ] && kill "${COMMANDER_PID}"
    unset COMMANDER_PID
    [ -p "${COMMANDER_FIFO}" ] && rm "${COMMANDER_FIFO}"
    unset COMMANDER_FIFO
    deactivate
    #unfunction command_not_found_handler
}

command_not_found_handler() {
    [ -p "${COMMANDER_FIFO}" ] && echo "${@}" > "${COMMANDER_FIFO}"
    return $?
}
