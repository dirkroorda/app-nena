'''
This module contains code for building the 
North Eastern Neo Aramaic Text-Fabric app,
which visualizes queries and results in TF.
'''

from tf.core.helpers import mdhtmlEsc, htmlEsc
from tf.applib.helpers import dh as display_HTML
from tf.applib.display import prettyPre, getFeatures
from tf.applib.highlight import hlText, hlRep
from tf.applib.api import setupApi
from tf.applib.links import outLink
from textwrap import dedent, indent

# TODO: format user-friendly texts in Github for plain_link to point to.
plain_link = 'https://github.com/{org}/{repo}/blob/master/texts/{dialect}/{text}'

sections = {'dialect', 'title', 'line'}
line = {'line'}
micros = {'char', 'morpheme'}
soft_border = {'prosa'}

# render chars and morphemes without borders when
# they are embedded in another object
blank_styles = {'char', 'morpheme'}

class TFApp:

    '''
    Constructs and delivers HTML for representing
    nodes in the Northeastern Neo-Aramaic TF corpus.
    '''
    
    def __init__(*args, **kwargs):
        '''
        On init, sets up a standard TF api for
        interacting with the corpus.
        '''
        setupApi(*args, **kwargs)
        
    def webLink(app, n, text=None, className=None, _asString=False, _noUrl=False):
        '''
        Formats a HTML link to a source text 
        that contains a supplied TF node.
        
        --input--
        * TF app object
        * TF node
        * kwargs
        
        --output--
        * link string if _asString
        * or display HTML
        '''
        
        # make TF methods available
        api = app.api
        T = api.T
        version = app.version
        
        # format string of node's embedding section
        dialect, text, line = T.sectionFromNode(n, fillup=True)
        passageText = app.sectionStrFromNode(n)
        
        # format the link
        if not _noUrl:
            href = plain_link.format(org=app.org, 
                                     repo=app.repo, 
                                     version=version,
                                     dialect=dialect,
                                     text=text) 
        # or return link to current page
        else:
            href = '#'
            
        # format the link text
        if text is None:
            text = passageText
            title = 'see this passage in its source document'
        else:
            title = passageText
            
        # outLink returns a formatted anchor string
        link = outLink(text, 
                       href, 
                       title=title,
                       className=className,
                       target=target,
                       passage=passageText)
        
        # give the link
        if _asString: 
            return link
         # or show the link 
        else: 
            display_HTML(link)
        
    def _plain(app, n, passage, isLinked, _asString, secLabel, **options):
        '''
        Format a plain HTML representation of a TF node:
        e.g. Barwar A8:1 xá-yuma
        '''
        
        # get display settings
        display = app.display
        opts = display.get(options)
        
        # prepare api methods
        _asApp = app._asApp # determine whether running in browser?
        api = app.api
        L, T, F = api.L, api.T, api.F
        
        # format and return HTML with format {section}{nodeUTF8}
        # the representation of the node depends on the node type and embedding
        otype = F.otype.v(n)
        result = passage
        
        # configure HTML for node number rendering if requested
        if _asApp:
            nodeRep = f' <a href="#" class="nd">{n}</a> ' if d.withNodes else ''
        else:
            nodeRep = f' <i>{n}</i> ' if d.withNodes else ''
            
        # configure object's representation
        
        # configure char-word
        if otype == 'char':
            
            # format text with any highlights
            # e.g. <span  class="hl"  style="background-color: green;">TEXT</span>
            rep = hlText(app, [n], opts.highlights, fmt=opts.fmt)
                        
        # configure sections
        elif otype in sections:
            
            if secLabel and opts.withPassages:
                rep = app.sectionStrFromNode(n)
            else:
                rep = ''
            
            # do not format sections as text segments
            isText = False            
            rep = hlRep(app, rep, n, opts.highlights)
            
            # configure lines to show words as well
            elif otype in line:
                
                # first add link if necessary
                if isLinked:
                    rep = app.webLink(n, text=rep, className='ln', _asString=True)
                else:
                    rep = f'<span class="ln">{rep}</span>'
                
                # then add words from the line
                rep += hlText(app, L.d(n, otype='char'), opts.highlights, fmt=opts.fmt)
                isText = True # treat line like text
                
        # configure all other otypes
        else:
            rep = hlText(app, L.d(n, otype='char'), opts.highlights, fmt=opts.highlights)
            
        # configure links
        if isLinked and otype not in line:
            rep = app.webLink(n, text=rep, _asString=True)
        
        # finalize span and add formatted string
        tClass = display.formatClass[opts.fmt] if isText else 'trb' # div class
        rep = f'<span class="{tClass}">{rep}</span>'
        result += f'{rep}{nodeRep}'
        
        # return as string
        if _asString or _asApp:
            return result
        
        # or display
        else:
            display_HTML(result)
            
    def _pretty(app, n, outer, html, firstSlot, lastSlot, **options):
        '''
        '''
        
        # get display settings
        display = app.display
        opts = display.get(options)
        
        # preprocess and validate node
        pre = prettyPre(app, n, firstSlot, lastSlot, opts.withNodes, opts.highlights)
        
        # error out
        if not pre:
            return
        
        # unpackage preprocessed objects
        slotType = pre[0]
        otype = pre[1]
        className = pre[2]
        boundaryClass = pre[3]
        hlAtt = pre[4]
        nodePart = pre[5]
        myStart = pre[6]
        myEnd = pre[7]
        
        # prepare TF api methods and data
        api = app.api
        L, T = api.L, api.T
        otypeRank = api.otypeRank
        isHtml = options.get('fmt', None) in app.textFormats
        
        # determine size of object
        # objects bigger than condense type will not have
        # any children
        bigType = False
        condense = opts.condenseType
        if condense and otypeRank[otype] > otypeRank[condense]:
            bigType = True
        
        # determine embedded objects to show
        # these will be called recursively
        if bigType:
            children = ()
        elif otype == 'char':
            chldren = ()
        elif otype == 'morpheme':
            children = L.d(n, 'char')
        elif otype == 'word':
            children = list(L.d(n, 'morpheme'))+list(L.d(n, 'char'))
        elif otype == 'prosa':
            children = L.d(n 'word')
        elif otype == 'sentence':
            children = L.d(n, 'prosa')
        elif otype == 'line':
            children = L.d(n, 'sentence')
        else:
            children = L.d(n, otype='word')
            
        # get the highlighting attributes for the object
        hlClass, hlStyle = hlAtt
        
        # determine whether object is outermost object
        # if it is and it is also a micro, toggle showMicro to True
        # this determines whether char/morpheme gets borders and features
        if outer:
            html.append('<div class="outeritem">')
            if otype in micros:
                options['showMicro'] = True
        
        # --
        # open the div for the node
        # set the border attribute accordingly
        # --
        if options['showMicro'] or otype not in soft_border:
            borderClass = 'hard' # line
        elif otype in soft_border:
            borderClass = 'soft' # dotted
        else:
            borderClass = 'clear' # none         
        html.append(f'<div class="{className} {borderClass} {boundaryClass} {hlClass}" {hlStyle}>')
        
        # format section text to appear over all items
        if otype in sections:
            passage = app.webLink(n, _asString=True)
            featurePart = getFeatures(app, n, (), **options)
            
            sectionHTML = f'''
            <div class="vl">
                <div class="line">{passage}</div>
                {nodePart}
                {featurePart}
            </div>
            '''
            sectionHTML = indent(dedent(sectionHTML), '    ')
            html.append(sectionHTML)
            
        # format micro objects
        elif otype in micros:
            text = T.text([n], fmt=opts.fmt)
            textHTML = f'<div class="ara">{text}</div>'
            
            # show node number only if asked
            if nodePart and options['showMicro']:
                html.append(nodePart)
            
        # format word objects
        elif otype == 'word':
            

        # format everything else
        else:
            