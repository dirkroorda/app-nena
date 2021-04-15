/*eslint-env jquery*/

import { SEARCH, MAXINPUT, NUMBER, QUWINDOW } from "./defs.js"

export class SearchProvider {
/* SEARCH EXECUTION
 *
 * The implementation of layered search:
 *
 * 1. gather:
 *    - match the regular expressions against the texts of the layers
 *    - for each node type, take the intersection of the resulting
 *      nodesets in the layers
 * 2. weed (the heart of the layered search algorithm):
 *    - intersect across node types (using projection to upward and downward levels)
 * 3. compose:
 *    - organize the result nodes around the nodes in a container type
 * 4. display:
 *    - draw the table of results on the interface by screenfuls
 *    - make navigation controls for moving the focus through the table
 */

  constructor() {
    this.getAcro = /[^0-9]/g
    this.tabNl = /[\n\t]/g
  }

  deps({ Log, Disk, State, Gui, Config, Corpus }) {
    this.Log = Log
    this.Disk = Disk
    this.State = State
    this.Gui = Gui
    this.Config = Config
    this.Corpus = Corpus
    this.tell = Log.tell
  }

  async runQuery() {
    /* Performs a complete query
     * The individual substeps each check whether there is something to do
     */

    /* LONG RUNNING FUNCTIONS
     *
     * We apply a device to make behaviour more conspicuous on the interface.
     *
     * There are two problems
     *
     * 1. some actions go so fast, that the user does not see them happening
     * 2. some actions take a lot of time, without the user knowing that he must wait
     *
     * To solve that, we apply some CSS formatting to background and border colors.
     * In order to trigger them, we wrap some functions into this sequence:
     *
     * a. add the CSS class "waiting" to some elements
     * b. run the function in question
     * c. remove the CSS class "waiting" from thiose elements
     *
     * However, when we implement this straightforwardly and synchronously,
     * we do not see any effect, because the browser does not take the trouble
     * to re-render during this sequence.
     *
     * So we need an asynchronous wrapper, and here is what happens:
     *
     * a. add the CSS class "waiting"
     * b. sleep for a fraction of a second
     * c. - now the browser renders the interface and you see the effect of "waiting"
     * d. run the function in question
     * e. remove the CSS class "waiting"
     * f. - when the sequence is done, the browser renders again, and you see the
     *       effect of "waiting" gone
     */

    const { Log, Gui } = this

    const output = $(`#resultsbody,#resultshead`)
    const go = $("#go")
    const expr = $("#exportr")

    Log.progress(`executing query`)
    go.html(SEARCH.exe)
    go.removeClass("dirty")
    go.addClass("waiting")
    output.addClass("waiting")
    /* sleep a number of milliseconds to trigger a rendering of the browser
     */
    await new Promise(r => setTimeout(r, 50))

    this.gather()
    const stats = this.weed()
    Gui.placeStatResults(stats)
    this.composeResults(false)
    this.displayResults()

    go.html(SEARCH.done)
    expr.addClass("active")
    output.removeClass("waiting")
    go.removeClass("waiting")
    $(".dirty").removeClass("dirty")
    Log.progress(`done query`)
  }

  doSearch(nType, layer, lrInfo, regex) {
    /* perform regular expression search for a single layer
     * return character positions and nodes that hold those positions
     */
    const { Corpus: { texts: { [nType]: { [layer]: text } }, positions } } = this
    const { pos: posKey } = lrInfo
    const { [nType]: { [posKey]: pos } } = positions
    const searchResults = text.matchAll(regex)
    const posFromNode = new Map()
    const nodeSet = new Set()
    for (const match of searchResults) {
      const hit = match[0]
      const start = match.index
      const end = start + hit.length
      for (let i = start; i < end; i++) {
        const node = pos[i]
        if (node != null) {
          if (!posFromNode.has(node)) {
            posFromNode.set(node, new Set())
          }
          posFromNode.get(node).add(i)
          nodeSet.add(node)
        }
      }
    }
    return { posFromNode, nodeSet }
  }

