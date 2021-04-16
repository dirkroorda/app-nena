export const DEBUG = false

export const BOOL = "boolean"
export const NUMBER = "number"
export const STRING = "string"
export const OBJECT = "object"

export const QUWINDOW = 10
export const MAXINPUT = 1000

export const DEFAULTJOB = "search"

export const BUTTON = {
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

export const UNITTEXT = { r: "row unit", a: "context", d: "content" }

export const FLAGSDEFAULT = { i: true, m: true, s: false }

export const SEARCH = {
  dirty: "fetch results",
  exe: "fetching ...",
  done: "up to date",
  failed: "failed",
}

export const TIP = {
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

