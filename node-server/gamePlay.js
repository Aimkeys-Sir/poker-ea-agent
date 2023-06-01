const { difference } = require("./utils")

const cards = new Array(54).fill(0).map((n, i) => i)

/**
 * starting the game
 * @param {*} numPlayers
 * @returns
 */
function gameStart(numPlayers) {
  const randomCards = getRandomCards(cards, numPlayers * 4 + 1)

  console.log({ randomCards })
  const startData = {}
  for (let i = 0; i < numPlayers; i++) {
    startData.hands = startData.hands ?? []
    startData.hands.push(randomCards.slice(i * 4, i * 4 + 4))
  }
  startData.startCard = randomCards.slice(-1)[0]

  return startData
}

function getRandomCards(cards, numRandom) {
  let randomCards = new Set()
  let cardSet = new Set([...cards])

  for (let i = 0; i < numRandom; i++) {
    const card = Array.from(cardSet)[Math.floor(Math.random() * cardSet.size)]
    randomCards.add(card)
    cardSet.delete(card)
  }
  return Array.from(randomCards)
}
/**
 *
 * @param {Array} hand
 * @param {number} topCard
 * @param {number} action
 * @returns
 */
function possibleMoves(hand, topCard, action = false) {
  const [f, n] = toCardPair(topCard)

  //cardless hand
  if (!hand.length) {
    return []
  }

  const starting = []

  //actions

  if (action === 7) {
    starting.push([...hand.filter((c) => Math.floor(c / 4) === 10)])
    if (!starting.length) {
      return []
    } else {
      return generateCombos()
    }
  } else if (action === 4 || action === 5) {
    starting.push(
      ...hand.filter((c) => Math.floor(c / 4) === 1 || Math.floor(c / 4) === 0),
    )
    if (!starting.length) {
      return []
    } else {
      return generateCombos()
    }
  } else if (action === 6) {
    starting.push(
      ...hand.filter((c) => c === 52 || c === 53 || Math.floor(c / 4) === 0),
    )
    if (!starting.length) {
      return []
    } else {
      return generateCombos()
    }
  } else if ([0, 1, 2, 3].includes(action)) {
    starting.push(
      ...hand.filter(
        (c) =>
          c % 4 === action ||
          Math.floor(c / 4) === 0 ||
          (c === 52 && action < 2) ||
          (c === 53 && action > 1)
      ),
    )
    if (!starting.length) {
      return []
    } else {
      return generateCombos()
    }
  }

  //normal topcard
  if (action === false) {
    starting.push(
      ...hand.filter((c) => c % 4 === f || Math.floor(c / 4) === n),
    )
  }


  const isQuestion = (c) => Math.floor(c / 4) === 7 || Math.floor(c / 4) === 7

  function getNext(progression) {
    return hand
      .filter((c) => !progression.includes(c))
      .filter(
        (c) =>
          (c % 4 === progression.slice(-1)[0] % 4 &&
            isQuestion(progression.slice(-1)[0])) ||
          Math.floor(c / 4) === Math.floor(progression.slice(-1)[0] / 4)
      )
      .map((c) => [...progression, c])
  }

  function generateCombos() {
    const probs = []
    if(!starting.length){
        return []
    }

    starting.forEach((card) => {
      const cardProbs = [[card]]

      for (let i = 0; i < hand.length; i++) {
        const all = cardProbs
          .filter((prog) => prog.length > i)
          .map((prog) => getNext(prog))
          .flat(1)

        cardProbs.push(...all)

        console.log({all, cardProbs})
        if (!all.length) break
      }
      probs.push(...cardProbs)
    })
    return probs
  }

  return generateCombos()
}

function toCardPair(c) {
  return c < 52 ? [c % 4, Math.floor(c / 4)] : [4 + (c % 2), Math.floor(c / 4)]
}

module.exports = {
  gameStart,
  possibleMoves,
}
