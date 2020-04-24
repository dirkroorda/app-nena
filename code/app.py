import re

from tf.core.helpers import htmlEsc
from tf.applib.api import setupApi


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


speakerRe = re.compile(r"""«([^»]+)»""", re.S)


class TfApp:
    def __init__(app, *args, **kwargs):
        setupApi(app, *args, **kwargs)
        notice(app)

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


def speakerRepl(match):
    return f"""<span class="speaker">{htmlEsc(match.group(1))}</span>"""
