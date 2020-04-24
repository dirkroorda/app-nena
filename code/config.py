from os.path import dirname, abspath

API_VERSION = 1

PROVENANCE_SPEC = dict(
    org="CambridgeSemiticsLab",
    repo="nena_tf",
    version="0.02",
    doi="10.5281/zenodo.3250721",
    corpus="Northeastern Neo-Aramaic Text Corpus",
)

DOCS = dict(
    docPage="features.md",
    featureBase="{docBase}/features{docExt}#{feature}",
    featurePage="",
    charUrl="{docBase}/transcription{docExt}",
    charText="NENA transcription script",
    webBase="{urlGh}/{org}/nena_corpus/blob/master/nena",
    webUrl="{version}/<1>/<2>.nena",
    webHint="Show this title in the NENA repository",
)

DATA_DISPLAY = (
    dict(
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
    ),
)

TYPE_DISPLAY = dict(
    text=dict(featuresBare="informant", features="title place"),
    paragraph=dict(template="{number}", children="sentence"),
    line=dict(children="paragraph"),
    sentence=dict(children="inton", condense=True),
    subsentence=dict(children="inton"),
    inton=dict(wrap=False),
    stress=dict(base=True, wrap=False),
    word=dict(featuresBare="gloss", features="gloss", wrap=False),
)

INTERFACE_DEFAULTS = dict(showFeatures=False)


def deliver():
    return (globals(), dirname(abspath(__file__)))
