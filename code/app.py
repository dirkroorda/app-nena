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
micros = {"letter", "morpheme"}
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
        L, F = api.L, api.F

        # format and return HTML with format {section}{nodeUTF8}
        # the representation of the node depends on the node type and embedding
        nType = F.otype.v(n)
        result = passage

        # configure HTML for node number rendering if requested
        if _asApp:
            nodeRep = f' <a href="#" class="nd">{n}</a> ' if d.withNodes else ""
        else:
            nodeRep = f" <i>{n}</i> " if d.withNodes else ""

        # configure object's representation
        isText = d.fmt is None or "-orig-" in d.fmt

        # configure letter
        if nType == "letter":

            # format text with any highlights
            # e.g. <span  class="hl"  style="background-color: green;">TEXT</span>
            rep = hlText(app, [n], d.highlights, fmt=d.fmt)

        # configure sections
        elif nType in sections:

            if secLabel and d.withPassage:
                rep = app.sectionStrFromNode(n)
            else:
                rep = ""

            # do not format sections as text segments
            isText = False
            rep = mdhtmlEsc(rep)
            rep = hlRep(app, rep, n, d.highlights)

            # configure lines to show words as well
            if nType == "line":

                # first add link if necessary
                if isLinked:
                    rep = app.webLink(n, text=rep, className="ln", _asString=True)
                else:
                    rep = f'<span class="ln">{rep}</span>'

                # then add words from the line
                rep += hlText(app, L.d(n, otype="letter"), d.highlights, fmt=d.fmt)
                isText = True  # treat line like text

        # configure all other otypes
        else:
            rep = hlText(app, L.d(n, otype="word"), d.highlights, fmt=d.fmt)

        # configure links

        if isLinked and not passage and nType != "line":
            rep = app.webLink(n, text=rep, _asString=True)

        # finalize span and add formatted string

        tClass = display.formatClass[d.fmt] if isText else "trb"  # div class
        rep = f'<span class="{tClass}">{rep}</span>'
        result += f"{rep}{nodeRep}"

        # return as string
        if _asString or _asApp:
            return result

        # or display
        else:
            display_HTML(result)

    def _pretty(app, n, outer, html, firstSlot, lastSlot, **options):
        """
        Formats a TF node with pretty HTML formatting.
        """

        # get display settings
        display = app.display
        d = display.get(options)

        # preprocess and validate node
        goOn = prettyPre(app, n, firstSlot, lastSlot, d)

        # error out
        if not goOn:
            return

        # unpackage preprocessed data
        # slotType : slot type in database
        # nType : node's object type in database
        # className : default div class for this node type
        # boundaryClass : ?div class for boundary?
        # hlAtt : div class for highlighted nodes
        # nodePart : html repre. of node number
        # myStart : first slot number in node
        # myEnd : last slot number in node

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

        # prepare TF api methods and data
        api = app.api
        F = api.F
        L = api.L
        T = api.T
        isHtml = options.get("fmt", None) in app.textFormats

        # determine whether object is outermost object
        # if it is and it is also a micro, toggle showMicro to True
        # this determines whether letter/morpheme gets borders and features
        if outer:
            html.append('<div class="outeritem">')
            if nType in micros:
                d.showMicro = True

        # skip non-displayed micros
        if nType in micros and not d.showMicro:
            return

        # determine embedded objects to show
        # these will be called recursively
        if isBigType:
            children = ()
        elif nType == "letter":
            children = ()
        elif nType == "morpheme":
            children = L.d(n, "letter")
        elif nType == "word":
            children = L.d(n, "morpheme")
        elif nType == "inton":
            children = L.d(n, "word")
        elif nType == "sentence":
            children = L.d(n, "inton")
        elif nType == "line":
            children = L.d(n, "sentence")
        else:
            children = L.d(n, otype="word")

        # --
        # OPEN the div for the node
        # set the border attribute and other classes accordingly
        # --

        hlClass, hlStyle = hlAtt  # highlighting attributes

        # package it all up:
        html.append(f'<div class="{className} {boundaryClass} {hlClass}" {hlStyle}>')

        # format section text to appear over all items
        doShowFeatures = d.showFeatures or (d.showFeatures is None and d.extraFeatures)

        if nType in sections:
            passage = app.webLink(n, _asString=True)
            featurePart = getFeatures(app, n, (), **options)

            sectionHTML = f"""
            <div class="ll">
                <div class="line">{passage}</div>
                {nodePart}
                {featurePart}
            </div>
            """
            sectionHTML = indent(dedent(sectionHTML), "    ")
            html.append(sectionHTML)

        # format micro objects
        elif nType in micros and d.showMicro:

            if nType == "letter":
                if d.fmt == "text-trans-full":
                    text = F.trans_f.v(n)
                elif d.fmt == "text-trans-lite":
                    text = F.trans_l.v(n)
                else:
                    text = F.text.v(n)
                text = text if isHtml else htmlEsc(text)
                textHTML = f'<div class="ara">{text}</div>'
                html.append(textHTML)

            # show additional features only if asked
            featurePart = getFeatures(app, n, (), **options) if doShowFeatures else ""
            nodePart = nodePart or ""
            nodeHTML = f"{nodePart}{featurePart}"
            html.append(nodeHTML)

        elif nType == "word" and not d.showMicro:
            text = T.text([n], fmt=d.fmt)
            text = text if isHtml else htmlEsc(text)
            textHTML = f'<div class="ara">{text}</div>'
            html.append(textHTML)

            # do features of word
            nodePart = nodePart or ""
            featurePart = getFeatures(app, n, (), **options) if doShowFeatures else ""
            html.append(f"{nodePart}{featurePart}")

        # format everything else
        else:

            # add node number if asked
            nodePart = nodePart or ""
            featurePart = getFeatures(app, n, (), **options) if doShowFeatures else ""
            html.append(f"{nodePart}{featurePart}")

            # for now, do nothing more
            # ...

        # format children with recursive call
        for child in children:
            app._pretty(child, False, html, firstSlot, lastSlot, **options)

        # --
        # CLOSE the node's div
        # --
        html.append("</div>")

        # close outer div if necessary
        if outer:
            html.append("</div>")
