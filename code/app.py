"""
This module contains code for building the
North Eastern Neo Aramaic Text-Fabric app,
which visualizes queries and results in TF.
"""

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

sections = {"dialect", "title", "line"}
micros = {"letter", "word"}
soft_border = {"inton"}


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

        descendType = "letter" if d.showChar else "word" if d.showWord else "stress"

        # configure HTML for node number rendering if requested
        if _asApp:
            nodeRep = f' <a href="#" class="nd">{n}</a> ' if d.withNodes else ""
        else:
            nodeRep = f" <i>{n}</i> " if d.withNodes else ""

        # configure object's representation
        isText = d.fmt is None or "-orig-" in d.fmt

        if nType in {"letter", "word", "stress"}:
            rep = hlText(app, [n], d.highlights, fmt=d.fmt)
        elif nType in sections:
            if secLabel and d.withPassage:
                rep = app.sectionStrFromNode(n)
            else:
                rep = ""

            # do not format sections as text segments
            isText = False
            rep = mdhtmlEsc(rep)
            rep = hlRep(app, rep, n, d.highlights)

            # configure lines to show stresses as well
            if nType == "line":

                # first add link if necessary
                if isLinked:
                    rep = app.webLink(n, text=rep, className="ln", _asString=True)
                else:
                    rep = f'<span class="ln">{rep}</span>'

                # then add stresses from the line
                rep += hlText(app, L.d(n, otype=descendType), d.highlights, fmt=d.fmt)
                isText = True  # treat line like text

        else:
            rep = hlText(app, L.d(n, otype=descendType), d.highlights, fmt=d.fmt)

        if isLinked and not passage and nType != "line":
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
        elif nType == "letter":
            children = ()
        elif nType == "word":
            children = L.d(n, "letter") if d.showChar else ()
        elif nType == "stress":
            children = (
                L.d(n, "word") if d.showWord else L.d(n, "letter") if d.showChar else ()
            )
        elif nType == "inton":
            children = L.d(n, "stress")
        elif nType == "sentence":
            children = L.d(n, "inton")
        elif nType == "line":
            children = L.d(n, "sentence")
        else:
            children = L.d(n, otype="stress")

        hlClass, hlStyle = hlAtt

        html.append(f'<div class="{className} {boundaryClass} {hlClass}" {hlStyle}>')

        doShowFeatures = d.showFeatures or (d.showFeatures is None and d.extraFeatures)
        featurePart = getFeatures(app, n, (), **options) if doShowFeatures else ""
        nodePart = nodePart or ""
        nodeHTML = f"{nodePart}{featurePart}"

        if nType in sections:
            passage = app.webLink(n, _asString=True)

            sectionHTML = f"""
            <div class="ll">
                <div class="line">{passage}</div>
                {nodeHTML}
            </div>
            """
            sectionHTML = indent(dedent(sectionHTML), "    ")
            html.append(sectionHTML)
        elif nType == "letter":
            text = T.text([n], fmt=d.fmt)
            text = text if isHtml else htmlEsc(text)
            textHTML = f'<div class="ara">{text}</div>'
            html.append(textHTML)
            html.append(nodeHTML)
        elif nType == "word":
            if not d.showChar:
                text = T.text([n], fmt=d.fmt)
                text = text if isHtml else htmlEsc(text)
                textHTML = f'<div class="ara">{text}</div>'
                html.append(textHTML)
            html.append(nodeHTML)
        elif nType == "stress":
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
