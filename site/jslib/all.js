/*eslint-env jquery*/
/* global configData */
/* global corpusData */


const DEBUG = true
const BOOL = "boolean"
const NUMBER = "number"
const STRING = "string"
const OBJECT = "object"
const QUWINDOW = 10
const MAXINPUT = 1000
const DEFAULTJOB = "search"
const RESULTCOL = "nr"
const BUTTON = {
  nodeseq: { on: "nodes start at 1", off: "nodes as in text-fabric" },
  autoexec: { on: "auto search", off: "use button to search" },
  exec: { no: " ", on: "⚫️", off: "🔴" },
  visible: { on: "🔵", off: "⚪️" },
  expand: {
    on: "- active layers",
    off: "+ all layers",
    no: "no layers",
  },
}
const UNITTEXT = { r: "row unit", a: "context", d: "content" }
const FLAGSDEFAULT = { i: true, m: true, s: false }
const SEARCH = {
  dirty: "fetch results",
  exe: "fetching ...",
  done: "up to date",
  failed: "failed",
}
const TIP = {
  nodeseq: `node numbers start at 1 for each node types
OR
node numbers are exactly as in Text Fabric`,
  autoexec: `search automatically after each change
OR
only search after you hit the search button`,
  expand: "whether to show inactive layers",
  unit: "make this the row unit",
  exec: "whether this pattern is used in the search",
  visible: "whether this layer is visible in the results",
  visibletp: "whether node numbers are visible in the results",
  flagm: `multiline: ^ and $ match:
ON: around newlines
OFF: at start and end of whole text`,
  flags: `single string: . matches all characters:
ON: including newlines
OFF: excluding newlines"`,
  flagi: `ignore
ON: case-insensitive
OFF: case-sensitive"`,
}


class JobProvider {
  deps({ Log, Disk, Mem, State, Gui }) {
    this.Disk = Disk
    this.Mem = Mem
    this.State = State
    this.Gui = Gui
    this.tell = Log.tell
  }
  init() {
    const { Mem, State } = this
    const [jobName, jobContent] = Mem.getkl()
    State.startj(jobName, jobContent)
  }
  later() {
    const { Gui } = this
    Gui.apply(true)
  }
  list() {
    const { Mem } = this
    return Mem.keys()
  }
  make(newJob) {
    const { State, Gui } = this
    const { jobName } = State.gets()
    if (jobName == newJob) {
      return
    }
    State.startj(newJob, {})
    Gui.apply(true)
  }
  copy(newJob) {
    const { State, Gui } = this
    const { jobName } = State.gets()
    if (jobName == newJob) {
      return
    }
    State.sets({ jobName: newJob })
    Gui.apply(false)
  }
  rename(newJob) {
    const { Mem, State, Gui } = this
    const { jobName } = State.gets()
    if (jobName == newJob) {
      return
    }
    Mem.remk(jobName)
    State.sets({ jobName: newJob })
    Gui.apply(false)
  }
  kill() {
    const { Mem, State } = this
    const { jobName } = State.gets()
    const newJob = Mem.remk(jobName)
    this.change(newJob)
  }
  change(jobName) {
    const { Mem, State, Gui } = this
    const jobContent = Mem.getk(jobName)
    State.startj(jobName, jobContent)
    Gui.apply(true)
  }
  read(elem) {
    const { Disk, State, Gui } = this
    const handler = (fileName, ext, content) => {
      if (ext != ".json") {
        alert(`${fileName}${ext} is not a JSON file`)
        return
      }
      const jobContent = JSON.parse(content)
      State.startj(fileName, jobContent)
      Gui.apply(true)
      Gui.applyJobOptions()
    }
    Disk.upload(elem, handler)
  }
  write() {
    const { State, Disk } = this
    const { jobName } = State.gets()
    const jobState = State.getj()
    const text = JSON.stringify(jobState)
    Disk.download(text, jobName, "json", false)
  }
}


