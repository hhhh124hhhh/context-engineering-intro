import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import { Deck, Card } from '@types/game'

interface DeckStore {
  decks: Deck[]
  currentDeck: Deck | null
  availableCards: Card[]
  loading: boolean
  error: string | null
  
  // Actions
  getDecks: () => Promise<void>
  getDeck: (id: string) => Promise<void>
  createDeck: (deck: Omit<Deck, 'id' | 'createdAt' | 'cardCount'>) => Promise<void>
  updateDeck: (id: string, deck: Partial<Deck>) => Promise<void>
  deleteDeck: (id: string) => Promise<void>
  setCurrentDeck: (id: string) => Promise<void>
  getAvailableCards: () => Promise<void>
  addCardToDeck: (deckId: string, cardId: string) => Promise<void>
  removeCardFromDeck: (deckId: string, cardId: string) => Promise<void>
}

export const useDeckStore = create<DeckStore>()(
  subscribeWithSelector((set, get) => ({
    decks: [],
    currentDeck: null,
    availableCards: [],
    loading: false,
    error: null,

    getDecks: async () => {
      set({ loading: true, error: null })
      try {
        // 模拟API调用
        const response = await fetch('/api/decks')
        if (!response.ok) throw new Error('Failed to fetch decks')
        const decks = await response.json()
        set({ decks, loading: false })
      } catch (error) {
        set({ error: (error as Error).message, loading: false })
      }
    },

    getDeck: async (id: string) => {
      set({ loading: true, error: null })
      try {
        // 模拟API调用
        const response = await fetch(`/api/decks/${id}`)
        if (!response.ok) throw new Error('Failed to fetch deck')
        const deck = await response.json()
        set({ currentDeck: deck, loading: false })
      } catch (error) {
        set({ error: (error as Error).message, loading: false })
      }
    },

    createDeck: async (deckData) => {
      set({ loading: true, error: null })
      try {
        // 模拟API调用
        const response = await fetch('/api/decks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(deckData)
        })
        if (!response.ok) throw new Error('Failed to create deck')
        const newDeck = await response.json()
        set(state => ({ decks: [...state.decks, newDeck], loading: false }))
      } catch (error) {
        set({ error: (error as Error).message, loading: false })
      }
    },

    updateDeck: async (id: string, deckData) => {
      set({ loading: true, error: null })
      try {
        // 模拟API调用
        const response = await fetch(`/api/decks/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(deckData)
        })
        if (!response.ok) throw new Error('Failed to update deck')
        const updatedDeck = await response.json()
        set(state => ({
          decks: state.decks.map(deck => deck.id === id ? updatedDeck : deck),
          currentDeck: state.currentDeck?.id === id ? updatedDeck : state.currentDeck,
          loading: false
        }))
      } catch (error) {
        set({ error: (error as Error).message, loading: false })
      }
    },

    deleteDeck: async (id: string) => {
      set({ loading: true, error: null })
      try {
        // 模拟API调用
        const response = await fetch(`/api/decks/${id}`, {
          method: 'DELETE'
        })
        if (!response.ok) throw new Error('Failed to delete deck')
        set(state => ({
          decks: state.decks.filter(deck => deck.id !== id),
          currentDeck: state.currentDeck?.id === id ? null : state.currentDeck,
          loading: false
        }))
      } catch (error) {
        set({ error: (error as Error).message, loading: false })
      }
    },

    setCurrentDeck: async (id: string) => {
      set({ loading: true, error: null })
      try {
        // 模拟API调用
        const response = await fetch(`/api/decks/${id}/set-current`, {
          method: 'POST'
        })
        if (!response.ok) throw new Error('Failed to set current deck')
        const deck = await response.json()
        set({ currentDeck: deck, loading: false })
      } catch (error) {
        set({ error: (error as Error).message, loading: false })
      }
    },

    getAvailableCards: async () => {
      set({ loading: true, error: null })
      try {
        // 模拟API调用
        const response = await fetch('/api/cards')
        if (!response.ok) throw new Error('Failed to fetch cards')
        const cards = await response.json()
        set({ availableCards: cards, loading: false })
      } catch (error) {
        set({ error: (error as Error).message, loading: false })
      }
    },

    addCardToDeck: async (deckId: string, cardId: string) => {
      set({ loading: true, error: null })
      try {
        // 模拟API调用
        const response = await fetch(`/api/decks/${deckId}/cards`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ cardId })
        })
        if (!response.ok) throw new Error('Failed to add card to deck')
        const updatedDeck = await response.json()
        set(state => ({
          decks: state.decks.map(deck => deck.id === deckId ? updatedDeck : deck),
          currentDeck: state.currentDeck?.id === deckId ? updatedDeck : state.currentDeck,
          loading: false
        }))
      } catch (error) {
        set({ error: (error as Error).message, loading: false })
      }
    },

    removeCardFromDeck: async (deckId: string, cardId: string) => {
      set({ loading: true, error: null })
      try {
        // 模拟API调用
        const response = await fetch(`/api/decks/${deckId}/cards/${cardId}`, {
          method: 'DELETE'
        })
        if (!response.ok) throw new Error('Failed to remove card from deck')
        const updatedDeck = await response.json()
        set(state => ({
          decks: state.decks.map(deck => deck.id === deckId ? updatedDeck : deck),
          currentDeck: state.currentDeck?.id === deckId ? updatedDeck : state.currentDeck,
          loading: false
        }))
      } catch (error) {
        set({ error: (error as Error).message, loading: false })
      }
    }
  }))
)