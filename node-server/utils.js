/**
 * sets manipulations
 * @param {*} setA 
 * @param {*} setB 
 * @returns 
 */

function union(setA, setB) {
  const _union = new Set(setA)
  for (const elem of setB) {
    _union.add(elem)
  }
  return _union
}

const difference = (setA, setB) =>
  new Set([...setA].filter((x) => !setB.has(x)))

module.exports = {
  union,
  difference,
}
