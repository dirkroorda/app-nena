import os

APP_VERSION = "0009@2021-04-16T12:29:42"

NAME = "nena"
GH = os.path.expanduser("~/github")
GH_URL = "https://github.com"
ORG = "annotation"
REPO = "app-nena"
TF_ORG = "CambridgeSemiticsLab"
TF_REPO = "nena_tf"
TF_LOCATION = f"{GH}/{TF_ORG}/{TF_REPO}/tf"
TF_VERSION = "alpha"
TF_DATA_URL = f"{GH_URL}/{TF_ORG}/{TF_REPO}/tree/master/tf/{TF_VERSION}"
DATA_DOC_URL = f"{GH_URL}/{TF_ORG}/{TF_REPO}/blob/master/docs/features.md"
APP_DOC_URL = f"https://{ORG}.github.io/text-fabric/tf/about/layeredsearch.html"
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
