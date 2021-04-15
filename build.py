import sys
import os
import re
import webbrowser

from subprocess import run, Popen, PIPE
from time import sleep
from zipfile import ZIP_DEFLATED, ZipFile

from defs import (
    NAME,
    OUTPUT,
    JS_DIR,
    JS_DEFS,
    JS_APP,
    JS_DEST,
    HTML_IN,
    HTML_NORMAL,
    HTML_FILE,
)

from mkdata import makeConfig, makeCorpus

HELP = """
python3 build.py command

command:

-h
--help
help  : print help and exit

serve          : serve search app locally
v              : show current version
debug [on|off] : production: set debug = false
config         : build config file
corpus         : build corpus files
app            : build the search app
commit         : commit repo and publish on Github Pages
ship           : increase version and commit repo and publish on Github Pages
                 performs all build steps, including version bump

For commit and ship you need to pass a commit message.
"""

VERSION_CONFIG = dict(
    setup=dict(
        file="lsversion.txt",
        re=re.compile(r"""version\s*=\s*['"]([^'"]*)['"]"""),
        mask="version='{}'",
    ),
)

DEBUG_CONFIG = dict(
    setup=dict(
        file="site/js/defs.js",
        re=re.compile(r"""export const DEBUG = ([a-z]+)"""),
        mask="export const DEBUG = {}",
    ),
)

ZIP_OPTIONS = dict(compression=ZIP_DEFLATED, compresslevel=6)


def console(*args):
    sys.stderr.write(" ".join(args) + "\n")
    sys.stderr.flush()


def readArgs():
    args = sys.argv[1:]
    if not len(args) or args[0] in {"-h", "--help", "help"}:
        console(HELP)
        console(f"Wrong arguments: «{' '.join(args)}»")
        return (False, None, [])
    arg = args[0]
    if arg not in {
        "serve",
        "v",
        "debug",
        "config",
        "corpus",
        "app",
        "commit",
        "ship",
    }:
        console(HELP)
        console(f"Wrong arguments: «{' '.join(args)}»")
        return (False, None, [])
    if arg in {"commit", "ship"}:
        if len(args) < 2:
            console("Provide a commit message")
            return (False, None, [])
        return (arg, args[1], args[2:])
    if arg in {"debug"}:
        if len(args) < 2 or args[1] not in {"on", "off"}:
            console("say on or off")
            return (False, None, [])
        return (arg, args[1], args[2:])
    return (arg, None, [])


def main():
    (task, msg, remaining) = readArgs()
    if not task:
        return
    elif task == "serve":
        serve()
    elif task == "v":
        showVersion()
    elif task == "debug":
        adjustDebug(msg)
    elif task == "config":
        makeConfig()
    elif task == "corpus":
        makeCorpus()
    elif task == "app":
        app()
    elif task == "commit":
        commit(msg)
    elif task == "ship":
        ship(msg)


def commit(msg):
    run(["git", "add", "--all", "."])
    run(["git", "commit", "-m", msg])
    run(["git", "push", "origin", "master"])
    run(["python3", "gh.py"])


def ship(msg):
    adjustVersion()
    adjustDebug(msg)
    makeConfig()
    makeCorpus()
    app()
    commit(msg)


def zipApp():
    items = set("""
        css
        corpus
        jslib
        png
        favicon.ico
        local.html
    """.strip().split())

    zipped = f"{OUTPUT}/{NAME}.zip"

    with ZipFile(zipped, "w", **ZIP_OPTIONS) as zipFile:
        with os.scandir(OUTPUT) as it:
            for entry in it:
                file = entry.name
                if file not in items:
                    continue
                if entry.is_file():
                    zipFile.write(f"{OUTPUT}/{file}", arcname=file)
                    console(f"adding {file}")
                else:
                    with os.scandir(f"{OUTPUT}/{file}") as sit:
                        for sentry in sit:
                            sfile = sentry.name
                            if sentry.is_file and not sfile.startswith("."):
                                sfile = f"{file}/{sfile}"
                                zipFile.write(f"{OUTPUT}/{sfile}", arcname=sfile)
                                console(f"adding {sfile}")
    console(f"Packaged app into {zipped}")


