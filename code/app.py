import re

from tf.core.helpers import htmlEsc
from tf.applib.app import App


speakerRe = re.compile(r"""«([^»]+)»""", re.S)


def speakerRepl(match):
    return f"""<span class="speaker">{htmlEsc(match.group(1))}</span>"""


class TfApp(App):
    def __init__(app, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
