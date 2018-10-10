"""Manage commander commands to open web sites by name."""
from . import helpers
from . import conf_handler
from commander import engine


def site_opener(urls):
    """
    Generate a closure function to open a list of urls in the browser.

    return a closure-powered site command function

    """
    # Note: this function name must be app_command
    # based on passing "app" to the ConfHandler below
    def site_command(*terms):
        for url in urls:
            if url.count("%s") == 1:
                helpers.search(url, terms)
            else:
                helpers.browser(url)

    return site_command


sites_handler = conf_handler.ConfHandler("site", site_opener)


@engine.command
def site(*terms):
    """commander command function to add a new site command by name."""
    sites_handler.add(*terms)