def serve():
    os.chdir(OUTPUT)

    server = Popen(
        ["python3", "-m", "http.server"], stdout=PIPE, bufsize=1, encoding="utf-8"
    )
    sleep(1)
    webbrowser.open("http://localhost:8000", new=2, autoraise=True)
    stopped = server.poll()
    if not stopped:
        try:
            console("Press <Ctrl+C> to stop the TF browser")
            if server:
                for line in server.stdout:
                    console(line)
        except KeyboardInterrupt:
            console("")
            if server:
                server.terminate()
                console("Http server has stopped")


def incVersion(version):
    v = int(version.lstrip("0"), base=16)
    return f"{v + 1:>04x}"


def replaceVersion(mask):
    def subVersion(match):
        currentVersion = match.group(1)
        newVersion = incVersion(currentVersion)
        return mask.format(newVersion)

    return subVersion


def getVersions():
    versions = {}

    for (key, c) in VERSION_CONFIG.items():
        with open(c["file"]) as fh:
            text = fh.read()
        match = c["re"].search(text)
        version = match.group(1)
        versions[c["file"]] = version

    return versions


def showVersion():
    versionInfo = getVersions()
    versions = set()

    for (source, version) in versionInfo.items():
        console(f'{version} (according to {source})')
        versions.add(version)


def getVersion():
    versionInfo = getVersions()
    versions = list(set(versionInfo.values()))

    if len(versions) == 0:
        console("Missing version")
        quit()
    if len(versions) > 1:
        console("Non-unique version")
        for (source, version) in versionInfo.items():
            console(f'{version} (according to {source})')
        quit()
    return versions[0]


def adjustVersion():
    currentVersion = getVersion()
    newVersion = incVersion(currentVersion)

    for (key, c) in VERSION_CONFIG.items():
        console(f'Adjusting version in {c["file"]}')
        with open(c["file"]) as fh:
            text = fh.read()
        text = c["re"].sub(replaceVersion(c["mask"]), text)
        with open(c["file"], "w") as fh:
            fh.write(text)

    console(f"Version went from `{currentVersion}` to `{newVersion}`")


def replaceDebug(mask, value):
    def subVersion(match):
        return mask.format(value)

    return subVersion


def getDebugs():
    debugs = {}

    good = True

    for (key, c) in DEBUG_CONFIG.items():
        cfile = c["file"]
        with open(cfile) as fh:
            text = fh.read()
        match = c["re"].search(text)
        if not match:
            console(f"No debug found in {cfile}")
            good = False
            continue
        debug = match.group(1)
        debugs[cfile] = debug

    if not good:
        quit()
    return debugs


def showDebug():
    debugInfo = getDebugs()

    for (source, debug) in debugInfo.items():
        console(f'{debug} (according to {source})')


def adjustDebug(onoff):
    showDebug()

    newValue = "true" if onoff == "on" else "false"

    for (key, c) in DEBUG_CONFIG.items():
        console(f'Adjusting debug in {c["file"]}')
        with open(c["file"]) as fh:
            text = fh.read()
        text = c["re"].sub(replaceDebug(c["mask"], newValue), text)
        with open(c["file"], "w") as fh:
            fh.write(text)

    console(f"Debug set to {newValue}")
    showDebug()


def app():
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
    and let the local.html include it

    We also zip the app into {NAME}.zip so that users can download it easily
    """

    version = getVersion()

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
    console(", ".join(module[0:-3] for module in modules))

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
    console(f"Combined js file written to {JS_DEST}")

    with open(HTML_IN) as fh:
        template = fh.read()
        htmlNormal = template.replace("«js»", '''type="module" src="js/app.js«v»"''')
        htmlNormal = htmlNormal.replace("«v»", f"?v={version}")
        htmlLocal = template.replace("«js»", '''defer src="jslib/all.js«v»"''')
        htmlLocal = htmlLocal.replace("«v»", f"?v={version}")

    with open(HTML_NORMAL, "w") as fh:
        fh.write(htmlNormal)
    console(f"html file written to {HTML_NORMAL}")

    with open(HTML_FILE, "w") as fh:
        fh.write(htmlLocal)
    console(f"html file (for use with file://) written to {HTML_FILE}")

    zipApp()


main()
