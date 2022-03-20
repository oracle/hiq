# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../../src/"))
import hiq


# -- Project information -----------------------------------------------------

project = "HiQ"
copyright = "UPL 1.0, 2021, Henry Fuheng Wu @ Oracle Cloud Infrastructure"
author = "Fuheng Wu"  # HiQ Library User Guide
email = "fuheng.wu@oracle.com"
version = hiq.__version__

# The full version, including alpha/beta/rc tags
release = hiq.__version__


# -- General configuration ---------------------------------------------------
source_suffix = [".rst", ".md", ".rmd"]

# See https://github.com/readthedocs/readthedocs.org/issues/2149
master_doc = "index"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx_click.ext",
    "sphinx_copybutton",
    "recommonmark",
    "sphinxcontrib.spelling",
    "sphinx_markdown_tables",
    "sphinx.ext.mathjax",
    "sphinxcontrib.images",  # https://sphinxcontrib-images.readthedocs.io/en/latest/
    "rst2pdf.pdfbuilder",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]


# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Remove the prompt when copying examples
copybutton_prompt_text = r">>> |\.\.\.|» |$ "
copybutton_prompt_is_regexp = True

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_js_files = ["js/hiq.js"]


from recommonmark.transform import AutoStructify


def setup(app):
    app.add_config_value(
        "recommonmark_config",
        {
            #'url_resolver': lambda url: github_doc_root + url,
            "auto_toc_tree_section": "Contents",
            "enable_math": False,
            "enable_inline_math": False,
            "enable_eval_rst": True,
        },
        True,
    )
    app.add_transform(AutoStructify)


latex_engine = "xelatex"
latex_use_xindy = False
latex_elements = {
    "preamble": r"""
\usepackage[UTF8]{ctex}
%%%%%%%%%%%%%%%%%%%% Meher %%%%%%%%%%%%%%%%%%
%%%add number to subsubsection 2=subsection, 3=subsubsection
%%% below subsubsection is not good idea.
\setcounter{secnumdepth}{3}
%
%%%% Table of content upto 2=subsection, 3=subsubsection
\setcounter{tocdepth}{2}
\usepackage{amsmath,amsfonts,amssymb,amsthm}
\usepackage{graphicx}
%%% reduce spaces for Table of contents, figures and tables
%%% it is used "\addtocontents{toc}{\vskip -1.2cm}" etc. in the document
\usepackage[notlot,nottoc,notlof]{}
\usepackage{color}
\usepackage{transparent}
\usepackage{eso-pic}
\usepackage{lipsum}
\usepackage{footnotebackref} %%link at the footnote to go to the place of footnote in the text
%% spacing between line
\usepackage{setspace}
%%%%\onehalfspacing
%%%%\doublespacing
\singlespacing
%%%%%%%%%%% datetime
\usepackage{datetime}
\newdateformat{MonthYearFormat}{%
    \monthname[\THEMONTH], \THEYEAR}
%% RO, LE will not work for 'oneside' layout.
%% Change oneside to twoside in document class
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
%%% Alternating Header for oneside
\fancyhead[L]{\ifthenelse{\isodd{\value{page}}}{ \small \nouppercase{\leftmark} }{}}
\fancyhead[R]{\ifthenelse{\isodd{\value{page}}}{}{ \small \nouppercase{\rightmark} }}
%%% Alternating Header for two side
%\fancyhead[RO]{\small \nouppercase{\rightmark}}
%\fancyhead[LE]{\small \nouppercase{\leftmark}}
%% for oneside: change footer at right side. If you want to use Left and right then use same as header defined above.
\fancyfoot[R]{\ifthenelse{\isodd{\value{page}}}{{\tiny Meher Krishna Patel} }{\href{http://pythondsp.readthedocs.io/en/latest/pythondsp/toc.html}{\tiny PythonDSP}}}
%%% Alternating Footer for two side
%\fancyfoot[RO, RE]{\scriptsize Meher Krishna Patel (mekrip@gmail.com)}
%%% page number
\fancyfoot[CO, CE]{\thepage}
\renewcommand{\headrulewidth}{0.5pt}
\renewcommand{\footrulewidth}{0.5pt}
\RequirePackage{tocbibind} %%% comment this to remove page number for following
\addto\captionsenglish{\renewcommand{\contentsname}{Table of contents}}
\addto\captionsenglish{\renewcommand{\listfigurename}{List of figures}}
\addto\captionsenglish{\renewcommand{\listtablename}{List of tables}}
% \addto\captionsenglish{\renewcommand{\chaptername}{Chapter}}
%%reduce spacing for itemize
\usepackage{enumitem}
\setlist{nosep}
%%%%%%%%%%% Quote Styles at the top of chapter
\usepackage{epigraph}
\setlength{\epigraphwidth}{0.8\columnwidth}
\newcommand{\chapterquote}[2]{\epigraphhead[60]{\epigraph{\textit{#1}}{\textbf {\textit{--#2}}}}}
%%%%%%%%%%% Quote for all places except Chapter
\newcommand{\sectionquote}[2]{{\quote{\textit{``#1''}}{\textbf {\textit{--#2}}}}}
""",
    'sphinxsetup': 'VerbatimColor={rgb}{0.95, 1.0, 0.8},verbatimwithframe=true,warningBgColor={rgb}{1, 0.86,0.86},warningborder=2pt,warningBorderColor={rgb}{0.86, 0.08, 0.24},VerbatimBorderColor={rgb}{0.5,0.6,0.0},VerbatimHighlightColor={rgb}{1,1,0.8},hmargin={0.8in,0.8in}, vmargin={1in,1in}, marginpar=0.5in',
    'fontpkg': r'''
\usepackage{fontspec}
\setmainfont{Symbola}
\setsansfont{Linux Biolinum O}
\setmonofont[Color={0019D4}]{DejaVu Sans Mono}
''',
    'printindex': r'\footnotesize\raggedright\printindex',
    'papersize': r'paper=7in:9.2in,pagesize=pdftex,headinclude=on,footinclude=on',
    'pointsize': r'11pt',
    "fncychap": "\\usepackage[Conny]{fncychap}",
    'tableofcontents': '''\\begin{center}

\\includegraphics{hiq.png}

\\vspace*{1cm}
 
        \\textbf{Special Thanks To Oleksandra For Reviewing The Project While Fighting At The Same Time!}
 
        \\vspace{0.5cm}

        \\begin{center}
        Imagine there's no countries.
        
        It isn't hard to do.
        
        Nothing to kill or die for.
        
        And no religion, too.
        
        Imagine all the people.
        
        Living life in peace...


        --John Lennon
        \\end{center}

             
        \\vspace{1.5cm}
        
        \\includegraphics{../../source/dove80.png}
        
    Fuheng Wu, 2022, CA, USA.\\end{center}\\clearpage\\tableofcontents''',
    #"maketitle": "\\input{main.tex}"
    # ...
}

latex_logo = "_static/hiq.png"