class DiskProvider {
  deps({ Log }) {
    this.tell = Log.tell
  }
  upload(elem, handler) {
    const { files } = elem
    if (files.length == 0) {
      alert("No file selected")
    } else {
      for (const file of files) {
        const reader = new FileReader()
        const [fileName, ext] = file.name.match(/([^/]+)(\.[^.]*$)/).slice(1)
        reader.onload = e => {
          handler(fileName, ext, e.target.result)
        }
        reader.readAsText(file)
      }
    }
  }
  download(text, fileName, ext, asUtf16) {
    let blob
    if (asUtf16) {
      const byteArray = []
      byteArray.push(255, 254)
      for (let i = 0; i < text.length; ++i) {
        const charCode = text.charCodeAt(i)
        byteArray.push(charCode & 0xff)
        byteArray.push((charCode / 256) >>> 0)
      }
      blob = new Blob(
        [new Uint8Array(byteArray)], { type: "text/plain;charset=UTF-16LE;" }
      )
    } else {
      blob = new Blob([text], { type: "text/plain;charset=UTF-8;" })
    }
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.setAttribute("href", url)
    link.setAttribute("download", `${fileName}.${ext}`)
    link.style.visibility = "hidden"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}



class LogProvider {
  deps({ Log }) {
    this.tell = Log.tell
  }
  init() {
    this.tell("!!! IS ON !!!")
    this.place = $("#progress")
    this.clearProgress()
    this.placeProgress("Javascript has kicked in.")
  }
  async later() {
    this.placeProgress("Done ...")
    await new Promise(r => setTimeout(r, 1000))
    this.clearProgress()
  }
  clearProgress() {
    this.place.html("")
  }
  placeProgress(msg) {
    this.place.append(`${msg}<br>`)
  }
  progress(msg) {
    console.log(msg)
  }
  clearError(ebox, box) {
    ebox.html("")
    ebox.hide()
    if (box != null) {
      box.removeClass("error")
    }
  }
  placeError(ebox, msg, box) {
    console.error(msg)
    ebox.show()
    ebox.html(msg)
    if (box != null) {
      box.addClass("error")
    }
  }
  error(msg) {
    console.error(msg)
  }
  tell(msg) {
    if (DEBUG) {
      console.log("DEBUG", msg)
    }
  }
}



class ConfigProvider {
  deps({ Log }) {
    this.tell = Log.tell
  }
  init() {
    const {
      defs: { appVersion, org, repo, name, description, urls, captions },
      levels,
      containerType, simpleBase,
      ntypes, ntypesinit, ntypessize,
      utypeOf, dtypeOf,
      layers, visible,
    } = configData
    this.appVersion = appVersion
    this.org = org
    this.repo = repo
    this.name = name
    this.description = description
    this.levels = levels
    this.urls = urls
    this.captions = captions
    this.simpleBase = simpleBase
    this.layers = layers
    this.visible = visible
    this.ntypes = ntypes
    this.ntypesinit = ntypesinit
    this.ntypessize = ntypessize
    this.utypeOf = utypeOf
    this.dtypeOf = dtypeOf
    const pos = Math.round(ntypes.length / 2)
    this.containerType = containerType || ntypes[pos]
    this.ntypesR = [...ntypes]
    this.ntypesR.reverse()
    const ntypesI = new Map()
    for (let i = 0; i < ntypes.length; i++) {
      ntypesI.set(ntypes[i], i)
    }
    this.ntypesI = ntypesI
  }
}



class CorpusProvider {
  deps({ Log }) {
    this.Log = Log
    this.tell = Log.tell
  }
  later() {
    const { texts, positions } = corpusData
    this.texts = texts
    this.positions = positions
    this.warmUpData()
  }
  warmUpData() {
    const { Log } = this
    Log.progress(`Decompress up-relation and infer down-relation`)
    this.decompress()
    Log.progress(`Infer inverted position maps`)
    this.invertPositionMaps()
    Log.progress(`Done`)
  }
  decompress() {
    const { up } = corpusData
    const newUp = new Map()
    const down = new Map()
    for (const line of up) {
      const [spec, uStr] = line.split("\t")
      const u = uStr >> 0
      if (!down.has(u)) {
        down.set(u, new Set())
      }
      const ns = []
      const ranges = spec.split(",")
      for (const range of ranges) {
        const bounds = range.split("-").map(x => x >> 0)
        if (bounds.length == 1) {
          ns.push(bounds[0])
        } else {
          for (let i = bounds[0]; i <= bounds[1]; i++) {
            ns.push(i)
          }
        }
      }
      const downs = down.get(u)
      for (const n of ns) {
        newUp.set(n, u)
        downs.add(n)
      }
    }
    this.up = newUp
    this.down = down
  }
  invertPositionMaps() {
    const { positions } = this
    const iPositions = {}
    for (const [nType, tpInfo] of Object.entries(positions)) {
      for (const [layer, pos] of Object.entries(tpInfo)) {
        const iPos = new Map()
        for (let i = 0; i < pos.length; i++) {
          const node = pos[i]
          if (node == null) {
            continue
          }
          if (!iPos.has(node)) {
            iPos.set(node, [])
          }
          iPos.get(node).push(i)
        }
        if (iPositions[nType] == null) {
          iPositions[nType] = {}
        }
        iPositions[nType][layer] = iPos
      }
    }
    this.iPositions = iPositions
  }
}



class StateProvider {
  deps({ Log, Mem, Config }) {
    this.Log = Log
    this.Mem = Mem
    this.Config = Config
    this.tell = Log.tell
  }
  init() {
    this.data = {
      tpResults: null,
      resultsComposed: null,
      resultTypeMap: null,
      jobName: null,
      jobState: this.initjslice(),
    }
  }
  initjslice() {
    const { Config: { ntypes, containerType, layers, visible } } = this
    const jobState = {
      settings: {
        autoexec: true,
        nodeseq: true,
      },
      query: {},
      dirty: false,
      expandTypes: {},
      containerType,
      visibleLayers: {},
      focusPos: -2,
      prevFocusPos: -2,
    }
    const { query, expandTypes, visibleLayers } = jobState
    for (const nType of ntypes) {
      const { [nType]: tpInfo = {} } = layers
      const { [nType]: tpVisible = {} } = visible
      query[nType] = {}
      expandTypes[nType] = false
      visibleLayers[nType] = { _: false }
      for (const layer of Object.keys(tpInfo)) {
        const { [layer]: { pattern = "" } = {} } = tpInfo
        const { [layer]: lrVisible = false } = tpVisible
        query[nType][layer] = {
          pattern: DEBUG ? pattern : "",
          flags: { ...FLAGSDEFAULT },
          exec: true,
        }
        visibleLayers[nType][layer] = lrVisible
      }
    }
    return jobState
  }
  startjslice(incoming) {
    const { data } = this
    const freshJobState = this.initjslice()
    this.merge(freshJobState, incoming, [])
    data.jobState = freshJobState
  }
  gets() {
    const { data: { jobState, ...rest } } = this
    return rest
  }
  getjn() {
    const { data: { jobName } } = this
    return jobName
  }
  sets(incoming) {
    const { Log, Mem, data } = this
    let commit = false
    for (const [inKey, inValue] of Object.entries(incoming)) {
      const stateVal = data[inKey]
      if (stateVal === undefined) {
        Log.error(`state update: unknown key ${inKey}`)
        continue
      }
      data[inKey] = inValue
      if (inKey == "jobName" || inKey == "jobState") {
        commit = true
      }
    }
    if (commit) {
      const { jobName, jobState } = data
      Mem.setk(jobName, jobState)
    }
    return this.gets()
  }
  startj(jobIn, jobStateIn) {
    const { Mem, data } = this
    const jobName = jobIn || DEFAULTJOB
    data.jobName = jobName
    this.startjslice(jobStateIn)
    const { jobState } = data
    Mem.setk(jobName, jobState)
  }
  getj() {
    const { data: { jobState } } = this
    return JSON.parse(JSON.stringify(jobState))
  }
  setj(incoming) {
    const { Mem, data: { jobName, jobState } } = this
    this.merge(jobState, incoming, [])
    Mem.setk(jobName, jobState)
  }
  merge(orig, incoming, path) {
    const { Log } = this
    const pRep = `Merge: incoming at path "${path.join(".")}": `
    if (incoming == null) {
      Log.error(`${pRep}undefined`)
      return
    }
    if (!(typeof incoming === OBJECT && !Array.isArray(incoming))) {
      Log.error(`${pRep}non-object`)
      return
    }
    for (const [inKey, inValue] of Object.entries(incoming)) {
      const origValue = orig[inKey]
      if (origValue === undefined) {
        Log.error(`${pRep}unknown key ${inKey}`)
        continue
      }
      if (inValue == null) {
        Log.error(`${pRep}undefined value for ${inKey}`)
        continue
      }
      const origType = typeof origValue
      const inType = typeof inValue
      if (origType === NUMBER || origType === STRING || origType === BOOL) {
        if (inType === OBJECT) {
          const repVal = JSON.stringify(inValue)
          Log.error(`${pRep}object ${repVal} for ${inKey} instead of leaf value`)
          continue
        }
        if (inType != origType) {
          Log.error(`${pRep}type conflict ${inType}, expected ${origType} for ${inKey}`)
          continue
        }
        if (inType === STRING && inValue.length > MAXINPUT) {
          const eRep = `${inValue.length} (${inValue.substr(0, 20)} ...)`
          Log.error(`${pRep}maximum length exceeded for ${inKey}: ${eRep}`)
          continue
        }
        orig[inKey] = inValue
        continue
      }
      if (origType !== OBJECT) {
        Log.error(
          `${pRep}unknown type ${inType} for ${inKey}=${inValue} instead of object`
        )
        continue
      }
      if (origType === OBJECT) {
        if (inType !== OBJECT) {
          Log.error(`${pRep}leaf value {inValue} for {inKey} instead of object`)
          continue
        }
        this.merge(origValue, inValue, [...path, inKey])
      }
    }
  }
}



class GuiProvider {
  deps({ Log, State, Job, Config, Search }) {
    this.State = State
    this.Job = Job
    this.Config = Config
    this.Search = Search
    this.tell = Log.tell
  }
  init() {
    this.build()
    this.activateJobs()
    this.activateSearch()
  }
  build() {
    const {
      Config: {
        ntypesR,
        appVersion,
        description,
        urls,
        captions: { title },
        layers, levels,
      },
    } = this
    $("head>title").html(title)
    $("#title").html(title)
    $("#description").html(description)
    $("#appversion").html(appVersion.replace(/@/, " @ "))
    $("go").html(SEARCH.dirty)
    const querybody = $("#querybody")
    const html = []
    for (const nType of ntypesR) {
      const tpInfo = layers[nType] || {}
      const description = levels[nType] || {}
      html.push(this.genTypeWidgets(nType, description, tpInfo))
    }
    querybody.html(html.join(""))
    this.placeStatTotals()
    this.placeSettings()
    for (const [kind, [linkText, linkHref, linkTitle]] of Object.entries(urls)) {
      const elem = $(`#${kind}link`)
      elem.attr("target", "_blank")
      elem.attr("title", linkTitle)
      elem.attr("href", linkHref)
      if (linkText != null) {
        elem.html(linkText)
      }
    }
  }
  placeSettings() {
    const { State } = this
    const { settings } = State.getj()
    const html = []
    for (const name of Object.keys(settings)) {
      html.push(`
        <p><button
          type="button" name="${name}" class="expand on"
        ></button></p>
      `)
    }
    const settingsplace = $("#settings")
    settingsplace.html(html.join(""))
  }
  placeStatTotals() {
    const { Config: { ntypesR, ntypessize } } = this
    const html = []
    for (const nType of ntypesR) {
      const total = ntypessize[nType]
      html.push(`
  <tr class="stat" ntype="${nType}">
    <td><span class="statlabel">${nType}</span></td>
    <td class="stat"><span class="stattotal">${total}</span></td>
    <td class="stat"><span class="statresult" ntype="${nType}"></span></td>
  </tr>
  `)
    }
    const statsbody = $("#statsbody")
    statsbody.html(html.join(""))
  }
  placeStatResults(stats) {
    const { Config: { ntypes } } = this
    for (const nType of ntypes) {
      const dest = $(`.statresult[ntype="${nType}"]`)
      const stat = stats[nType]
      const useStat = (stat == null) ? " " : stat
      dest.html(`${useStat}`)
    }
  }
  genTypeWidgets(nType, description, tpInfo) {
    const nTypeRep = description
      ? `<details>
           <summary class="lv">${nType}</summary>
           <div>${description}</div>
          </details>`
      : `<span class="lv">${nType}</span>`
    const html = []
    html.push(`
  <tr class="qtype" ntype="${nType}">
    <td class="lvcell">${nTypeRep}</td>
    <td><button type="button" name="expand" class="expand"
      ntype="${nType}"
      title="${TIP.expand}"
    ></button></td>
    <td><button type="button" name="ctype" class="unit"
      ntype="${nType}"
      title="${TIP.unit}"
    >result</button></td>
    <td></td>
    <td><button type="button" name="visible" class="visible"
      ntype="${nType}" layer="_"
      title="${TIP.visibletp}"
    ></button></td>
  </tr>
  `)
    for (const [layer, lrInfo] of Object.entries(tpInfo)) {
      html.push(this.genWidget(nType, layer, lrInfo))
    }
    return html.join("")
  }
  genWidget(nType, layer, lrInfo) {
   return (
    `
  <tr class="ltype" ntype="${nType}" layer="${layer}">
    <td>${this.genLegend(nType, layer, lrInfo)}</td>
    <td>
      /<input type="text" kind="pattern" class="pattern"
        ntype="${nType}" layer="${layer}"
        maxlength="${MAXINPUT}"
        value=""
      ><span kind="error" class="error"
        ntype="${nType}" layer="${layer}"
      ></span>/</td>
    <td><button type="button" name="i" class="flags"
        ntype="${nType}" layer="${layer}"
        title="${TIP.flagi}"
      >i</button><button type="button" name="m" class="flags"
        ntype="${nType}" layer="${layer}"
        title="${TIP.flagm}"
      >m</button><button type="button" name="s" class="flags"
        ntype="${nType}" layer="${layer}"
        title="${TIP.flags}"
      >s</button>
    </td>
    <td><button type="button" name="exec" class="exec"
      ntype="${nType}" layer="${layer}"
      title="${TIP.exec}"
    ></button></td>
    <td><button type="button" name="visible" class="visible"
      ntype="${nType}" layer="${layer}"
      title="${TIP.visible}"
    ></button></td>
  </tr>
  `)
  }
  genLegend(nType, layer, lrInfo) {
    const { valueMap, description } = lrInfo
    const html = []
    if (valueMap || description) {
      html.push(`
  <details>
    <summary class="lyr">${layer}</summary>
  `)
      if (description) {
        html.push(`<div>${description}</div>`)
      }
      if (valueMap) {
        for (const [acro, full] of Object.entries(valueMap)) {
          html.push(`
  <div class="legend">
    <b><code>${acro}</code></b> =
    <i><code>${full}</code></i>
  </div>`
          )
        }
      }
      html.push(`
  </details>
  `)
    } else {
      html.push(`
  <span class="lyr">${layer}</span>
  `)
    }
    return html.join("")
  }
  activateJobs() {
    const { State, Job } = this
    const jobnew = $("#newj")
    const jobdup = $("#dupj")
    const jobrename = $("#renamej")
    const jobkill = $("#deletej")
    const jobchange = $("#jchange")
    jobnew.off("click").click(() => {
      const newJob = this.suggestName(null)
      if (newJob == null) {
        return
      }
      Job.make(newJob)
      this.applyJobOptions(true)
    })
    jobdup.off("click").click(() => {
      const { jobName } = State.gets()
      const newJob = this.suggestName(jobName)
      if (newJob == null) {
        return
      }
      Job.copy(newJob)
      this.applyJobOptions(true)
    })
    jobrename.off("click").click(() => {
      const { jobName } = State.gets()
      const newJob = this.suggestName(jobName)
      if (newJob == null) {
        return
      }
      Job.rename(newJob)
      this.applyJobOptions(true)
    })
    jobkill.off("click").click(() => {
      Job.kill()
      this.applyJobOptions(true)
    })
    jobchange.change(e => {
      const { jobName } = State.gets()
      const newJob = e.target.value
      if (jobName == newJob) {
        return
      }
      Job.change(newJob)
      this.clearBrowserState()
    })
    const fileSelect = $("#importj")
    const fileElem = $("#imjname")
    fileSelect.off("click").click(e => {
      fileElem.click()
      e.preventDefault()
    })
    fileElem.off("change").change(e => Job.read(e.target))
    const expjButton = $("#exportj")
    expjButton.off("click").click(() => {
      Job.write()
    })
  }
  suggestName(jobName) {
    const { Job } = this
    const jobNames = new Set(Job.list())
    let newName = jobName
    const resolved = s => s && s != jobName && !jobNames.has(s)
    let cancelled = false
    while (!resolved(newName) && !cancelled) {
      while (!resolved(newName)) {
        if (newName == null) {
          newName = DEFAULTJOB
        } else {
          newName += "N"
        }
      }
      if (jobName != null) {
        const answer = prompt("New job name:", newName)
        if (answer == null) {
          cancelled = true
        } else {
          newName = answer
        }
      }
    }
    return cancelled ? null : newName
  }
  activateSearch() {
    const { State, Search } = this
    const go = $(`#go`)
    const handleQuery = e => {
      e.preventDefault()
      go.off("click")
      Search.runQuery({ allSteps: true })
      State.setj({ dirty: false })
      this.clearBrowserState()
      go.click(handleQuery)
    }
    go.off("click").click(handleQuery)
    const settingctls = $("#settings button")
    settingctls.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const name = elem.attr("name")
      const isNo = elem.hasClass("no")
      if (!isNo) {
        const isOn = elem.hasClass("on")
        State.setj({ settings: { [name]: !isOn } })
        this.applySettings(name)
        if (name == "nodeseq") {
          Search.runQuery({ display: [] })
        }
      }
      this.clearBrowserState()
    })
    const expands = $(`button[name="expand"]`)
    expands.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const nType = elem.attr("ntype")
      const isNo = elem.hasClass("no")
      if (!isNo) {
        const isOn = elem.hasClass("on")
        State.setj({ expandTypes: { [nType]: !isOn } })
        this.applyLayers(nType)
      }
      this.clearBrowserState()
    })
    const units = $(`button[name="ctype"]`)
    units.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const nType = elem.attr("ntype")
      const { containerType } = State.getj()
      if (nType == containerType) {
        return
      }
      State.setj({ containerType: nType })
      Search.runQuery({ compose: [true] })
      Search.runQuery({ display: [] })
      this.applyContainer(nType)
      this.clearBrowserState()
    })
    const patterns = $(`input[kind="pattern"]`)
    patterns.off("change").change(e => {
      const elem = $(e.target)
      const nType = elem.attr("ntype")
      const layer = elem.attr("layer")
      const { target: { value: pattern } } = e
      this.makeDirty(elem)
      State.setj({ query: { [nType]: { [layer]: { pattern } } } })
      const { settings: { autoexec } } = State.getj()
      if (autoexec) {
        Search.runQuery({ allSteps: true })
      }
      this.applyExec(nType, layer)
      this.clearBrowserState()
    })
    const errors = $(`[kind="error"]`)
    errors.hide()
    const flags = $(`button.flags`)
    flags.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const name = elem.attr("name")
      const nType = elem.attr("ntype")
      const layer = elem.attr("layer")
      const isOn = elem.hasClass("on")
      this.makeDirty(elem)
      State.setj({ query: { [nType]: { [layer]: { flags: { [name]: !isOn } } } } })
      const { settings: { autoexec } } = State.getj()
      if (autoexec) {
        Search.runQuery({ allSteps: true })
      }
      this.setButton(name, `[ntype="${nType}"][layer="${layer}"]`, !isOn)
      this.clearBrowserState()
    })
    const execs = $(`button.exec`)
    execs.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const nType = elem.attr("ntype")
      const layer = elem.attr("layer")
      const isNo = elem.hasClass("no")
      if (!isNo) {
        const isOn = elem.hasClass("on")
        this.makeDirty(elem)
        State.setj({ query: { [nType]: { [layer]: { exec: !isOn } } } })
        const { settings: { autoexec } } = State.getj()
        if (autoexec) {
          Search.runQuery({ allSteps: true })
        }
        this.setButton("exec", `[ntype="${nType}"][layer="${layer}"]`, !isOn, true)
      }
      this.clearBrowserState()
    })
    const visibles = $(`button.visible`)
    visibles.off("click").click(e => {
      e.preventDefault()
      const elem = $(e.target)
      const nType = elem.attr("ntype")
      const layer = elem.attr("layer")
      const isOn = elem.hasClass("on")
      State.setj({ visibleLayers: { [nType]: { [layer]: !isOn } } })
      this.setButton(
        "visible", `[ntype="${nType}"][layer="${layer}"]`, !isOn, true,
      )
      Search.runQuery({ display: [] })
      this.clearBrowserState()
    })
    this.activateResults()
    const exprButton = $("#exportr")
    exprButton.off("click").click(() => {
      const { tpResults } = State.gets()
      if (tpResults == null) {
        alert("Query has not been executed yet")
        return
      }
      Search.saveResults()
    })
  }
  makeDirty(elem) {
    const { State } = this
    const go = $("#go")
    const expr = $("#exportr")
    elem.addClass("dirty")
    go.addClass("dirty")
    go.html(SEARCH.dirty)
    expr.removeClass("active")
    State.setj({ dirty: true })
  }
  activateResults() {
    const { State, Search } = this
    const slider = $("#slider")
    const setter = $("#setter")
    const minp = $("#minp")
    const min2p = $("#min2p")
    const mina = $("#mina")
    const maxp = $("#maxp")
    const max2p = $("#max2p")
    const maxa = $("#maxa")
    slider.off("change").change(() => {
      const { focusPos } = State.getj()
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(slider.val() - 1),
      })
      Search.runQuery({ display: [] })
    })
    setter.off("change").change(() => {
      const { focusPos } = State.getj()
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(setter.val() - 1),
      })
      Search.runQuery({ display: [] })
    })
    minp.off("click").click(() => {
      const { focusPos } = State.getj()
      if (focusPos == -2) {
        return
      }
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(focusPos - 1),
      })
      Search.runQuery({ display: [] })
    })
    min2p.off("click").click(() => {
      const { focusPos } = State.getj()
      if (focusPos == -2) {
        return
      }
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(focusPos - QUWINDOW),
      })
      Search.runQuery({ display: [] })
    })
    mina.off("click").click(() => {
      const { focusPos } = State.getj()
      if (focusPos == -2) {
        return
      }
      State.setj({ prevFocusPos: focusPos, focusPos: 0 })
      Search.runQuery({ display: [] })
    })
    maxp.off("click").click(() => {
      const { focusPos } = State.getj()
      if (focusPos == -2) {
        return
      }
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(focusPos + 1),
      })
      Search.runQuery({ display: [] })
    })
    max2p.off("click").click(() => {
      const { focusPos } = State.getj()
      if (focusPos == -2) {
        return
      }
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(focusPos + QUWINDOW),
      })
      Search.runQuery({ display: [] })
    })
    maxa.off("click").click(() => {
      const { focusPos } = State.getj()
      if (focusPos == -2) {
        return
      }
      State.setj({
        prevFocusPos: focusPos, focusPos: this.checkFocus(-1),
      })
      Search.runQuery({ display: [] })
    })
  }
  apply(run) {
    this.applyJobOptions()
    this.applySettings()
    this.applyQuery()
    this.applyResults(run)
    this.clearBrowserState()
  }
  applyQuery() {
    const { Config, State } = this
    const { ntypes, layers } = Config
    const { query, containerType, visibleLayers } = State.getj()
    for (const nType of ntypes) {
      const { [nType]: tpInfo = {} } = layers
      const { [nType]: tpQuery } = query
      const { [nType]: tpVisible } = visibleLayers
      this.applyLayers(nType)
      const { _: visibleNodes } = tpVisible
      this.setButton("visible", `[ntype="${nType}"][layer="_"]`, visibleNodes, true)
      for (const layer of Object.keys(tpInfo)) {
        const { [layer]: { pattern, flags } } = tpQuery
        const box = $(`[kind="pattern"][ntype="${nType}"][layer="${layer}"]`)
        box.val(pattern)
        const useFlags = { ...FLAGSDEFAULT, ...flags }
        for (const [flag, isOn] of Object.entries(useFlags)) {
          this.setButton(flag, `[ntype="${nType}"][layer="${layer}"]`, isOn)
        }
        this.applyExec(nType, layer)
        const { [layer]: visible } = tpVisible
        this.setButton(
          "visible", `[ntype="${nType}"][layer="${layer}"]`, visible, true,
        )
      }
    }
    this.applyContainer(containerType)
  }
  applyExec(nType, layer) {
    const { State } = this
    const { query: { [nType]: { [layer]: { pattern, exec } } } } = State.getj()
    const useExec = pattern.length == 0 ? null : exec
    this.setButton("exec", `[ntype="${nType}"][layer="${layer}"]`, useExec, true)
  }
  applyJobOptions(clear) {
    const { Job, State } = this
    const { jobName } = State.gets()
    const jobchange = $("#jchange")
    const jobname = $("#jobname")
    let html = ""
    for (const otherJobName of Job.list()) {
      const selected = otherJobName == jobName ? " selected" : ""
      html += `<option value="${otherJobName}"${selected}>${otherJobName}</option>`
      jobchange.html(html)
    }
    jobchange.val(jobName)
    jobname.val(jobName)
    if (clear) {
      this.clearBrowserState()
    }
  }
  applySettings(name) {
    const { State } = this
    const { settings } = State.getj()
    const tasks = (name == null) ? Object.entries(settings) : [[name, settings[name]]]
    for (const [name, setting] of tasks) {
      this.setButton(name, "", setting, true)
    }
  }
  applyLayers(nType) {
    const { Config: { layers: { [nType]: tpLayers = {} } = {} }, State } = this
    const {
      expandTypes: { [nType]: expand },
      visibleLayers: { [nType]: tpVisible },
      query: { [nType]: tpQuery },
    } = State.getj()
    const totalLayers = Object.keys(tpLayers).length
    const useExpand = (totalLayers == 0) ? null : expand
    let totalActive = 0
    for (const layer of Object.keys(tpLayers)) {
      const row = $(`.ltype[ntype="${nType}"][layer="${layer}"]`)
      const { [layer]: { pattern } } = tpQuery
      const { [layer]: visible } = tpVisible
      const isActive = visible || pattern.length > 0
      if (isActive) {
        totalActive += 1
      }
      if (expand || isActive) {
        row.show()
      }
      else {
        row.hide()
      }
    }
    const { expand: { no, on, off } } = BUTTON
    const expandText = {
      no,
      on: `${on}(${totalActive})`,
      off: `${off}(${totalLayers})`,
    }
    this.setButton("expand", `[ntype="${nType}"]`, useExpand, expandText)
  }
  applyContainer(containerType) {
    const { Config: { ntypes, ntypesI } } = this
    const containerIndex = ntypesI.get(containerType)
    for (const nType of ntypes) {
      const nTypeIndex = ntypesI.get(nType)
      const k = (containerIndex == nTypeIndex)
        ? "r" : (containerIndex < nTypeIndex)
        ? "a" : "d"
      const elem = $(`button[name="ctype"][ntype="${nType}"]`)
      elem.html(UNITTEXT[k])
    }
    this.setButton("ctype", ``, false)
    this.setButton("ctype", `[ntype="${containerType}"]`, true)
    const statRows = $(`tr.stat`)
    const statContainer = $(`tr.stat[ntype="${containerType}"]`)
    statRows.removeClass("focus")
    statContainer.addClass("focus")
  }
  applyResults(run) {
    // const { State, Search } = this
    const { Search } = this
    if (run) {
      Search.runQuery({ allSteps: true })
    }
  }
  applyFocus() {
    const { State } = this
    const { resultsComposed } = State.gets()
    const { focusPos } = State.getj()
    const setter = $("#setter")
    const setterw = $("#setterw")
    const slider = $("#slider")
    const sliderw = $("#sliderw")
    const total = $("#total")
    const totalw = $("#totalw")
    const minp = $("#minp")
    const min2p = $("#min2p")
    const mina = $("#mina")
    const maxp = $("#maxp")
    const max2p = $("#max2p")
    const maxa = $("#maxa")
    const nResults = resultsComposed == null ? 0 : resultsComposed.length
    const nResultsP = Math.max(nResults, 1)
    const stepSize = Math.max(Math.round(nResults / 100), 1)
    const focusVal = focusPos == -2 ? 0 : focusPos + 1
    const totalVal = focusPos == -2 ? 0 : nResults
    setter.attr("max", nResultsP)
    setter.attr("step", stepSize)
    slider.attr("max", nResultsP)
    slider.attr("step", stepSize)
    setter.val(focusVal)
    slider.val(focusVal)
    total.html(totalVal)
    sliderw.hide()
    setterw.hide()
    totalw.hide()
    minp.removeClass("active")
    min2p.removeClass("active")
    mina.removeClass("active")
    maxp.removeClass("active")
    max2p.removeClass("active")
    maxa.removeClass("active")
    if (focusPos != -2) {
      setterw.show()
      totalw.show()
      if (nResults > 2 * QUWINDOW) {
        sliderw.show()
      }
      if (focusPos < nResults - 1) {
        maxa.addClass("active")
        maxp.addClass("active")
      }
      if (focusPos + QUWINDOW < nResults - 1) {
        max2p.addClass("active")
      }
      if (focusPos > 0) {
        mina.addClass("active")
        minp.addClass("active")
      }
      if (focusPos - QUWINDOW > 0) {
        min2p.addClass("active")
      }
    }
    const rTarget = $(`.focus`)
    if (rTarget != null && rTarget[0] != null) {
      rTarget[0].scrollIntoView({ block: "center", behavior: "smooth" })
    }
  }
  setButton(name, spec, onoff, changeTag) {
    const elem = $(`button[name="${name}"]${spec}`)
    if (onoff == null) {
      elem.removeClass("on")
      elem.addClass("no")
    }
    else {
      if (onoff) {
        elem.addClass("on")
        elem.removeClass("no")
      }
      else {
        elem.removeClass("on")
        elem.removeClass("no")
      }
    }
    if (changeTag) {
      const texts = (typeof changeTag == BOOL) ? BUTTON[name] : changeTag
      elem.html(texts[(onoff == null) ? "no" : onoff ? "on" : "off"])
    }
  }
  checkFocus(focusPos) {
    const { State } = this
    const { resultsComposed } = State.gets()
    if (resultsComposed == null) {
      return -2
    }
    const nResults = resultsComposed.length
    if (focusPos == nResults) {
      return 0
    }
    if (focusPos == -1 || focusPos > nResults) {
      return nResults - 1
    }
    if (focusPos < 0) {
      return 0
    }
    return focusPos
  }
  clearBrowserState() {
    if (window.history.replaceState) {
      window.history.replaceState(null, null, window.location.href)
    }
  }
}



