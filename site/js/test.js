/*eslint-env jquery*/

import { FeatureTester } from "./feature.js"

const Tester = new FeatureTester(true)

$(document).on("DOMContentLoaded", () => {
  /* DOM is loaded, not all data has arrived
   */
  Tester.init()
  const features = Tester.test()
  console.warn({ features })
})
