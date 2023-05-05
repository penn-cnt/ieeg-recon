# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'ieeg-recon'
copyright = '2023, Alfredo Lucas, Brittany H. Scheid, Nishant Sinha'
author = 'Alfredo Lucas, Brittany Scheid, Nishant Sinha'

release = '0.1'
version = '0.1.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx_tabs.tabs'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

sphinx_tabs_valid_builders = ['linkcheck']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'alabaster'  # sphinx-rtd-theme, alabaster
html_static_path = ['_static']
html_css_files = ['css/styles.css']

# html_sidebars = {
#     '**': [
#         'about.html',
#         'navigation.html',
#         'relations.html',
#         'searchbox.html',
#         'donate.html',
#     ]
# }

html_theme_options = {
    'font_family': 'Arial',
    'font_size': 12, 
    'logo' : 'logo.png',
    'github_button' : 'true',
    'github_type' : 'star',
    'github_user' : 'penn-cnt',
    'github_repo' : 'https://github.com/penn-cnt/ieeg-recon'

}

# -- Options for EPUB output
epub_show_urls = 'footnote'