  gather() {
    /* perform regular expression search for all layers
     * return for each node type
     *     the intersection of the nodesets found for each layer
     *     for each layer, a mapping of nodes to matched positions
     */
    const { Log, Config: { ntypesR, layers }, State } = this

    const { query } = State.getj()

    State.sets({ resultsComposed: [], resultTypeMap: new Map() })
    const { tpResults } = State.sets({ tpResults: {} })

    for (const nType of ntypesR) {
      const { [nType]: tpInfo = {} } = layers
      const { [nType]: tpQuery } = query
      let intersection = null
      const matchesByLayer = {}

      for (const [layer, lrInfo] of Object.entries(tpInfo)) {
        const box = $(`[kind="pattern"][ntype="${nType}"][layer="${layer}"]`)
        const ebox = $(`[kind="error"][ntype="${nType}"][layer="${layer}"]`)
        Log.clearError(box, ebox)
        const { [layer]: { pattern, flags, exec } } = tpQuery
        if (!exec || pattern.length == 0) {
          continue
        }
        if (pattern.length > MAXINPUT) {
          Log.placeError(
            box,
            ebox,
            `pattern must be less than ${MAXINPUT} characters long`
          )
          continue
        }
        const flagString = Object.entries(flags)
          .filter(x => x[1]).map(x => x[0]).join("")
        let regex
        try {
          regex = new RegExp(pattern, `g${flagString}`)
        } catch (error) {
          Log.placeError(box, ebox, `"${pattern}": ${error}`)
          continue
        }
        const { posFromNode, nodeSet } = this.doSearch(nType, layer, lrInfo, regex)
        matchesByLayer[layer] = posFromNode
        if (intersection == null) {
          intersection = nodeSet
        } else {
          for (const node of intersection) {
            if (!nodeSet.has(node)) {
              intersection.delete(node)
            }
          }
        }
      }
      const matches = matchesByLayer || null
      tpResults[nType] = { matches, nodes: intersection }
    }
  }

  weed() {
    /* combine the search results across node types
     * the current search results will be weeded in place:
     *   the nodesets found per node type will be projected onto other types
     *   and then the intersection with those projected sets will be taken.
     *   This leads to the situation where for each node type there is a nodeset
     *   that maps 1-1 to the nodeset of any other type modulo projection.
     *  returns statistics: how many nodes there are for each type.
     */
    const { Config: { ntypes }, Corpus: { up, down }, State } = this
    const { tpResults } = State.gets()
    const stats = {}

    /* determine highest and lowest types in which a search has been performed
     */
    let hi = null
    let lo = null

    for (let i = 0; i < ntypes.length; i++) {
      const nType = ntypes[i]
      const { [nType]: { nodes } } = tpResults

      if (nodes != null) {
        if (lo == null) {
          lo = i
        }
        hi = i
      }
    }

    /* we are done if no search has been performed
     */
    if (hi == null) {
      return stats
    }

    /*
     * Suppose we have types 0 .. 7 with hi and lo as follows.
     *
     *  0
     *  1
     *  2=hi
     *  3
     *  4
     *  5=lo
     *  6
     *  7
     *
     *  Then we walk through the layers as follows
     *
     *  2 dn 3 dn 4 dn 5
     *  5 up 4 up 3 up 2 up 1 up 0
     *  5 dn 6 dn 7
     */

    /* intersect downwards
     */

    for (let i = hi; i > lo; i--) {
      const upType = ntypes[i]
      const dnType = ntypes[i - 1]
      const { [upType]: { nodes: upNodes }, [dnType]: resultsDn = {} } = tpResults
      let { nodes: dnNodes } = resultsDn
      const dnFree = dnNodes == null

      /* project upnodes downward if there was no search in the down type
       */
      if (dnFree) {
        dnNodes = new Set()
        for (const un of upNodes) {
          if (down.has(un)) {
            for (const dn of down.get(un)) {
              dnNodes.add(dn)
            }
          }
        }
        resultsDn["nodes"] = dnNodes
      }

      /* if there was a search in the down type, weed out the down nodes that
       * have no upward partner in the up nodes
       */
      for (const dn of dnNodes) {
        if (!up.has(dn) || !upNodes.has(up.get(dn))) {
          dnNodes.delete(dn)
        }
      }
    }

    /* intersect upwards (all the way to the top)
     */
    for (let i = lo; i < ntypes.length - 1; i++) {
      const dnType = ntypes[i]
      const upType = ntypes[i + 1]
      const { [upType]: resultsUp = {}, [dnType]: { nodes: dnNodes } } = tpResults

      const upNodes = new Set()
      for (const dn of dnNodes) {
        if (up.has(dn)) {
          upNodes.add(up.get(dn))
        }
      }
      resultsUp["nodes"] = upNodes
    }

    /* project downwards from the lowest level to the bottom type
     */
    for (let i = lo; i > 0; i--) {
      const upType = ntypes[i]
      const dnType = ntypes[i - 1]
      const { [upType]: { nodes: upNodes }, [dnType]: resultsDn = {} } = tpResults
      const dnNodes = new Set()
      for (const un of upNodes) {
        if (down.has(un)) {
          for (const dn of down.get(un)) {
            dnNodes.add(dn)
          }
        }
      }
      resultsDn["nodes"] = dnNodes
    }

    /* collect statistics
     */
    for (const [nType, { nodes }] of Object.entries(tpResults)) {
      stats[nType] = nodes.size
    }
    return stats
  }

