AUTHOR = 'RGOODS Tech team'
SITENAME = 'RGOODS Engineering'
SITESUBTITLE = (
    'We are RGOODS tech team.<br />'
    'We build cool tools to help associations & NGOs raise more funds.<br />'
    'On this blog, we talk about Python/Django/Wagtail & VueJS.'
)
SITEURL = 'http://localhost:8000'

PATH = "content"

TIMEZONE = 'Europe/Paris'

COPYRIGHT_NAME = 'RGOODS'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("rgoods", "https://rgoods.com/"),
)

# Social widget
SOCIAL = (
    ("instagram", "https://www.instagram.com/rgoods_official/"),
    ("linkedin", "https://www.linkedin.com/company/rgoods/"),
    ('rss', '/feeds/all.atom.xml'),
)

DEFAULT_PAGINATION = False

MAIN_MENU = True
MENUITEMS = (('Archives', '/archives.html'),
             ('Categories', '/categories.html'),)

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

STATIC_PATHS = ['images']

THEME = "themes/Flex"

SITELOGO = "/images/logo.png"
FAVICON = "/images/favicon.ico"

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["i18n_subsites"]

# Internationalisation
ARTICLE_TRANSLATION_ID = 'id'
DEFAULT_LANG = "en"
I18N_TEMPLATES_LANG = "en"
I18N_SUBSITES = {
    'fr': {
        'SITENAME': 'RGOODS Ingénierie',
        'SITESUBTITLE': (
            "Nous sommes l'équipe tech RGOODS.<br />"
            "Nous construisons des outils cool pour aider les associations et les ONGs à récolter plus de fonds.<br />"
            "Sur ce blog, nous parlons principalement de Python/Django/Wagtail & VueJS."
        ),
        'MENUITEMS': (
            ('Archives', '/archives.html'),
            ('Catégories', '/categories.html'),
        ),
        'DEFAULT_LANG': "fr"
    }
}
JINJA_ENVIRONMENT = {
  'extensions': ['jinja2.ext.i18n']
}