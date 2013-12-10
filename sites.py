import helpers
import conf_handler
from commander import engine


def site_opener(URLs):
    "Generate a closure function to open a list of URLs in the browser"
    #Note: this function name must match the ConfHandler instance name below
    def sites(*terms):
        for URL in URLs:
            if URL.count("%s") == 1:
                helpers.search(URL, terms)
            else:
                helpers.browser(URL)
    return sites


sites_handler = conf_handler.ConfHandler("sites", site_opener)


@engine.command
def site(*terms):
    sites_handler.add(*terms)