  composeResults(recomputeFocus) {
    /* divided search results into chunks by containerType
     * The results are organized by the nodes that have containerType as node type.
     * Each result will have three parts:
     *   ancestor nodes: result nodes of higher types that contain the container node
     *   container node: one node of the containerType
     *   descendant nodes: all descendants of the container node
     * The result at the position that has currently focus on the interface,
     * is marked by means of a class
     *
     * recomputeFocus = true:
     * If we do a new compose because the user has changed the container type
     * we estimate the focus position in the new container type based on the
     * focus position in the old container type
     * We adjust the interface to the new focus pos (slider and number controls)
     */
    const { Config: { ntypesI, utypeOf }, Corpus: { up }, State } = this
    const { tpResults, resultsComposed: oldResultsComposed } = State.gets()

    if (tpResults == null) {
      State.sets({ resultsComposed: null })
      return
    }

    const {
      focusPos: oldFocusPos,
      prevFocusPos: oldPrevFocusPos,
      dirty: oldDirty,
      containerType,
    } = State.getj()

    const { [containerType]: { nodes: containerNodes } = {} } = tpResults

    const oldNResults = oldResultsComposed == null ? 1 : oldResultsComposed.length
    const oldNResultsP = Math.max(oldNResults, 1)
    const oldRelative = oldFocusPos / oldNResultsP
    const oldPrevRelative = oldPrevFocusPos / oldNResultsP

    const {
      resultsComposed, resultTypeMap,
    } = State.sets({ resultsComposed: [], resultTypeMap: new Map() })

    if (containerNodes) {
      for (const cn of containerNodes) {

        /* collect the upnodes
         */
        resultTypeMap.set(cn, containerType)

        let un = cn
        let uType = containerType

        const ancestors = []

        while (up.has(un)) {
          un = up.get(un)
          uType = utypeOf[uType]
          resultTypeMap.set(un, uType)
          ancestors.unshift(un)
        }

        /* collect the down nodes
         */
        const descendants = this.getDescendants(cn, ntypesI.get(containerType))

        resultsComposed.push({ cn, ancestors, descendants })
      }
    }
    const nResults = resultsComposed == null ? 0 : resultsComposed.length
    let focusPos = oldDirty ? -2 : oldFocusPos,
      prevFocusPos = oldDirty ? -2 : oldPrevFocusPos
    if (recomputeFocus) {
      focusPos = Math.min(nResults, Math.round(nResults * oldRelative))
      prevFocusPos = Math.min(nResults, Math.round(nResults * oldPrevRelative))
    } else {
      if (focusPos == -2) {
        focusPos = nResults == 0 ? -1 : 0
        prevFocusPos = -2
      } else if (focusPos > nResults) {
        focusPos = 0
        prevFocusPos = -2
      }
    }

    State.setj({ focusPos, prevFocusPos })
  }

