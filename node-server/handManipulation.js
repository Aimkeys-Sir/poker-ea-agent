import { aces, punishCards, actionCards, cards, questionCards, normalCards, flowerSuits, flowers } from './cards'

function sortHand(hand) {
    const represents = (card) => {
        if (parseInt(card)) return parseInt(card)
        return card.includes("jack") ? 11 :
            card.includes('queen') ? 12 :
                card.includes('king') ? 13 :
                    card.includes('ace') ? 1 : 14
    }

    return hand.sort((a, b) => represents(a) - represents(b))
}

function pluck(num, array) {
    let pluckFrom = [...array]
    const plucked = []
    for (let i = 0; i < num; i++) {
        const item = pluckFrom[Math.floor(Math.random() * pluckFrom.length)]
        pluckFrom = pluckFrom.filter(c => c !== item)
        plucked.push(item)
    }

    return [sortHand(plucked), pluckFrom]
}

function selectionWhiteList(selection = []) {
    if (!selection.length) {
        return cards
    }

    const last = selection[selection.length - 1]
    if (last.includes("joker")) {
        return cards.filter(c => c.includes("joker"))
    }

    const lastTwo = selection.slice(-2).filter(c => c.includes("king")).length
    const twoKicks = lastTwo && lastTwo % 2 === 0


    const [cardNum, flower] = last.split("_").filter(w => w !== 'of')
    if (questionCards.includes(last) || twoKicks) {
        const flowerColor = flower === 'clubs' || flower === "spades" ? "black" : "red"
        return cards.filter(c => c.includes(flower) || c.includes(cardNum) || c.includes(flowerColor)).concat(aces)
    } else {
        return cards.filter(c => c.includes(cardNum))
    }

}

function playwhiteList(topCard, actions = null) {
    const jokers = punishCards.filter(c => c.includes("joker"))
    if (actions) {
        if (actions.punish) {
            if (topCard.includes("joker")) {
                return cards.filter(c => c.includes('joker')).concat(aces)
            }
            return [...aces, ...punishCards.filter(c => c.includes(actions.punish.split("_")[0]))]
        }

        if (actions.jump) {
            return [...actionCards.filter(c => c.includes("jack"))]
        }

        if (actions.ask) {
            const flower = flowers.indexOf(actions.ask) < 2 ? "black" : "red"
            return cards.filter(c => c.includes(actions.ask)).concat(jokers.filter(c => c.includes(flower))).concat(aces)
        }
    }

    if (topCard.includes("joker")) {

        if (topCard.includes("red")) {
            return flowerSuits.slice(2).flat().concat(aces).concat(jokers)
        } else {
            return flowerSuits.slice(0, 2).flat().concat(aces).concat(jokers)
        }
    }


    const [cardNum, flower] = topCard.split("_").filter(w => w !== 'of')

    const flowerColor = flower === 'clubs' || flower === "spades" ? "black" : "red"

    return cards.filter(c => c.includes(flower) || c.includes(cardNum) || c.includes(flowerColor)).concat(aces)
}

function checkWinningHand(hand) {
    if (hand.find(c => punishCards.includes(c) || aces.includes(c) || c.includes('jump'))) return false

    const normals = hand.filter(c => normalCards.includes(c))

    if (!normals.length) return false

    const normalsNum = new Set(normals.map(c => c.split('_')[0]))

    if (normalsNum.size > 1) return false

    const kicks = hand.filter(c => c.includes('king'))

    if (kicks.length % 2 !== 0) return false

    return checkArticulation(hand)
}

function kickPairs(kicks) {
    switch (kicks.length) {
        case 2:
            const pairedKicks = []
            for (let i = 0; i < kicks.length; i++) {
                for (let j = 0; j < kicks.length; j++) {
                    if (j !== i) {
                        pairedKicks.push([kicks[i], kicks[j]].join("_"))
                    }
                }
            }
            return pairedKicks
        case 4:
            return [
                "king_of_clubs_king_of_diamonds",
                "king_of_hearts_king_of_spades",
                "king_of_clubs_king_of_hearts",
                "king_of_clubs_king_of_spades",
            ]
    }
}

function checkArticulation(hand) {
    const corespondents = {}

    const kicks = hand.filter(c=> c.includes("king"))
    hand = hand.filter(c=> !c.includes("king"))

    if(kicks.length) hand = hand.concat(kickPairs(kicks))

    console.log({hand});


    for (let i = 0; i < hand.length; i++) {
        corespondents[hand[i]] = nextCard(hand[i], hand.filter(c => c !== hand[i]))
    }
    for (let j = 0; j < hand.length; j++) { 
        let possiblePaths = [[hand[j]]]
        if (possiblePaths[0].length === hand.length) return true

        for (let i = 0; i < hand.length; i++) {
            possiblePaths = borePaths(possiblePaths)

            possiblePaths = possiblePaths.filter(p=> p.length >= i+1)

            console.log(possiblePaths);
            if (!possiblePaths.length) break
            if (possiblePaths[0].length === hand.length) return true
        }
    }

    function borePaths(paths) {
        return paths.map(p => checkIfPath(p)).flat()
    }

    function checkIfPath(candidate) {
        const last = candidate.slice(-1)
        const corrs = corespondents[last[0]].filter(c => !candidate.includes(c))
        const build = [...candidate]
        const paths = []
        for (const c of corrs) {
            paths.push(checkCandidates([...build], c))
        }
        return paths
    }

    return false
}
function checkCandidates(build, candidate) {
    if (!build.includes(candidate)) {
        build.push(candidate)
    }
    return build
}



function nextCard(card, restOfHand) {
    if(card.includes("king")){
        const [cardNum, flower] = card.split("_").filter(w => w !== 'of').slice(-2)
        return restOfHand.filter(c => (c.includes(cardNum) || c.includes(flower)) && c !== card)
    }else{
        const [cardNum, flower] = card.split("_").filter(w => w !== 'of')
        if (questionCards.includes(card)) {
            return restOfHand.filter(c => (c.includes(cardNum) || c.includes(flower)) && c !== card)
        }
        else {
            return restOfHand.filter(c => c.includes(cardNum) && c !== card)
        }
    }
}




export { sortHand, pluck, selectionWhiteList, playwhiteList, checkWinningHand }


