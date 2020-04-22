from os.path import dirname, abspath

API_VERSION = 1

PROTOCOL = "http://"
HOST = "localhost"
PORT = {"kernel": 19700, "web": 9700}

ORG = "CambridgeSemiticsLab"
REPO = "nena_tf"
CORPUS = "Northeastern Neo-Aramaic Text Corpus"
VERSION = "0.02"
RELATIVE = "tf"

DOI_TEXT = "10.5281/zenodo.3250721"
DOI_URL = "https://doi.org/10.5281/zenodo.3250721"

DOC_URL = f"https://github.com/{ORG}/{REPO}/blob/master/docs"
DOC_INTRO = "features.md"
CHAR_URL = f"https://github.com/{ORG}/{REPO}/blob/master/docs/transcription.md"
CHAR_TEXT = ("NENA transcription script",)

FEATURE_URL = f"{DOC_URL}/features.md#{{feature}}"

MODULE_SPECS = ()

ZIP = [REPO]

NONE_VALUES = {None, "NA", "none", "unknown"}

EXAMPLE_SECTION = (
    f"<code>Village Life 1.1</code> (use"
    f' <a href="https://github.com/{ORG}/{REPO}'
    f'/blob/master/tf/{VERSION}/book%40en.tf" target="_blank">'
    f"English book names</a>)"
)
EXAMPLE_SECTION_TEXT = "Barwar, The Monk and the Angel, 1"

STANDARD_FEATURES = "dialect title text end".strip().split(),

DATA_DISPLAY = dict(
    noneValues={None, "NA", "none", "unknown"},
    sectionSep1=", ",
    sectionSep2=", Ln. ",
    writing="cld",
    writingDir="ltr",
    fontName="CharisSIL-R",
    font="CharisSIL-R.otf",
    fontw="CharisSIL-R.woff",
    textFormats={
        "layout-orig-full": "layoutOrigFull",
        "layout-orig-lite": "word#layoutOrigLite",
        "layout-trans-full": "word#layoutTransFull",
        "layout-trans-fuzzy": "word#layoutTransFuzzy",
        "layout-trans-lite": "word#layoutTransLite",
    },
    browseNavLevel=2,
    browseContentPretty=False,
)

TYPE_DISPLAY = dict(
    dialect=dict(
        template="{dialect}",
        children="text",
        level=3, flow="col", wrap=False, stretch=False,
    ),
    text=dict(
        template="{text_id}",
        featuresBare="informant",
        features="title place",
        children="line",
        level=3, flow="col", wrap=False, strectch=False,
    ),
    paragraph=dict(
        template="{number}",
        children="sentence",
        level=3, flow="col", wrap=False, strectch=True,
    ),
    line=dict(
        template="{number}",
        children="paragraph",
        level=2, flow="row", wrap=True, strectch=True,
    ),
    sentence=dict(
        template="",
        children="inton",
        condense=True,
        level=2, flow="row", wrap=True, strectch=True,
    ),
    subsentence=dict(
        template="",
        level=2, flow="row", wrap=True, strectch=True,
    ),
    inton=dict(
        template="",
        children="stress",
        level=1, flow="row", wrap=True, strectch=True,
    ),
    stress=dict(
        template="",
        children="word",
        base=True,
        level=1, flow="row", wrap=True, strectch=True,
    ),
    word=dict(
        template=True,
        featuresBare="gloss",
        features="gloss",
        children="letter",
        level=1, flow="row", wrap=True, strectch=True,
    ),
    letter=dict(
        template=True,
        level=0, flow="col", wrap=False, strectch=False,
    ),
)

INTERFACE_DEFAULTS = dict(
    showFeatures=False,
)


def deliver():
    return (globals(), dirname(abspath(__file__)))