  getDescendants(u, uTypeIndex) {
    /* get all descendents of a node, organized by node type
     * This is an auxiliary function for composeResults()
     * The function calls itself recursively for all the children of
     * the node in a lower level
     * returns an array of subarrays, where each subarray corresponds to a child node
     * and has the form [node, [...descendants of node]]
     */
    if (uTypeIndex == 0) {
      return []
    }

    const { Config: { dtypeOf, ntypes }, Corpus: { down }, State } = this
    const { resultTypeMap } = State.gets()

    const uType = ntypes[uTypeIndex]
    const dType = dtypeOf[uType]
    const dTypeIndex = uTypeIndex - 1

    const dest = []

    for (const d of down.get(u)) {
      resultTypeMap.set(d, dType)
      if (dTypeIndex == 0) {
        dest.push(d)
      } else {
        dest.push([d, this.getDescendants(d, dTypeIndex, resultTypeMap)])
      }
    }
    return dest
  }

  getHLText(iPositions, matches, text, valueMap, tip) {
    /* get highlighted text for a node
     * The results of matching a pattern against a text are highlighted within that text
     * returns a sequence of spans, where a span is an array of postions plus a boolean
     * that indicated whether the span is highlighted or not.
     * Used by display() and tabular() below
     */
    const { getAcro } = this

    const hasMap = valueMap != null

    const spans = []
    let str = ""
    let curHl = null

    for (const i of iPositions) {
      const ch = text[i]
      if (hasMap) {
        str += ch
      }
      const hl = matches.has(i)
      if (curHl == null || curHl != hl) {
        const newSpan = [hl, ch]
        spans.push(newSpan)
        curHl = hl
      } else {
        spans[spans.length - 1][1] += ch
      }
    }
    /* the str that we get back from the node, may contain after-node material
     * and hence is not necessarily a value that we can feed to the valueMap.
     * However, the values that we need for this purpose are purely numeric
     * or the empty string
     */

    const tipStr = (hasMap && tip) ? valueMap[str.replaceAll(getAcro, "")] : null
    return { spans, tipStr }
  }

  getLayers(nType, layers, visibleLayers, includeNodes) {
    const { [nType]: definedLayers = {} } = layers
    const { [nType]: tpVisible } = visibleLayers
    const nodeLayer = includeNodes ? ["_"] : []
    return nodeLayer.concat(Object.keys(definedLayers)).filter(x => tpVisible[x])
  }

