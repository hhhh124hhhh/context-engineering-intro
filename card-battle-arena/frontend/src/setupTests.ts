import '@testing-library/jest-dom'
import { configure } from '@testing-library/react'
import { server } from './__mocks__/server'

// Configure testing-library
configure({
  testIdAttribute: 'data-testid',
  asyncUtilTimeout: 5000,
  asyncWrapperUtilTimeout: 2000,
})

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock getComputedStyle
Object.defineProperty(window, 'getComputedStyle', {
  value: () => ({
    getPropertyValue: () => '',
    width: '0px',
    height: '0px',
  }),
})

// Mock scrollTo
Object.defineProperty(window, 'scrollTo', {
  value: jest.fn(),
})

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
})

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.OPEN
  url = ''
  protocol = ''
  extensions = ''
  bufferedAmount = 0
  binaryType = 'blob'

  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null

  constructor(url: string, protocols?: string | string[]) {
    this.url = url
    if (protocols) {
      this.protocol = Array.isArray(protocols) ? protocols[0] : protocols
    }
  }

  send(data: string | ArrayBuffer | Blob) {
    // Mock implementation
  }

  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code: code || 1000, reason }))
    }
  }

  addEventListener(type: string, listener: EventListener) {
    // Mock implementation
  }

  removeEventListener(type: string, listener: EventListener) {
    // Mock implementation
  }

  dispatchEvent(event: Event) {
    // Mock implementation
    return true
  }
}

Object.defineProperty(window, 'WebSocket', {
  value: MockWebSocket,
})

// Mock performance.now
Object.defineProperty(window, 'performance', {
  value: {
    now: jest.fn(() => Date.now()),
  },
})

// Mock console methods for cleaner test output
const originalError = console.error
const originalWarn = console.warn

beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is deprecated')
    ) {
      return
    }
    originalError.call(console, ...args)
  }

  console.warn = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('componentWillReceiveProps')
    ) {
      return
    }
    originalWarn.call(console, ...args)
  }
})

afterAll(() => {
  console.error = originalError
  console.warn = originalWarn
})

// Mock environment variables
process.env.NODE_ENV = 'test'
process.env.REACT_APP_API_URL = 'http://localhost:8000'
process.env.REACT_APP_WS_URL = 'ws://localhost:8000/ws'

// Start MSW server before all tests
beforeAll(() => {
  server.listen({
    onUnhandledRequest: 'error',
  })
})

//  Reset request handlers after each test
afterEach(() => {
  server.resetHandlers()
  localStorageMock.clear()
  sessionStorageMock.clear()
  jest.clearAllMocks()
})

// Close MSW server after all tests
afterAll(() => {
  server.close()
})

// Global test utilities
global.testUtils = {
  // Wait for next tick
  waitForNextTick: () => new Promise(resolve => setTimeout(resolve, 0)),

  // Create mock user
  createMockUser: (overrides = {}) => ({
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    rating: 1500,
    is_active: true,
    is_verified: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...overrides,
  }),

  // Create mock deck
  createMockDeck: (overrides = {}) => ({
    id: 1,
    name: 'Test Deck',
    description: 'A test deck',
    card_class: 'mage',
    format_type: 'standard',
    is_public: false,
    is_favorite: false,
    games_played: 0,
    games_won: 0,
    games_lost: 0,
    win_rate: 0.0,
    version: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    last_used_at: null,
    cards: [],
    ...overrides,
  }),

  // Create mock card
  createMockCard: (overrides = {}) => ({
    id: 1,
    name: 'Fireball',
    description: 'Deal 6 damage',
    cost: 4,
    attack: null,
    defense: null,
    durability: null,
    card_type: 'spell',
    rarity: 'common',
    card_class: 'mage',
    card_set: 'basic',
    mechanics: [],
    image_url: 'http://example.com/fireball.png',
    ...overrides,
  }),

  // Create mock game state
  createMockGameState: (overrides = {}) => ({
    game_id: 'test-game-1',
    player1_id: 1,
    player2_id: 2,
    current_player_number: 1,
    turn_number: 1,
    turn_time_limit: 90,
    is_game_over: false,
    winner: null,
    action_history: [],
    player1: {
      user_id: 1,
      username: 'player1',
      health: 30,
      max_health: 30,
      armor: 0,
      mana: 1,
      max_mana: 1,
      hand: [],
      battlefield: [],
      deck_count: 20,
      graveyand_count: 0,
    },
    player2: {
      user_id: 2,
      username: 'player2',
      health: 30,
      max_health: 30,
      armor: 0,
      mana: 0,
      max_mana: 0,
      hand: [],
      battlefield: [],
      deck_count: 20,
      graveyand_count: 0,
    },
    ...overrides,
  }),
}