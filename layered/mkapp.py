"""
The app is a modular Javascript program.
That does not work when you open the HTML file locally
(i.e. when the HTML is not served by a server).

N.B. There is a difference between a local web server serving at
`localhost` and opening the file directly into your browser by double clicking on it.

In the first case, you see in your browser, in the URL box something that starts with
`http://` or `https://`, in the second case you see `file://` instead.

Modular Javascript does not work with `file://` origins.

For that case, we bundle the modules into one,
and let the index.html include it with the flag `nomodule`
"""

import os
import re

from defs import JS_DIR, JS_DEFS, JS_APP, JS_DEST, HTML_IN, HTML_NORMAL, HTML_FILE


def bundleApp():

    commentRe = re.compile(r"""[ \t]*/\*.*?\*/[ \t]*""", re.S)
    importRe = re.compile(r'''import\s+\{.*?\}\s+from\s+"[^"]*\.js"''', re.S)
    exportRe = re.compile(r"""^export[ ]+""", re.M)
    whiteRe = re.compile(r"""^\s+$""", re.M)
    nlRe = re.compile(r"""\n\n+""")

    def getModule(module):
        with open(f"{JS_DIR}/{module}") as fh:
            text = fh.read()
        text = importRe.sub("", text)
        text = exportRe.sub("", text)
        text = commentRe.sub("", text)
        text = whiteRe.sub("", text)
        text = nlRe.sub("\n", text)
        return text

    modules = []

    with os.scandir(JS_DIR) as it:
        for entry in it:
            name = entry.name
            if not entry.is_file() or name.startswith(".") or not name.endswith(".js"):
                continue
            modules.append(entry.name)
    print(", ".join(module[0:-3] for module in modules))

    content = {module: getModule(module) for module in modules}

    header = """\
/*eslint-env jquery*/
/* global configData */
/* global corpusData */


"""
    combined = (
        header
        + content[JS_DEFS]
        + "\n\n"
        + "\n\n".join(
            text for (name, text) in content.items() if name not in {JS_DEFS, JS_APP}
        )
        + "\n\n"
        + content[JS_APP]
    )
    with open(JS_DEST, "w") as fh:
        fh.write(combined)
    print(f"Combined js file written to {JS_DEST}")

    with open(HTML_IN) as fh:
        htmlTemplate = fh.read()

    with open(HTML_NORMAL, "w") as fh:
        fh.write(htmlTemplate.replace("«»", '''type="module" src="js/app.js"'''))
    print(f"html file written to {HTML_NORMAL}")

    with open(HTML_FILE, "w") as fh:
        fh.write(htmlTemplate.replace("«»", '''defer src="jslib/all.js"'''))
    print(f"html file (for use with file://) written to {HTML_FILE}")


bundleApp()
