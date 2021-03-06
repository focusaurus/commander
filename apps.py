"""Manage commander commands to open applications by name."""
from . import helpers
from . import conf_handler
from commander import engine


def app_opener(app_name):
    """
    Generate a closure function to open a named application on OSX.

    return a closure-powered app command function

    """
    # Note: this function name must be app_command
    # based on passing "app" to the ConfHandler below
    def app_command(*args):
        run_args = ["open", "-a"]
        run_args.append(" ".join(app_name))
        run_args.extend(args)
        run_args = [arg for arg in run_args if arg]
        helpers.run(run_args)

    return app_command


apps_handler = conf_handler.ConfHandler("app", app_opener)


@engine.command
def app(*tokens):
    """command function to add a command for an app with command name."""
    apps_handler.add(*tokens)
