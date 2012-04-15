#Source this from your ~/.bashrc or ~/.zshrc
#customize as you see fit
#For example, you may want to integrate virtualenvwrapper

commander-on() {
    #Set this to "fifo" to have 1 long-running commander process
    export COMMANDER_MODE=one
    case "${COMMANDER_MODE}" in
        "fifo")
            export COMMANDER_FIFO="/tmp/commander_$$.fifo"
            [ -p "${COMMANDER_FIFO}" ] || mkfifo "${COMMANDER_FIFO}"
            workon commander
            ~/dotfiles/commander.py --repl --in "${COMMANDER_FIFO}" &
            export COMMANDER_PID=$!
            echo commander running with pid "${COMMANDER_PID}"
        ;;
        "one")
            unset COMMANDER_FIFO
            unset COMMANDER_PID
        ;;
    esac
}

commander-off() {
    [ -n "${COMMANDER_PID}" ] && [ -d "/proc/${COMMANDER_PID}" ] && kill "${COMMANDER_PID}"
    unset COMMANDER_PID
    [ -p "${COMMANDER_FIFO}" ] && rm "${COMMANDER_FIFO}"
    unset COMMANDER_FIFO
    unset COMMANDER_MODE
}


commander-exec() {
    case "${COMMANDER_MODE}" in
        fifo)
            clear
            echo "${@}" > "${COMMANDER_FIFO}"
        ;;
        one)
             ~/dotfiles/commander.py "${@}"
        ;;
    esac
    return $?
}

if [ -n "${ZSH_VERSION} "]; then
    #ZSH
    command_not_found_handler() {
        commander-exec "${@}"
    }
else
    #BASH
    command_not_found_handle() {
        commander-exec "${@}"
    }
fi
