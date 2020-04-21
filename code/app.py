import re
from tf.core.helpers import htmlEsc
from tf.applib.helpers import dh
from tf.applib.api import setupApi
from tf.applib.links import outLink

PLAIN_LINK = (
    "https://github.com/{org}/nena_corpus/blob/master/nena/"
    "{version}/{dialect}/{title}.nena"
)

speakerRe = re.compile(r"""«([^»]+)»""", re.S)


def speakerRepl(match):
    return f"""<span class="speaker">{htmlEsc(match.group(1))}</span>"""


def notice(app):
    if int(app.api.TF.version.split(".")[0]) <= 7:
        print(
            f"""
Your Text-Fabric is outdated.
It cannot load this version of the TF app `{app.appName}`.
Recommendation: upgrade Text-Fabric to version 8.
Hint:

    pip3 install --upgrade text-fabric

"""
        )


class TfApp:
    def __init__(app, *args, **kwargs):
        setupApi(app, *args, **kwargs)
        notice(app)

    def webLink(app, n, text=None, clsName=None, _asString=False, _noUrl=False):
        api = app.api
        T = api.T
        version = app.version

        dialect, text_title, line = T.sectionFromNode(n, fillup=True)
        passageText = app.sectionStrFromNode(n)

        href = (
            "#"
            if _noUrl
            else PLAIN_LINK.format(
                org=app.org, version=version, dialect=dialect, title=text_title
            )
        )

        if text is None:
            text = passageText
            title = "see this passage in its source document"
        else:
            title = passageText

        target = "" if _noUrl else None
        link = outLink(
            text,
            href,
            title=title,
            clsName=clsName,
            target=target,
            passage=passageText,
        )

        if _asString:
            return link
        else:
            dh(link)

    def fmt_layoutOrigFull(app, n):
        return app._wrapHtml(n, "text-orig-full")

    def fmt_layoutOrigLite(app, n):
        return app._wrapHtml(n, "text-orig-lite")

    def fmt_layoutTransFull(app, n):
        return app._wrapHtml(n, "text-trans-full")

    def fmt_layoutTransFuzzy(app, n):
        return app._wrapHtml(n, "text-trans-fuzzy")

    def fmt_layoutTransLite(app, n):
        return app._wrapHtml(n, "text-trans-lite")

    def _wrapHtml(app, n, fmt):
        api = app.api
        T = api.T
        F = api.F

        nType = F.otype.v(n)
        material = T.text(n, fmt=fmt, descend=False if nType == "letter" else None)
        material = speakerRe.sub(speakerRepl, material)
        return material
