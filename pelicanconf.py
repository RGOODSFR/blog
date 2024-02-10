AUTHOR = 'RGOODS Tech team'
SITENAME = 'RGOODS Engineering'
#SITEURL = "https://engineering.rgoods.com"

PATH = "content"

TIMEZONE = 'Europe/Paris'

ARTICLE_TRANSLATION_ID = 'id'
DEFAULT_LANG = 'fr'
LOCALE = 'fr_FR'


# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("RGOODS", "https://rgoods.com/"),
)

# Social widget
SOCIAL = (
    ("Instagram", "https://www.instagram.com/rgoods_official/"),
    ("Linkedin", "https://www.linkedin.com/company/rgoods/"),
)

DEFAULT_PAGINATION = False

DISPLAY_CATEGORIES_ON_MENU = False
# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

STATIC_PATHS = ['images']
EXTRA_PATH_METADATA = {'images/favicon.ico': {'path': 'favicon.ico'},}
