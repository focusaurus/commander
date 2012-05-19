#Source this from your ~/.bashrc or ~/.zshrc

########## configuration environment variables ##########
#COMMANDER_PATH should be set to the path to your commander.py file.
#    This is ~/dotfiles/commander.py by default.
#    This file should be executable with a valid shebang #! line
#
#COMMANDER_VENV may be the name of a virtual env. If set and the "workon"
#    function is available, the specified virtual env will be activated before
#    executing commander

#This is the main commander control function. It accepts the following arguments
#    on: turn on commander in one-command mode
#        (recommended for shell integration)
#    off: stop commander and disable commander integration
#    fifo: start a long-running commander process connected to a fifo
#    interpret: interpret a single command (Internal use only)
commander() {
    local EXEC=${COMMANDER_PATH-~/dotfiles/commander.py}
    local FIFO=${COMMANDER_FIFO-~/.commander_$$.fifo}
    case "${1}" in
        fifo)
            [ -p "${FIFO}" ] || mkfifo "${FIFO}"
            _commander_venv
            "${EXEC}" --repl --in "${FIFO}" &
            export COMMANDER_PID=$!
            echo commander running with pid "${COMMANDER_PID}"
            _commander_hooks
        ;;
        repl)
            shift
            _commander_venv
            if [ type rlwrap >/dev/null 2>&1 ]; then
                EXEC="rlwrap ${EXEC}"
            fi
            "${EXEC}" --repl "${@}"
        ;;
        on)
            unset COMMANDER_PID
            _commander_hooks
        ;;
        off)
            [ -n "${COMMANDER_PID}" ] && \
                ps -p "${COMMANDER_PID}" >/dev/null 2>&1 && \
                kill "${COMMANDER_PID}"
            unset COMMANDER_PID
            [ -p "${FIFO}" ] && rm "${FIFO}"
            if [ -n "${ZSH_VERSION}" ]; then
                unfunction command_not_found_handler 2>/dev/null
            else
                unset -f command_not_found_handle
            fi
        ;;
        interpret)
            shift
            if [ -n "${COMMANDER_PID}" ]; then
                #FIFO mode
                echo "${@}" > "${FIFO}"
            else
                #one-shot mode
                _commander_venv
                "${EXEC}" "${@}"
            fi
            return $?
        ;;
        *)
            echo "Usage: commander on|off|repl|fifo|interpret" 1>&2
            return 1
        ;;
    esac
}

_commander_venv() {
    #virtualenvwrapper support
    [ -n "${COMMANDER_VENV}" ] && \
        type workon > /dev/null 2>&1 && \
        workon "${COMMANDER_VENV}"
}

_commander_hooks() {
    if [ -n "${ZSH_VERSION}" ]; then
        #ZSH
        command_not_found_handler() {
            commander interpret "${@}"
            return $?
        }
    else
        #BASH
        command_not_found_handle() {
            commander interpret "${@}"
            return $?
        }
    fi
}
