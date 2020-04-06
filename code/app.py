"""
This module contains code for building the
North Eastern Neo Aramaic Text-Fabric app,
which visualizes queries and results in TF.
"""

import re
from tf.core.helpers import mdhtmlEsc, htmlEsc
from tf.applib.helpers import dh as display_HTML
from tf.applib.display import prettyPre, getFeatures
from tf.applib.highlight import hlText, hlRep
from tf.applib.api import setupApi
from tf.applib.links import outLink
from textwrap import dedent, indent

plain_link = (
    "https://github.com/{org}/nena_corpus/blob/master/nena/"
    "{version}/{dialect}/{title}.nena"
)

LETTER = "letter"
WORD = "word"
STRESS = "stress"
INTON = "inton"
SENTENCE = "sentence"

DIALECT = "dialect"
TEXT = "text"
LINE = "line"

SECTIONS = {DIALECT, TEXT, LINE}

speakerRe = re.compile(r"""«([^»]+)»""", re.S)


def speakerRepl(match):
    return f"""<span class="speaker">{htmlEsc(match.group(1))}</span>"""


class TfApp:

    """
    Constructs and delivers HTML for representing
    nodes in the Northeastern Neo-Aramaic TF corpus.
    """

    def __init__(*args, **kwargs):
        """
        On init, sets up a standard TF api for
        interacting with the corpus.
        """
        setupApi(*args, **kwargs)

    def webLink(app, n, text=None, className=None, _asString=False, _noUrl=False):
        """
        Formats a HTML link to a source text
        that contains a supplied TF node.
        """

        # make TF methods available
        api = app.api
        T = api.T
        version = app.version

        # format string of node's embedding section
        dialect, text_title, line = T.sectionFromNode(n, fillup=True)
        passageText = app.sectionStrFromNode(n)

        # format the link
        if not _noUrl:
            href = plain_link.format(
                org=app.org, version=version, dialect=dialect, title=text_title
            )
        # or return link to current page
        else:
            href = "#"

        # format the link text
        if text is None:
            text = passageText
            title = "see this passage in its source document"
        else:
            title = passageText

        # returns a formatted anchor string
        target = "" if _noUrl else None
        link = outLink(
            text,
            href,
            title=title,
            className=className,
            target=target,
            passage=passageText,
        )

        # give the link
        if _asString:
            return link
        # or show the link
        else:
            display_HTML(link)

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
        material = T.text(n, fmt=fmt, descend=False if nType == LETTER else None)
        material = speakerRe.sub(speakerRepl, material)
        return material

    def _plain(app, n, passage, isLinked, _asString, secLabel, **options):
        """
        Format a plain HTML representation of a TF node:
        """

        # get display settings
        display = app.display
        d = display.get(options)

        # prepare api methods
        _asApp = app._asApp  # determine whether running in browser?
        api = app.api
        F = api.F
        L = api.L

        # format and return HTML with format {section}{nodeUTF8}
        # the representation of the node depends on the node type and embedding
        nType = F.otype.v(n)
        result = passage

        descendType = LETTER if d.showChar else WORD if d.showWord else STRESS
        descendOption = dict(descend=False) if descendType == LETTER else {}

        # configure HTML for node number rendering if requested
        if _asApp:
            nodeRep = f' <a href="#" class="nd">{n}</a> ' if d.withNodes else ""
        else:
            nodeRep = f" <i>{n}</i> " if d.withNodes else ""

        # configure object's representation
        isText = d.fmt is None or "-orig-" in d.fmt

        if nType == LETTER:
            rep = hlText(app, n, d.highlights, fmt=d.fmt, descend=False)
        elif nType == WORD:
            rep = (
                hlText(
                    app,
                    L.d(n, otype=descendType),
                    d.highlights,
                    **descendOption,
                    fmt=d.fmt,
                )
                if descendType == LETTER
                else hlText(app, [n], d.highlights, fmt=d.fmt)
            )
        elif nType == STRESS:
            rep = hlText(
                app,
                L.d(n, otype=descendType),
                d.highlights,
                **descendOption,
                fmt=d.fmt,
            )
        elif nType in SECTIONS:
            if secLabel and d.withPassage:
                rep = app.sectionStrFromNode(n)
            else:
                rep = ""

            # do not format sections as text segments
            isText = False
            rep = mdhtmlEsc(rep)
            rep = hlRep(app, rep, n, d.highlights)

            # configure lines to show stresses as well
            if nType == LINE:

                # first add link if necessary
                if isLinked:
                    rep = app.webLink(n, text=rep, className="ln", _asString=True)
                else:
                    rep = f'<span class="ln">{rep}</span>'

                # then add stresses from the line
                rep += hlText(
                    app,
                    L.d(n, otype=descendType),
                    d.highlights,
                    **descendOption,
                    fmt=d.fmt,
                )
                isText = True  # treat line like text

        else:
            rep = hlText(
                app, L.d(n, otype=descendType), d.highlights, **descendOption, fmt=d.fmt
            )

        if isLinked and not passage and nType != LINE:
            rep = app.webLink(n, text=rep, _asString=True)

        tClass = display.formatClass[d.fmt] if isText else "trb"  # div class
        rep = f'<span class="{tClass}">{rep}</span>'
        result += f"{rep}{nodeRep}"

        if _asString or _asApp:
            return result

        else:
            display_HTML(result)

    def _pretty(app, n, outer, html, firstSlot, lastSlot, **options):
        """
        Formats a TF node with pretty HTML formatting.
        """

        display = app.display
        d = display.get(options)

        goOn = prettyPre(app, n, firstSlot, lastSlot, d)

        # error out
        if not goOn:
            return

        goOn = prettyPre(app, n, firstSlot, lastSlot, d)
        if not goOn:
            return
        (
            slotType,
            nType,
            isBigType,
            className,
            boundaryClass,
            hlAtt,
            nodePart,
            myStart,
            myEnd,
        ) = goOn

        api = app.api
        L = api.L
        T = api.T
        isHtml = options.get("fmt", None) in app.textFormats

        if outer:
            html.append('<div class="outeritem">')

        if isBigType:
            children = ()
        elif nType == LETTER:
            children = ()
        elif nType == WORD:
            children = L.d(n, LETTER) if d.showChar else ()
        elif nType == STRESS:
            children = (
                L.d(n, WORD) if d.showWord else L.d(n, LETTER) if d.showChar else ()
            )
        elif nType == INTON:
            children = L.d(n, STRESS)
        elif nType == SENTENCE:
            children = L.d(n, INTON)
        elif nType == LINE:
            children = L.d(n, SENTENCE)
        else:
            children = L.d(n, otype=STRESS)

        hlClass, hlStyle = hlAtt

        html.append(f'<div class="{className} {boundaryClass} {hlClass}" {hlStyle}>')

        doShowFeatures = d.showFeatures or (d.showFeatures is None and d.extraFeatures)
        featurePart = getFeatures(app, n, (), **options) if doShowFeatures else ""
        nodePart = nodePart or ""
        nodeHTML = f"{nodePart}{featurePart}"

        if nType in SECTIONS:
            passage = app.webLink(n, _asString=True)

            sectionHTML = f"""
            <div class="ll">
                <div class="{LINE}">{passage}</div>
                {nodeHTML}
            </div>
            """
            sectionHTML = indent(dedent(sectionHTML), "    ")
            html.append(sectionHTML)
        elif nType == LETTER:
            text = T.text([n], fmt=d.fmt, descend=False)
            text = text if isHtml else htmlEsc(text)
            textHTML = f'<div class="ara">{text}</div>'
            html.append(textHTML)
            html.append(nodeHTML)
        elif nType == WORD:
            if not d.showChar:
                text = T.text([n], fmt=d.fmt)
                text = text if isHtml else htmlEsc(text)
                textHTML = f'<div class="ara">{text}</div>'
                html.append(textHTML)
            html.append(nodeHTML)
        elif nType == STRESS:
            if not (d.showWord or d.showChar):
                text = T.text([n], fmt=d.fmt)
                text = text if isHtml else htmlEsc(text)
                textHTML = f'<div class="ara">{text}</div>'
                html.append(textHTML)
            html.append(nodeHTML)
        else:
            html.append(nodeHTML)

        for child in children:
            app._pretty(child, False, html, firstSlot, lastSlot, **options)

        html.append("</div>")

        if outer:
            html.append("</div>")
