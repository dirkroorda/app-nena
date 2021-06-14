from tf.core.helpers import mdhtmlEsc, htmlEsc
from tf.applib.helpers import dh
from tf.applib.display import prettyPre, getFeatures
from tf.applib.highlight import hlText, hlRep
from tf.applib.api import setupApi
from tf.applib.links import outLink

PLAIN_LINK = 'https://github.com/{org}/{repo}/blob/master/source/{version}/{book}'

SECTION = {'text', 'paragraph', 'line'}
VERSE = {'line'}


class TfApp(object):

  def __init__(*args, **kwargs):
    setupApi(*args, **kwargs)

  def webLink(app, n, text=None, className=None, _asString=False, _noUrl=False):
    api = app.api
    T = api.T
    version = app.version

    (book, chapter, verse) = T.sectionFromNode(n, fillup=True)
    passageText = app.sectionStrFromNode(n)
    href = '#' if _noUrl else PLAIN_LINK.format(
        org=app.org,
        repo=app.repo,
        version=version,
        book=book,
    )
    if text is None:
      text = passageText
      title = 'show this passage in the Peshitta source'
    else:
      title = passageText
    if _noUrl:
      title = None
    target = '' if _noUrl else None
    result = outLink(
        text,
        href,
        title=title,
        className=className,
        target=target,
        passage=passageText,
    )
    if _asString:
      return result
    dh(result)

  def _plain(
      app,
      n,
      passage,
      isLinked,
      _asString,
      secLabel,
      **options,
  ):
    display = app.display
    d = display.get(options)

    _asApp = app._asApp
    api = app.api
    L = api.L
    T = api.T
    F = api.F

    # format and return a string with {rep}{nodeRep}
    # formatting depends on node type and section parts
    
    nType = F.otype.v(n)
    result = passage
    
    # configure HTML for node number rendering
    if _asApp:
      nodeRep = f' <a href="#" class="nd">{n}</a> ' if d.withNodes else ''
    else:
      nodeRep = f' <i>{n}</i> ' if d.withNodes else ''

    # configure object's representation (rep)
    isText = d.fmt is None or '-orig-' in d.fmt
    if nType == 'word':
      rep = hlText(app, [n], d.highlights, fmt=d.fmt)
    elif nType in SECTION:
      if secLabel and d.withPassage:
        label = ('{}' if nType == 'book' else '{} {}' if nType == 'chapter' else '{} {}:{}')
        rep = label.format(*T.sectionFromNode(n))
      else:
        rep = ''
      isText = False
      rep = mdhtmlEsc(rep)
      rep = hlRep(app, rep, n, d.highlights)
      if nType in VERSE:
        if isLinked:
          rep = app.webLink(n, text=rep, className='vn', _asString=True)
        else:
          rep = f'<span class="vn">{rep}</span>'
        rep += hlText(app, L.d(n, otype="word"), d.highlights, fmt=d.fmt)
        isText = True
    else:
      rep = hlText(app, L.d(n, otype='word'), d.highlights, fmt=d.fmt)

    if isLinked and nType not in VERSE:
      rep = app.webLink(n, text=rep, _asString=True)

    tClass = display.formatClass[d.fmt] if isText else 'trb'
    
    print(tClass)
    
    rep = f'<span class="{tClass}">{rep}</span>'
    result += f'{rep}{nodeRep}'

    if _asString or _asApp:
      return result
    dh((result))

  def _pretty(
      app,
      n,
      outer,
      html,
      firstSlot,
      lastSlot,
      **options,
  ):
    display = app.display
    d = display.get(options)

    goOn = prettyPre(
        app,
        n,
        firstSlot,
        lastSlot,
        d.withNodes,
        d.highlights,
    )
    if not goOn:
      return
    (
        slotType,
        nType,
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
    otypeRank = api.otypeRank
    isHtml = options.get('fmt', None) in app.textFormats

    bigType = False
    if d.condenseType is not None and otypeRank[nType] > otypeRank[d.condenseType]:
      bigType = True

    if bigType:
      children = ()
    elif nType == 'verse':
      children = L.d(n, otype='word')
    elif nType == 'lex':
      children = ()
    elif nType == slotType:
      children = ()
    else:
      children = L.d(n, otype='word')

    (hlClass, hlStyle) = hlAtt

    doOuter = outer and nType == slotType
    if doOuter:
      html.append('<div class="outeritem">')

    html.append(f'<div class="{className} {boundaryClass} {hlClass}" {hlStyle}>')

    featurePart = ''

    if nType in SECTION:
      passage = app.webLink(n, _asString=True)
      featurePart = getFeatures(
          app,
          n,
          (),
          **options,
      )
      html.append(
          f'''
    <div class="vl">
        <div class="vrs">{passage}</div>
        {nodePart}
        {featurePart}
    </div>
'''
      )
    else:
      if nodePart:
        html.append(nodePart)

      heading = ''
      featurePart = ''
      occs = ''
      if nType == slotType:
        text = T.text([n], fmt=d.fmt)
        text = text if isHtml else htmlEsc(text)
        tClass = 'sy' if d.fmt is None or '-orig-' in d.fmt else 'tr'
        heading = f'<div class="{tClass}">{text}</div>'
        featurePart = getFeatures(
            app,
            n,
            ('word_etcbc', ),
            **options,
        )
      html.append(heading)
      html.append(featurePart)
      html.append(occs)

    for ch in children:
      app._pretty(
          ch,
          False,
          html,
          firstSlot,
          lastSlot,
          **options,
      )
    html.append('''
</div>
''')
    if doOuter:
      html.append('</div>')
