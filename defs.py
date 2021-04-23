import os

APP_VERSION = "vx10@2021-04-23T10:26:29"

NAME = "nena"
GH = os.path.expanduser("~/github")
GH_URL = "https://github.com"
GH_PAGES = "github.io"
NB_TUT_URL = "https://nbviewer.jupyter.org/github/annotation/tutorials/tree/master"
ORG = "annotation"
REPO = "app-nena"
REL = "site"
INPUT = f"{GH}/{ORG}/{REPO}"
OUTPUT = f"{GH}/{ORG}/{REPO}/{REL}"
JS_DIR = f"{OUTPUT}/js"
JS_CORPUS_DIR = f"{OUTPUT}/corpus"
JS_APP = "app.js"
JS_DEFS = "defs.js"
JS_DEST = f"{OUTPUT}/jslib/all.js"
HTML_IN = f"{INPUT}/app-template.html"
HTML_NORMAL = f"{OUTPUT}/index.html"
HTML_FILE = f"{OUTPUT}/local.html"
PACKAGE_URL = f"https://{ORG}.{GH_PAGES}/{REPO}/{NAME}.zip",
APP_DOC_URL = f"https://{ORG}.{GH_PAGES}/text-fabric/tf/about/layeredsearch.html"
SOURCE_URL = f"{GH_URL}/{ORG}/{REPO}"
ISSUE_URL = f"{SOURCE_URL}/issues"
TUT_URL = f"{NB_TUT_URL}/{NAME}/start.ipynb"

TF_ORG = "CambridgeSemiticsLab"
TF_REPO = "nena_tf"
TF_LOCATION = f"{GH}/{TF_ORG}/{TF_REPO}/tf"
TF_VERSION = "alpha"
TF_DATA_URL = f"{GH_URL}/{TF_ORG}/{TF_REPO}/tree/master/tf/{TF_VERSION}"
DATA_DOC_URL = f"{GH_URL}/{TF_ORG}/{TF_REPO}/blob/master/docs/features.md"
WRITING_URL = f"https://{ORG}.{GH_PAGES}/text-fabric/tf/writing/neoaramaic.html"

URLS = dict(
    cheatsheet=(
        "cheatsheet",
        (
            "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/"
            "Regular_Expressions/Cheatsheet"
        ),
        "cheatsheet of regular expressions",
    ),
    license=(
        "license",
        "https://mit-license.org",
        "MIT license",
    ),
    corpus=(
        None,
        "https://nena.ames.cam.ac.uk",
        "North-Eastern Neo-Aramaic Data Project website",
    ),
    corpus2=(
        None,
        "https://nena.ames.cam.ac.uk",
        "North-Eastern Neo-Aramaic Data Project website",
    ),
    maker=(
        None,
        "https://dans.knaw.nl/en/front-page?set_language=en",
        "DANS = Data Archiving and Networked Services",
    ),
    author=(
        "Dirk Roorda",
        "https://pure.knaw.nl/portal/en/persons/dirk-roorda",
        "author",
    ),
    author2=(
        "Cody Kingham",
        "https://www.linkedin.com/in/cody-kingham-1135018a",
        "author (second)",
    ),
    author3=(
        "Geoffrey Khan",
        "https://www.ames.cam.ac.uk/people/professor-geoffrey-khan",
        "author (second)",
    ),
    tf=(
        None,
        f"https://{ORG}.{GH_PAGES}/text-fabric/tf/",
        "Text-Fabric documentation website",
    ),
    appdoc=(
        "about layered search",
        APP_DOC_URL,
        "Powered by Text-Fabric data",
    ),
    datadoc=(
        "data (feature) documentation",
        DATA_DOC_URL,
        "Powered by Text-Fabric data",
    ),
    data=(
        f"based on text-fabric data version {TF_VERSION}",
        TF_DATA_URL,
        "Powered by Text-Fabric data",
    ),
    source=(
        None,
        SOURCE_URL,
        "source code in Github repository",
    ),
    issue=(
        "Feature requests, bugs, feedback",
        ISSUE_URL,
        "report issues",
    ),
    issue2=(
        "Report an issue",
        ISSUE_URL,
        "report issues",
    ),
    package=(
        "download",
        PACKAGE_URL,
        "zip file for offline use",
    ),
    writing=(
        "alphabet",
        WRITING_URL,
        "characters and transliteration",
    ),
    related=(
        "text-fabric nena",
        TUT_URL,
        "using Text-Fabric on the same corpus",
    ),
)
