import os

NAME = "nena"
GH = os.path.expanduser("~/github")
ORG = "annotation"
REPO = "app-nena"
TF_LOCATION = f"{GH}/CambridgeSemiticsLab/nena_tf/tf"
TF_VERSION = "alpha"
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