class MemProvider {
  deps({ Log, Config }) {
    this.Config = Config
    this.tell = Log.tell
  }
  init() {
    const { Config: { name: appName } } = this
    this.appPrefix = `ls/${appName}/`
    this.keyLast = `${this.appPrefix}LastJob`
    this.keyPrefix = `${this.appPrefix}Keys/`
    this.keyLength = this.keyPrefix.length
  }
  getRawKey(userKey) {return `${this.keyPrefix}${userKey}`}
  getUserKey(rawKey) {return rawKey.substring(this.keyLength)}
  getLastKey() {return localStorage.getItem(this.keyLast)}
  getk(userKey) {
    localStorage.setItem(this.keyLast, userKey)
    const rawKey = this.getRawKey(userKey)
    return JSON.parse(localStorage.getItem(rawKey) ?? "{}")
  }
  setk(userKey, content) {
    const rawKey = this.getRawKey(userKey)
    localStorage.setItem(rawKey, JSON.stringify(content))
  }
  remk(userKey) {
    const rawKey = this.getRawKey(userKey)
    localStorage.removeItem(rawKey)
    const lastKey = this.getLastKey()
    if (userKey == lastKey) {
      localStorage.removeItem(this.keyLast)
    }
    const allKeys = this.keys()
    return (allKeys.length == 0) ? DEFAULTJOB : allKeys[allKeys.length - 1]
  }
  getkl() {
    let lastKey = localStorage.getItem(this.keyLast)
    let content
    if (lastKey == null) {
      const allKeys = this.keys()
      if (allKeys.length == 0) {
        lastKey = DEFAULTJOB
        content = {}
        localStorage.setItem(this.keyLast, lastKey)
      }
      else {
        lastKey = allKeys[allKeys.length - 1]
        content = this.getk(lastKey)
      }
    }
    else {
      content = this.getk(lastKey)
    }
    return [lastKey, content]
  }
  setkl(userKey, content) {
    this.setk(userKey, content)
    localStorage.setItem(this.keyLast, userKey)
  }
  keys() {
    const rawKeys = Object.keys(localStorage)
      .filter(rawKey => rawKey.startsWith(this.keyPrefix))
      .map(rawKey => this.getUserKey(rawKey))
    rawKeys.sort()
    return rawKeys
  }
}



