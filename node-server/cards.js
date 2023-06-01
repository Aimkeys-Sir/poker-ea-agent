const cards = [
  "ace_of_clubs",
  "ace_of_spades",
  "ace_of_hearts",
  "ace_of_diamonds",
  "2_of_clubs",
  "2_of_spades",
  "2_of_hearts",
  "2_of_diamonds",
  "3_of_clubs",
  "3_of_spades",
  "3_of_hearts",
  "3_of_diamonds",
  "4_of_clubs",
  "4_of_spades",
  "4_of_hearts",
  "4_of_diamonds",
  "5_of_clubs",
  "5_of_spades",
  "5_of_hearts",
  "5_of_diamonds",
  "6_of_clubs",
  "6_of_spades",
  "6_of_hearts",
  "6_of_diamonds",
  "7_of_clubs",
  "7_of_spades",
  "7_of_hearts",
  "7_of_diamonds",
  "8_of_clubs",
  "8_of_spades",
  "8_of_hearts",
  "8_of_diamonds",
  "9_of_clubs",
  "9_of_spades",
  "9_of_hearts",
  "9_of_diamonds",
  "10_of_clubs",
  "10_of_spades",
  "10_of_hearts",
  "10_of_diamonds",
  "jack_of_clubs",
  "jack_of_spades",
  "jack_of_hearts",
  "jack_of_diamonds",
  "queen_of_clubs",
  "queen_of_spades",
  "queen_of_hearts",
  "queen_of_diamonds",
  "king_of_clubs",
  "king_of_spades",
  "king_of_hearts",
  "king_of_diamonds",
  "black_joker",
  "red_joker",
]

const questionCards = cards.filter((c) => c.includes("q") || c.includes("8"))

const actionCards = cards.filter(
  (c) => c.includes("jack") || c.includes("king")
)

const aces = cards.filter((c) => c.includes("ace"))

const punishCards = cards.filter(
  (c) => c.includes("2") || c.includes("3") || c.includes("joker")
)
const normals = [4, 5, 6, 7, 9, 10]

const normalCards = cards.filter((c) => normals.includes(parseInt(c)))

const flowers = ["clubs", "spades", "hearts", "diamonds"]
const flowerSuits = flowers.map((f) => cards.filter((c) => c.includes(f)))

export {
  cards,
  questionCards,
  actionCards,
  aces,
  punishCards,
  normalCards,
  flowers,
  flowerSuits,
}
