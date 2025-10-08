export enum CardType {
  MINION = 'minion',
  SPELL = 'spell',
  WEAPON = 'weapon',
  HERO_POWER = 'hero_power'
}

export enum CardRarity {
  COMMON = 'common',
  RARE = 'rare',
  EPIC = 'epic',
  LEGENDARY = 'legendary'
}

export enum CardClass {
  WARRIOR = 'warrior',
  MAGE = 'mage',
  HUNTER = 'hunter',
  ROGUE = 'rogue',
  PRIEST = 'priest',
  WARLOCK = 'warlock',
  SHAMAN = 'shaman',
  PALADIN = 'paladin',
  DRUID = 'druid',
  NEUTRAL = 'neutral'
}

export enum CardSet {
  BASIC = 'basic',
  CLASSIC = 'classic',
  EXPERT = 'expert',
  HOF = 'hof',
  NAXXRAMAS = 'naxxramas',
  GVG = 'gvg',
  TGT = 'tgt',
  MSG = 'msg',
  WOG = 'wog',
  BRM = 'brm',
  TGT2 = 'tgt2',
  UNGORO = 'ungoro',
  LOE = 'loe',
  GVG2 = 'gvg2',
  TGT3 = 'tgt3',
  WOTOG = 'wotog',
  BRM2 = 'brm2',
  KARAZHAN = 'karazhan',
  MSoG = 'msog',
  UNGORO2 = 'ungoro2'
}

export interface Card {
  id: number
  name: string
  description: string
  flavorText?: string
  cost: number
  attack?: number
  defense?: number
  durability?: number
  cardType: CardType
  rarity: CardRarity
  cardClass: CardClass
  cardSet: CardSet
  mechanics?: string[]
  effectText?: string
  playRequirements?: any
  deathrattleEffect?: any
  battlecryEffect?: any
  ongoingEffect?: any
  imageUrl?: string
  goldenImageUrl?: string
  soundUrl?: string
  isCollectible?: boolean
  isStandardLegal?: boolean
  isWildLegal?: boolean
  craftingCost?: number
  playCount?: number
  winRate?: number
  usageRate?: number
  artist?: string
  howToGet?: string
  lore?: string
}

export interface CardInstance {
  id: number
  instanceId: string
  card: Card
  currentCost: number
  currentAttack?: number
  currentDefense?: number
  currentDurability?: number
  isDormant: boolean
  isSilenced: boolean
  isFrozen: boolean
  attackCount: number
  summoningSickness: boolean
  enchantments: Enchantment[]
  location: CardLocation
  position?: number
  controller: number
}

export enum CardLocation {
  DECK = 'deck',
  HAND = 'hand',
  BATTLEFIELD = 'battlefield',
  GRAVEYARD = 'graveyard',
  SECRET = 'secret',
  REMOVED = 'removed',
  WEAPON = 'weapon'
}

export interface Enchantment {
  id: string
  source: string
  effects: string[]
  duration?: number
  attackBuff?: number
  defenseBuff?: number
  costBuff?: number
  description: string
}

export interface DeckCard {
  cardId: number
  quantity: number
  position: number
  card: Card
}

export interface Deck {
  id: number
  name: string
  description?: string
  cardClass: CardClass
  formatType: string
  isPublic: boolean
  isFavorite: boolean
  gamesPlayed: number
  gamesWon: number
  gamesLost: number
  winRate: number
  version: number
  createdAt: string
  updatedAt: string
  lastUsedAt?: string
  cards: DeckCard[]
}

export interface CardCollection {
  normalCount: number
  goldenCount: number
  craftedNormal: number
  craftedGolden: number
  disenchantedNormal: number
  disenchantedGolden: number
  firstObtainedAt?: string
  lastUsedAt?: string
  totalCraftingCost: number
  totalDisenchantValue: number
  isCraftable: boolean
  totalCount: number
}

export interface CardFilter {
  cardType?: CardType
  rarity?: CardRarity
  cardClass?: CardClass
  cardSet?: CardSet
  costMin?: number
  costMax?: number
  attackMin?: number
  attackMax?: number
  healthMin?: number
  healthMax?: number
  mechanics?: string[]
  textFilter?: string
  isCollectible?: boolean
  isStandardLegal?: boolean
  isWildLegal?: boolean
  hasDuplicates?: boolean
  ownedCards?: boolean
  unownedCards?: boolean
  craftableCards?: boolean
}

export interface CardSort {
  field: 'cost' | 'name' | 'attack' | 'defense' | 'rarity' | 'class' | 'set'
  direction: 'asc' | 'desc'
}

export interface CardSearch {
  query?: string
  filter?: CardFilter
  sort?: CardSort
  limit?: number
  offset?: number
}