  displayResults() {
    /* Displays composed results on the interface.
     * Results are displayed in a table, around a focus position
     * We only display a limited amount of results around the focus position,
     * but the user can move the focus position in various ways.
     * Per result this is visible:
     *   Ancestor nodes are rendered highlighted
     *   The container nodes themselves are rendered as single nodes
     *     if they have content, otherwise they are left out
     *   The descendants of the container node are rendered with
     *   all of descendants (recursively),
     *     where the descendants that have results are highlighted.
     */
    const {
      Config: { simpleBase, layers, ntypesI, ntypesinit },
      Corpus: { texts, iPositions },
      State,
      Gui,
    } = this

    const { resultTypeMap, tpResults, resultsComposed } = State.gets()
    const {
      settings: { nodeseq },
      visibleLayers, focusPos, prevFocusPos,
    } = State.getj()

    if (tpResults == null) {
      State.sets({ resultsComposed: null })
      return
    }

    const genValueHtml = (nType, layer, node) => {
      /* generates the html for a layer of node, including the result highlighting
       */
      if (layer == "_") {
        const num = nodeseq ? node - ntypesinit[nType] + 1 : node
        return `<span class="n">${num}</span>`
      }
      const { [nType]: { [layer]: { pos: posKey, valueMap, tip } } } = layers
      const { [nType]: { [layer]: text } } = texts
      const { [nType]: { [posKey]: iPos } } = iPositions
      const nodeIPositions = iPos.get(node)
      const { [nType]: { matches: { [layer]: matches } = {} } } = tpResults
      const nodeMatches =
        matches == null || !matches.has(node) ? new Set() : matches.get(node)

      const { spans, tipStr } = this.getHLText(
        nodeIPositions, nodeMatches, text, valueMap, tip,
      )
      const hasTip = tipStr != null
      const tipRep = (hasTip) ? ` title="${tipStr}"` : ""

      const html = []
      const multiple = spans.length > 1 || hasTip
      if (multiple) {
        html.push(`<span${tipRep}>`)
      }
      for (const [hl, val] of spans) {
        const hlRep = hl ? ` class="hl"` : ""
        html.push(`<span${hlRep}>${val}</span>`)
      }
      if (multiple) {
        html.push(`</span>`)
      }
      return html.join("")
    }

    const genNodeHtml = node => {
      /* generates the html for a node, including all layers and highlighting
       */
      const [n, children] = typeof node === NUMBER ? [node, []] : node
      const nType = resultTypeMap.get(n)
      const { [nType]: { nodes } = {} } = tpResults
      const tpLayers = this.getLayers(nType, layers, visibleLayers, true)
      const nLayers = tpLayers.length
      const hasLayers = nLayers > 0
      const hasSingleLayer = nLayers == 1
      const hasChildren = children.length > 0
      if (!hasLayers && !hasChildren) {
        return ""
      }

      const hlClass =
        simpleBase && ntypesI.get(nType) == 0 ? "" : nodes.has(n) ? " hlh" : "o"

      const hlRep = hlClass == "" ? "" : ` class="${hlClass}"`
      const lrRep = hasSingleLayer ? "" : ` m`
      const hdRep = hasChildren ? "h" : ""

      const html = []
      html.push(`<span${hlRep}>`)

      if (hasLayers) {
        html.push(`<span class="${hdRep}${lrRep}">`)
        for (const layer of tpLayers) {
          html.push(`${genValueHtml(nType, layer, n)}`)
        }
        html.push(`</span>`)
      }

      if (hasChildren) {
        html.push(`<span>`)
        for (const ch of children) {
          html.push(genNodeHtml(ch))
        }
        html.push(`</span>`)
      }

      html.push(`</span>`)

      return html.join("")
    }

    const genAncestorsHtml = ancestors => {
      /* generates the html for the ancestor nodes of a result
       */
      const html = ancestors.map(anc => genNodeHtml(anc))
      return html.join(" ")
    }

    const genResHtml = (cn, descendants) => {
      /* generates the html for the container node and descendant nodes of a result
       */
      const html = []
      html.push(`${genNodeHtml(cn)} `)
      for (const desc of descendants) {
        html.push(genNodeHtml(desc))
      }
      return html.join("")
    }

    const genResultHtml = (i, result) => {
      /* generates the html for a single result
       */
      const isFocus = i == focusPos
      const isPrevFocus = i == prevFocusPos
      const { ancestors, cn, descendants } = result
      const ancRep = genAncestorsHtml(ancestors)
      const resRep = genResHtml(cn, descendants)
      const focusCls = isFocus
        ? ` class="focus"`
        : isPrevFocus
        ? ` class="pfocus"`
        : ""

      return `
  <tr${focusCls}>
    <th>${i + 1}</th>
    <td>${ancRep}</td>
    <td>${resRep}</td>
  </tr>
    `
    }

    const genResultsHtml = () => {
      /* generates the html for all relevant results around a focus position in the
       * table of results
       */
      if (resultsComposed == null) {
        return ""
      }
      const startPos = Math.max((focusPos || 0) - 2 * QUWINDOW, 0)
      const endPos = Math.min(
        startPos + 4 * QUWINDOW + 1,
        resultsComposed.length - 1
      )
      const html = []
      for (let i = startPos; i <= endPos; i++) {
        html.push(genResultHtml(i, resultsComposed[i], i == focusPos))
      }
      return html.join("")
    }

    const html = genResultsHtml()
    const resultsbody = $("#resultsbody")
    resultsbody.html(html)
    Gui.applyFocus()
  }

