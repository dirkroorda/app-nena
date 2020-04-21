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

BASE_TYPE = "stress"
CONDENSE_TYPE = "sentence"

NONE_VALUES = {None, "NA", "none", "unknown"}

STANDARD_FEATURES = """
    dialect title text end
""".strip().split()

EXCLUDED_FEATURES = set()

NO_DESCEND_TYPES = {}

EXAMPLE_SECTION = (
    f"<code>Village Life 1.1</code> (use"
    f' <a href="https://github.com/{ORG}/{REPO}'
    f'/blob/master/tf/{VERSION}/book%40en.tf" target="_blank">'
    f"English book names</a>)"
)
EXAMPLE_SECTION_TEXT = "Barwar, The Monk and the Angel, 1"

SECTION_SEP1 = ", "
SECTION_SEP2 = ", Ln. "

WRITING = "cld"
WRITING_DIR = "ltr"

FONT_NAME = "CharisSIL-R"
FONT = "CharisSIL-R.otf"
FONTW = "CharisSIL-R.woff"

TEXT_FORMATS = {
    "layout-orig-full": "layoutOrigFull",
    "layout-orig-lite": "word#layoutOrigLite",
    "layout-trans-full": "word#layoutTransFull",
    "layout-trans-fuzzy": "word#layoutTransFuzzy",
    "layout-trans-lite": "word#layoutTransLite",
}

BROWSE_NAV_LEVEL = 2
BROWSE_CONTENT_PRETTY = False

VERSE_TYPES = None

LEX = None

TRANSFORM = None

CHILD_TYPE = dict(
    word="letter",
    stress="word",
    inton="stress",
    sentence="inton",
    paragraph="sentence",
    line="paragraph",
    text="line",
    dialect="text",
)

SUPER_TYPE = None

TYPE_DISPLAY = dict(
    dialect=dict(
        template="{dialect}",
        bareFeatures="",
        features="",
        level=3, flow="col", wrap=False, stretch=False,
    ),
    text=dict(
        template="{text_id}",
        bareFeatures="informant",
        features="title place",
        level=3, flow="col", wrap=False, strectch=False,
    ),
    paragraph=dict(
        template="{number}",
        bareFeatures="",
        features="",
        level=3, flow="col", wrap=False, strectch=True,
    ),
    line=dict(
        template="{number}",
        bareFeatures="",
        features="",
        level=2, flow="row", wrap=True, strectch=True,
    ),
    sentence=dict(
        template="",
        bareFeatures="",
        features="",
        level=2, flow="row", wrap=True, strectch=True,
    ),
    subsentence=dict(
        template="",
        bareFeatures="",
        features="",
        level=2, flow="row", wrap=True, strectch=True,
    ),
    inton=dict(
        template="",
        bareFeatures="",
        features="",
        level=1, flow="row", wrap=True, strectch=True,
    ),
    stress=dict(
        template="",
        bareFeatures="",
        features="",
        level=1, flow="row", wrap=True, strectch=True,
    ),
    word=dict(
        template=True,
        bareFeatures="gloss",
        features="gloss",
        level=1, flow="row", wrap=True, strectch=True,
    ),
    letter=dict(
        template=True,
        bareFeatures="",
        features="",
        level=0, flow="col", wrap=False, strectch=False,
    ),
)

INTERFACE_DEFAULTS = dict(
    showFeatures=False,
)


def deliver():
    return (globals(), dirname(abspath(__file__)))
