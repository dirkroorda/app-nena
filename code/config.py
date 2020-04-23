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

STANDARD_FEATURES = ("dialect title text end".strip().split(),)

DATA_DISPLAY = dict(
    noneValues={None, "NA", "none", "unknown"},
    sectionSep1=", ",
    sectionSep2=", Ln. ",
    writing="cld",
    textFormats={
        "layout-orig-full": "layoutOrigFull",
        "layout-orig-lite": "word#layoutOrigLite",
        "layout-trans-full": "word#layoutTransFull",
        "layout-trans-fuzzy": "word#layoutTransFuzzy",
        "layout-trans-lite": "word#layoutTransLite",
    },
)

TYPE_DISPLAY = dict(
    text=dict(featuresBare="informant", features="title place",),
    paragraph=dict(template="{number}", children="sentence",),
    line=dict(children="paragraph",),
    sentence=dict(children="inton", condense=True,),
    subsentence=dict(children="inton",),
    inton=dict(wrap=False,),
    stress=dict(base=True, wrap=False,),
    word=dict(featuresBare="gloss", features="gloss", wrap=False,),
)

INTERFACE_DEFAULTS = dict(showFeatures=False,)


def deliver():
    return (globals(), dirname(abspath(__file__)))