  /* RESULTS EXPORT
   * Exports the current results to a tsv file
   * All result nodes will be exported in a table
   * with one node per row:
   * the first column is the node number, the second one is the node type
   * and the layers are the remaining columns
   *
   * N.B. So we do not export composed results, but raw result nodes.
   *
   * The resulting tsv is written in UTF-16-LE encoding for optimal interoperability
   * with Excel
   */
  tabular() {
    const {
      Config: { layers, ntypes, ntypesinit },
      Corpus: { texts, iPositions }, State,
    } = this

    const { settings: { nodeseq } } = State.getj()

    const { tpResults } = State.gets()
    if (tpResults == null) {
      return null
    }
    const { visibleLayers } = State.getj()

    const headFields = ["type"]
    const nodeFields = new Map()

    for (let i = 0; i < ntypes.length; i++) {
      const nType = ntypes[i]
      const { [nType]: { matches, nodes } } = tpResults

      if (nodes == null) {
        continue
      }

      const { [nType]: tpLayerInfo } = layers
      const { [nType]: tpTexts } = texts
      const { [nType]: tpIPositions } = iPositions

      const exportLayers = this.getLayers(nType, layers, visibleLayers, false)
      for (const node of nodes) {
        if (!nodeFields.has(node)) {
          nodeFields.set(node, new Map())
        }
        const fields = nodeFields.get(node)
        fields.set("type", nType)
      }
      for (const layer of exportLayers) {
        const tpLayer = `${nType}-${layer}`
        headFields.push(tpLayer)

        const { [layer]: { pos: posKey, valueMap, tip } } = tpLayerInfo
        const { [layer]: text } = tpTexts
        const { [posKey]: iPos } = tpIPositions
        const { [layer]: lrMatches } = matches

        for (const node of nodes) {
          const fields = nodeFields.get(node)
          fields.set("type", nType)

          const nodeIPositions = iPos.get(node)
          const nodeMatches =
            lrMatches == null || !lrMatches.has(node)
              ? new Set()
              : lrMatches.get(node)
          const { spans, tipStr } = this.getHLText(
            nodeIPositions, nodeMatches, text, valueMap, tip
          )
          const tipRep = (tipStr == null) ? "" : `(=${tipStr})`

          let piece = ""
          for (const [hl, val] of spans) {
            piece += `${hl ? "«" : ""}${val}${hl ? "»" : ""}${tipRep}`
          }
          fields.set(tpLayer, piece.replaceAll(this.tabNl, " "))
        }
      }
    }

    const firstField = nodeseq ? "seqno" : "node"
    const headLine = `${firstField}\t${headFields.join("\t")}\n`
    const lines = [headLine]

    for (let i = 0; i < ntypes.length; i++) {
      const nType = ntypes[i]
      const { [nType]: { nodes } } = tpResults
      if (nodes == null) {
        continue
      }

      const sortedNodes = [...nodes].sort()

      for (const node of sortedNodes) {
        const num = nodeseq ? node - ntypesinit[nType] + 1 : node
        const line = [`${num}`]
        const fields = nodeFields.has(node) ? nodeFields.get(node) : new Map()

        for (const headField of headFields) {
          line.push(fields.has(headField) ? fields.get(headField) : "")
        }
        lines.push(`${line.join("\t")}\n`)
      }
    }

    return lines
  }

  saveResults() {
    /* save job results to file
     * The file will be offered to the user as a download
     */
    const { Disk, State } = this

    const { jobName } = State.gets()
    const lines = this.tabular()
    const text = lines.join("")
    Disk.download(text, jobName, "tsv", true)
  }

}