class SearchProvider {
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
  async runQuery({ allSteps, gather, weed, compose: composeArg, display } = {}) {
    const { Log, Gui } = this
    const output = $(`#resultsbody,#resultshead`)
    const go = $("#go")
    const expr = $("#exportr")
    const runerror = $("#runerror")
    Log.progress(`executing query`)
    go.html(SEARCH.exe)
    go.removeClass("dirty")
    go.addClass("waiting")
    output.addClass("waiting")
    await new Promise(r => setTimeout(r, 50))
    const errors = []
    if (allSteps || gather) {
      try {
        this.gather()
      }
      catch (error) {
        errors.push({ where: "gather", error })
        Log.error(error)
      }
    }
    if (errors.length == 0) {
      if (allSteps || weed) {
        try {
          const stats = this.weed()
          Gui.placeStatResults(stats)
        }
        catch (error) {
          errors.push({ where: "weed", error })
          Log.error(error)
        }
      }
    }
    if (errors.length == 0) {
      if (allSteps || composeArg !== undefined) {
        try {
          this.composeResults(allSteps ? false : composeArg)
        }
        catch (error) {
          errors.push({ where: "compose", error })
          Log.error(error)
        }
      }
    }
    if (errors.length == 0) {
      if (allSteps || display) {
        try {
          this.displayResults()
        }
        catch (error) {
          errors.push({ where: "display", error })
          Log.error(error)
        }
      }
    }
    if (errors.length > 0) {
      Log.placeError(
        runerror,
        errors.map(({ where, error }) => `${where}: ${error}`).join("<br>"),
        go,
      )
    }
    else {
      Log.clearError(runerror, go)
    }
    go.html(SEARCH[(errors.length == 0) ? "done" : "failed"])
    expr.addClass("active")
    output.removeClass("waiting")
    go.removeClass("waiting")
    $(".dirty").removeClass("dirty")
    Log.progress(`done query`)
  }
  doSearch(nType, layer, lrInfo, regex) {
    const { Corpus: { texts: { [nType]: { [layer]: text } }, positions } } = this
    const { pos: posKey } = lrInfo
    const { [nType]: { [posKey]: pos } } = positions
    const searchResults = text.matchAll(regex)
    const posFromNode = new Map()
    const nodeSet = new Set()
    for (const match of searchResults) {
      for (let group = 0; group < match.length; group++) {
        const hit = match[group]
        const start = match.index
        const end = start + hit.length
        for (let i = start; i < end; i++) {
          const node = pos[i]
          if (node != null) {
            if (!posFromNode.has(node)) {
              posFromNode.set(node, new Map())
            }
            posFromNode.get(node).set(i, group)
            nodeSet.add(node)
          }
        }
      }
    }
    return { posFromNode, nodeSet }
  }
  gather() {
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
        Log.clearError(ebox, box)
        const { [layer]: { pattern, flags, exec } } = tpQuery
        if (!exec || pattern.length == 0) {
          continue
        }
        if (pattern.length > MAXINPUT) {
          Log.placeError(
            ebox,
            `pattern must be less than ${MAXINPUT} characters long`,
            box,
          )
          continue
        }
        const flagString = Object.entries(flags)
          .filter(x => x[1]).map(x => x[0]).join("")
        let regex
        try {
          regex = new RegExp(pattern, `g${flagString}`)
        } catch (error) {
          Log.placeError(ebox, `"${pattern}": ${error}`, box)
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
    const { Config: { ntypes }, Corpus: { up, down }, State } = this
    const { tpResults } = State.gets()
    const stats = {}
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
    if (hi == null) {
      return stats
    }
    for (let i = hi; i > lo; i--) {
      const upType = ntypes[i]
      const dnType = ntypes[i - 1]
      const { [upType]: { nodes: upNodes }, [dnType]: resultsDn = {} } = tpResults
      let { nodes: dnNodes } = resultsDn
      const dnFree = dnNodes == null
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
      for (const dn of dnNodes) {
        if (!up.has(dn) || !upNodes.has(up.get(dn))) {
          dnNodes.delete(dn)
        }
      }
    }
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
    for (const [nType, { nodes }] of Object.entries(tpResults)) {
      stats[nType] = nodes.size
    }
    return stats
  }
  composeResults(recomputeFocus) {
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
        resultTypeMap.set(cn, containerType)
        const levels = { [containerType]: [cn] }
        let un = cn
        let uType = containerType
        while (up.has(un)) {
          un = up.get(un)
          uType = utypeOf[uType]
          resultTypeMap.set(un, uType)
          if (levels[uType] === undefined) {
            levels[uType] = []
          }
          levels[uType].push(un)
        }
        const descendants = this.getDescendants(cn, ntypesI.get(containerType))
        for (const desc of descendants) {
          const d = (typeof desc === NUMBER) ? desc : desc[0]
          const dType = resultTypeMap.get(d)
          if (levels[dType] === undefined) {
            levels[dType] = []
          }
          levels[dType].push(desc)
        }
        resultsComposed.push(levels)
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
    if (uTypeIndex == 0) {
      return []
    }
    const { Config: { dtypeOf, ntypes }, Corpus: { down }, State } = this
    const { resultTypeMap } = State.gets()
    const uType = ntypes[uTypeIndex]
    const dType = dtypeOf[uType]
    const dTypeIndex = uTypeIndex - 1
    const dest = []
    if (down.has(u)) {
      for (const d of down.get(u)) {
        resultTypeMap.set(d, dType)
        if (dTypeIndex == 0) {
          dest.push(d)
        } else {
          dest.push([d, this.getDescendants(d, dTypeIndex, resultTypeMap)])
        }
      }
    }
    return dest
  }
  getHLText(iPositions, matches, text, valueMap, tip) {
    const { getAcro } = this
    this.tell({ matches })
    const hasMap = valueMap != null
    const spans = []
    let str = ""
    let curHl = -1
    for (const i of iPositions) {
      const ch = text[i]
      if (hasMap) {
        str += ch
      }
      const hl = matches.get(i) ?? -1
      if (curHl == -1 || curHl != hl) {
        const newSpan = [hl, ch]
        spans.push(newSpan)
        curHl = hl
      } else {
        spans[spans.length - 1][1] += ch
      }
    }
    const tipStr = (hasMap && tip) ? valueMap[str.replaceAll(getAcro, "")] : null
    return { spans, tipStr }
  }
  getLayersPerType() {
    const { Config: { ntypesR, ntypesI, layers }, State } = this
    const { containerType, visibleLayers } = State.getj()
    const containerIndex = ntypesI.get(containerType)
    const layersPerType = new Map()
    for (const nType of ntypesR) {
      const { [nType]: definedLayers = {} } = layers
      const { [nType]: tpVisible = {} } = visibleLayers
      const nodeLayer = ["_"]
      const tpLayers = nodeLayer.concat(Object.keys(definedLayers))
        .filter(x => tpVisible[x])
      layersPerType.set(nType, tpLayers)
    }
    const visibleTypes = ntypesR.filter(x => layersPerType.get(x).length > 0)
    const contextTypes = visibleTypes.filter(x => ntypesI.get(x) > containerIndex)
    const rowUnitTypes = visibleTypes.filter(x => ntypesI.get(x) == containerIndex)
    const contentTypes = ntypesR.filter(x => ntypesI.get(x) < containerIndex)
    const firstContentTypes = (contentTypes.length == 0) ? [] : [contentTypes[0]]
    const cols = contextTypes.concat(rowUnitTypes).concat(firstContentTypes)
    const layersContent = []
    for (const cnType of contentTypes) {
      layersContent.push(...layersPerType.get(cnType))
    }
    return {
      contextTypes,
      rowUnitTypes,
      contentTypes,
      upperTypes: contextTypes.concat(rowUnitTypes),
      cols,
      layersPerType,
      layersContent,
    }
  }
  displayResults() {
    const {
      Config: { simpleBase, layers, ntypesI, ntypesinit },
      Corpus: { texts, iPositions },
      State,
      Gui,
    } = this
    const { resultTypeMap, tpResults, resultsComposed } = State.gets()
    const { settings: { nodeseq }, focusPos, prevFocusPos } = State.getj()
    if (tpResults == null) {
      State.sets({ resultsComposed: null })
      return
    }
    const {
      upperTypes, contentTypes,
      cols, layersPerType, layersContent,
    } = this.getLayersPerType()
    const colsRep = cols.map(x => `<th>${x}</th>`)
    const header = `<tr><th>${RESULTCOL}</th>${colsRep.join("")}</tr>`
    const resultshead = $("#resultshead")
    resultshead.html(header)
    const genValueHtml = (nType, layer, node) => {
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
        const hlRep = (hl >= 0) ? ` class="hl${hl}"` : ""
        const hlTitle = (hl >= 0) ? ` title="group ${hl}` : ""
        html.push(`<span${hlRep}${hlTitle}>${val}</span>`)
      }
      if (multiple) {
        html.push(`</span>`)
      }
      return html.join("")
    }
    const genNodeHtml = node => {
      const [n, children] = typeof node === NUMBER ? [node, []] : node
      const nType = resultTypeMap.get(n)
      const { [nType]: { nodes } = {} } = tpResults
      const tpLayers = layersPerType.get(nType)
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
    const genResultHtml = (i, result) => {
      const isFocus = i == focusPos
      const isPrevFocus = i == prevFocusPos
      const typeNodes = []
      for (const nType of upperTypes) {
        typeNodes.push(
          `<td>${(result[nType] ?? []).map(x => genNodeHtml(x)).join(" ")}</td>`
        )
      }
      if (contentTypes.length > 0) {
        if (layersContent.length > 0) {
          const nType = contentTypes[0]
          typeNodes.push(
            `<td>${(result[nType] ?? []).map(x => genNodeHtml(x)).join(" ")}</td>`
          )
        }
      }
      const typeRep = typeNodes.join("\n")
      const focusCls = isFocus
        ? ` class="focus"`
        : isPrevFocus
        ? ` class="pfocus"`
        : ""
      return `
  <tr${focusCls}>
    <th>${i + 1}</th>
    ${typeRep}
  </tr>
    `
    }
    const genResultsHtml = () => {
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
        html.push(genResultHtml(i, resultsComposed[i]))
      }
      return html.join("")
    }
    const html = genResultsHtml()
    const resultsbody = $("#resultsbody")
    resultsbody.html(html)
    Gui.applyFocus()
  }
  tabular() {
    const {
      Config: { layers, ntypesinit },
      Corpus: { texts, iPositions },
      State,
      tabNl,
    } = this
    const { resultTypeMap, tpResults, resultsComposed } = State.gets()
    const { settings: { nodeseq } } = State.getj()
    if (tpResults == null) {
      State.sets({ resultsComposed: null })
      return
    }
    const {
      upperTypes, contentTypes,
      cols, layersPerType,
    } = this.getLayersPerType()
    const colsRep = cols.map(x => `${x}\t`)
    const header = `${RESULTCOL}\t${colsRep.join("")}\n`
    const genValueTsv = (nType, layer, node) => {
      if (layer == "_") {
        return `${nodeseq ? node - ntypesinit[nType] + 1 : node} `
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
      const tipRep = (tipStr == null) ? "" : `(=${tipStr})`
      let piece = ""
      for (const [hl, val] of spans) {
        if (hl >= 0) {
          piece += `«${hl}=${val}»`
        }
        else {
          piece += val
        }
        piece += tipRep
      }
      piece = piece.replaceAll(tabNl, " ")
      return piece
    }
    const genNodeTsv = (node, stack) => {
      const [n, children] = typeof node === NUMBER ? [node, []] : node
      const nType = resultTypeMap.get(n)
      const tpLayers = layersPerType.get(nType)
      const newStack = [
        ...stack ?? [],
        ...tpLayers.map(lr => genValueTsv(nType, lr, n)),
      ]
      let tsv
      if (children.length == 0) {
        tsv = newStack
      }
      else {
        const tsvs = []
        let first = true
        for (const ch of children) {
          tsvs.push(genNodeTsv(ch, newStack))
          if (first) {
            first = false
            newStack.fill("")
          }
        }
        tsv = zip(tsvs)
      }
      return tsv
    }
    const zip = tsvs => {
      const maxLen = Math.max(...tsvs.map(x => x.length))
      const stack = []
      for (let i = 0; i < maxLen; i++) {
        stack[i] = tsvs.map(x => (i < x.length) ? x[i] : "").join("")
      }
      return stack
    }
    const genResultTsv = (s, result) => {
      const typeNodes = []
      for (const nType of upperTypes) {
        typeNodes.push([false, (result[nType] ?? []).map(x => genNodeTsv(x))])
      }
      for (const nType of contentTypes) {
        typeNodes.push([true, (result[nType] ?? []).map(x => genNodeTsv(x))])
      }
      const tsv = []
      const maxLines = Math.max(
        ...typeNodes.map(
          x => Math.max(...x[1].map(y => y.length))
        )
      )
      for (let i = 0; i < maxLines; i++) {
        const line = [`${s + 1}`]
        for (const [separate, chunks] of typeNodes) {
          line.push("\t")
          let first = true
          let sep = ""
          for (const chunk of chunks) {
            if (sep) {
              line.push(sep)
            }
            line.push((i < chunk.length) ? chunk[i] : "")
            if (first) {
              first = false
              if (separate) {
                sep = "\t"
              }
            }
          }
        }
        tsv.push(`${line.join("")}\n`)
      }
      return tsv
    }
    if (resultsComposed == null) {
      return ""
    }
    const tsv = []
    for (let i = 0; i < resultsComposed.length; i++) {
      const rows = genResultTsv(i, resultsComposed[i])
      for (let j = 0; j < rows.length; j++) {
        tsv.push(rows[j])
      }
    }
    return header + tsv.join("")
  }
  async saveResults() {
    const { Log, Disk, State } = this
    const { jobName } = State.gets()
    const expr = $("#exportr")
    const runerror = $("#runerror")
    Log.progress(`exporting results`)
    expr.addClass("waiting")
    await new Promise(r => setTimeout(r, 50))
    const errors = []
    let text
    try {
      text = this.tabular()
    }
    catch (error) {
      errors.push({ where: "tabular", error })
      Log.error(error)
    }
    if (errors.length == 0) {
      try {
        Disk.download(text, jobName, "tsv", true)
      }
      catch (error) {
        errors.push({ where: "download", error })
        Log.error(error)
      }
    }
    if (errors.length > 0) {
      Log.placeError(
        runerror,
        errors.map(({ where, error }) => `${where}: ${error}`).join("<br>"),
        expr,
      )
    }
    else {
      Log.clearError(runerror, expr)
    }
    expr.addClass("active")
    expr.removeClass("waiting")
    Log.progress(`done export`)
  }
}



class AppProvider {
  constructor() {
    this.providers = {
      Log: new LogProvider(),
      Disk: new DiskProvider(),
      Mem: new MemProvider(),
      State: new StateProvider(),
      Job: new JobProvider(),
      Gui: new GuiProvider(),
      Config: new ConfigProvider(),
      Corpus: new CorpusProvider(),
      Search: new SearchProvider(),
    }
    this.order = {
      init: ["Log", "Config", "Mem", "State", "Job", "Gui"],
      later: ["Corpus", "Job", "Log"],
    }
    this.deps()
  }
  deps() {
    const { providers, providers: { Log } } = this
    for (const Provider of Object.values(providers)) {
      Provider.deps(providers)
    }
    this.tell = Log.tell
  }
  init() {
    const { providers, order: { init } } = this
    for (const name of init) {
      providers[name].init()
    }
  }
  async later() {
    const { providers, order: { later } } = this
    for (const name of later) {
      providers[name].later()
    }
  }
}
const App = new AppProvider()
$(document).on("DOMContentLoaded", () => {
  App.init()
})
$(window).on("load", () => {
  App.later()
})
