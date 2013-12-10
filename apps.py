import helpers
import conf_handler
from commander import engine


def app_opener(app_name):
    "Generate a closure function to open a named application on OSX"
    #Note: this function name must match the ConfHandler instance name below
    def apps(*args):
        run_args = ["open", "-a"]
        run_args.append(" ".join(app_name))
        run_args.extend(args)
        run_args = [arg for arg in run_args if arg]
        helpers.run(run_args)
    return apps


apps_handler = conf_handler.ConfHandler("apps", app_opener)


@engine.command
def app(*tokens):
    apps_handler.add(*tokens)
