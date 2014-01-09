"""Manage commander commands to open web sites by name."""
import helpers
import conf_handler
from commander import engine


def site_opener(URLs):
    """
    Generate a closure function to open a list of URLs in the browser.

    return a closure-powered site command function

    """
    #Note: this function name must match the ConfHandler instance name below
    def site(*terms):
        for URL in URLs:
            if URL.count("%s") == 1:
                helpers.search(URL, terms)
            else:
                helpers.browser(URL)
    return site


sites_handler = conf_handler.ConfHandler("site", site_opener)


@engine.command
def site(*terms):
    """commander command function to add a new site command by name."""
    sites_handler.add(*terms)
