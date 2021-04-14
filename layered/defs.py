import os

GH = os.path.expanduser("~/github")
ORG = "annotation"
REPO = "app-nena"
LAYERED = "layered"
REL = f"{LAYERED}/ship"
INPUT = f"{GH}/{ORG}/{REPO}/{LAYERED}"
OUTPUT = f"{GH}/{ORG}/{REPO}/{REL}"

JS_DIR = f"{OUTPUT}/js"
JS_APP = "app.js"
JS_DEFS = "defs.js"
JS_DEST = f"{OUTPUT}/jslib/all.js"
HTML_IN = f"{INPUT}/app-template.html"
HTML_NORMAL = f"{OUTPUT}/index.html"
HTML_FILE = f"{OUTPUT}/local.html"
