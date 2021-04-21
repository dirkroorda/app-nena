/*eslint-env jquery*/

const indices = {
  capability: `highlight submatches with different colors`,
  missing: `only highlight the complete matches with one color`,
  support: `✅ Chrome, ✅ Firefox, ✅ Edge, ❌ Safari`,

  data: {
    text: "abc123-----def456",
    pattern: "[a-z]([a-z])[a-z][0-9]([0-9])[0-9]",
    flag: "d",
  },

  use() {
    const { data: { text, pattern, flag } } = this
    const re = new RegExp(pattern, `g${flag}`)

    const highlights = new Map()
    let result

    while ((result = re.exec(text)) !== null) {
      const { indices } = result
      for (let g = 0; g < result.length; g++) {
        const b = indices[g][0]
        const e = indices[g][1]
        for (let h = b; h < e; h++) {
          highlights.set(h, g)
        }
      }
    }

    return `<p>${this.getHlText(text, highlights)}</p>`
  },

  fallback() {
    const { data: { text, pattern } } = this
    const re = new RegExp(pattern, `g`)

    const highlights = new Map()
    const results = text.matchAll(re)
    const g = 0

    for (const match of results) {
      const hit = match[0]
      const b = match.index
      const e = b + hit.length
      for (let h = b; h < e; h++) {
        highlights.set(h, g)
      }
    }
    return `<p>${this.getHlText(text, highlights)}</p>`
  },

  getHlText(text, highlights) {
    const spans = []
    let curG = -2

    for (let i = 0; i < text.length; i++) {
      const ch = text[i]
      const g = highlights.get(i) ?? -1
      if (curG != g) {
        const newSpan = [g, ch]
        spans.push(newSpan)
        curG = g
      } else {
        spans[spans.length - 1][1] += ch
      }
    }
    const html = []
    for (const [g, m] of spans) {
      const gRep = (g >= 0) ? ` class="hl${g}"` : ""
      html.push(`<span${gRep}>${m}</span>`)
    }
    return html.join("")
  },

  can: null,
  error: null,

}

export class FeatureTester {
/* BROWSER SUPPORT FOR CERTAIN FEATURES
 *
 */

  constructor(reporting) {
    /* create all Provider objects
     */
    this.reporting = reporting
    this.features = { indices }
    this.keyDetails = ["capability", "missing", "support", "miss"]
  }

  init() {
    const browserDest = $(`#browser`)
    browserDest.html(`
    <dl>
      <dt>Browser</dt><dd>${navigator.userAgent}</dd>
      <dt>Platform</dt><dd>${navigator.platform}</dd>
    </dl>
    `)
  }

  test() {
    const { features, reporting } = this

    let useResult = []
    let fallbackResult = []

    for (const [name, feature] of Object.entries(features)) {
      try {
        useResult = feature.use()
        feature.can = true
      }
      catch (error) {
        feature.error = error
        feature.can = false
      }
      fallbackResult = feature.fallback()
      if (reporting) {
        this.report(name, useResult, fallbackResult)
      }
    }
    if (reporting) {
      $(`#tests`).append("<hr>")
    }
    return features
  }

  report(name, useResult, fallbackResult) {
    const { features: { [name]: details }, keyDetails } = this
    const { can, error } = details
    const testDest = $(`#tests`)

    const html = []
    const canRep = can ? "✅" : "❌"
    html.push(`<hr><h2>${canRep} ${name}</h2><dl>`)
    for (const dt of keyDetails) {
      const { [dt]: dd } = details
      html.push(`<dt>${dt}</dt><dd>${dd}</dd>`)
    }
    html.push("</dl>")

    if (can) {
      html.push(`<h4>Desired output:</h4>`)
      html.push(useResult)
    }
    else {
      html.push(`<h4>Error message:</h4>`)
      html.push(`<div class="error">${error}</div>`)
    }
    html.push(`<h4>Fallback output${can ? " (not needed)" : ""}:</h4>`)
    html.push(fallbackResult)
    testDest.append(html.join(""))
  }
}
