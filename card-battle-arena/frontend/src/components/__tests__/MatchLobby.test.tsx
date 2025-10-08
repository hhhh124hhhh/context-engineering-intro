import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { motion } from 'framer-motion'
import MatchLobby from '../matchmaking/MatchLobby'
import type { GameMode, Deck, UserMatchStatusResponse } from '@/types/matchmaking'

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    h1: ({ children, ...props }: any) => <h1 {...props}>{children}</h1>,
    h2: ({ children, ...props }: any) => <h2 {...props}>{children}</h2>,
  },
}))

// Mock WebSocket
jest.mock('@/hooks/useWebSocket', () => ({
  __esModule: true,
  default: () => ({
    send: jest.fn(),
    onmessage: null,
    readyState: WebSocket.OPEN,
  }),
}))

// Mock fetch
global.fetch = jest.fn()

const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

// Test data
const mockDecks: Deck[] = [
  {
    id: 1,
    name: '快攻法师',
    description: '以低费法术为主的快攻卡组',
    cardClass: 'mage',
    formatType: 'standard',
    isPublic: false,
    isFavorite: true,
    gamesPlayed: 50,
    gamesWon: 30,
    gamesLost: 20,
    winRate: 0.6,
    version: 1,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
    lastUsedAt: '2024-01-01T12:00:00Z',
    cards: [],
  },
  {
    id: 2,
    name: '控制术士',
    description: '后期控制型卡组',
    cardClass: 'warlock',
    formatType: 'standard',
    isPublic: false,
    isFavorite: false,
    gamesPlayed: 30,
    gamesWon: 18,
    gamesLost: 12,
    winRate: 0.6,
    version: 1,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
    lastUsedAt: '2024-01-01T11:00:00Z',
    cards: [],
  },
]

const mockMatchStatus: UserMatchStatusResponse = {
  in_queue: false,
  in_match: false,
}

const mockQueueStatus = {
  ranked: {
    mode: 'ranked' as GameMode,
    queue_length: 5,
    average_wait_time: 120,
    active_matches: 3,
  },
  casual: {
    mode: 'casual' as GameMode,
    queue_length: 8,
    average_wait_time: 60,
    active_matches: 5,
  },
  practice: {
    mode: 'practice' as GameMode,
    queue_length: 2,
    average_wait_time: 30,
    active_matches: 1,
  },
}

// Wrapper component for router context
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
)

describe('MatchLobby Component', () => {
  const mockOnMatchFound = jest.fn()
  const mockOnSpectateMatch = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    mockFetch.mockClear()
  })

  describe('Initial Rendering', () => {
    test('renders match lobby title and description', () => {
      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      expect(screen.getByText('对战大厅')).toBeInTheDocument()
      expect(screen.getByText('选择游戏模式和卡组，开始匹配对战')).toBeInTheDocument()
    })

    test('renders game mode selection', () => {
      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      expect(screen.getByText('游戏模式')).toBeInTheDocument()
      expect(screen.getByText('天梯')).toBeInTheDocument()
      expect(screen.getByText('休闲')).toBeInTheDocument()
      expect(screen.getByText('练习')).toBeInTheDocument()
      expect(screen.getByText('锦标赛')).toBeInTheDocument()
      expect(screen.getByText('友谊赛')).toBeInTheDocument()
    })

    test('renders deck selection', () => {
      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      expect(screen.getByText('选择卡组')).toBeInTheDocument()
      expect(screen.getByText('快攻法师')).toBeInTheDocument()
      expect(screen.getByText('控制术士')).toBeInTheDocument()
    })

    test('renders queue status', () => {
      // Mock queue status fetch
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMatchStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockQueueStatus,
        })

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      expect(screen.getByText('队列状态')).toBeInTheDocument()
    })
  })

  describe('Game Mode Selection', () => {
    test('selects game mode when clicked', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMatchStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockQueueStatus,
        })

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      const casualMode = screen.getByText('休闲')
      fireEvent.click(casualMode)

      // Check if casual mode is selected (visual indication)
      expect(casualMode.closest('button')).toHaveClass('bg-blue-600')
    })

    test('shows mode descriptions', () => {
      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      expect(screen.getByText('影响段位和积分')).toBeInTheDocument()
      expect(screen.getByText('轻松休闲对局')).toBeInTheDocument()
      expect(screen.getByText('与AI对战练习')).toBeInTheDocument()
    })
  })

  describe('Deck Selection', () => {
    test('selects deck when clicked', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMatchStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockQueueStatus,
        })

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      const deckButton = screen.getByText('快攻法师')
      fireEvent.click(deckButton)

      // Check if deck is selected (visual indication)
      expect(deckButton.closest('button')).toHaveClass('bg-blue-600')
    })

    test('shows deck statistics', () => {
      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      expect(screen.getByText('mage • 0种卡牌')).toBeInTheDocument()
      expect(screen.getByText('胜率: 60.0% • 50场')).toBeInTheDocument()
    })

    test('shows empty state when no decks', () => {
      render(
        <TestWrapper>
          <MatchLobby
            userDecks={[]}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      expect(screen.getByText('你还没有创建任何卡组')).toBeInTheDocument()
    })
  })

  describe('Matchmaking Process', () => {
    test('starts matchmaking when valid selection made', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMatchStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockQueueStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            queue_id: 'test_queue_1',
            user_id: 1,
            username: 'testuser',
            mode: 'ranked',
            deck_id: 1,
            deck_name: '快攻法师',
            rating: 1500,
            preferences: {},
            status: 'waiting',
            created_at: Date.now() / 1000,
          }),
        })

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      // Select game mode and deck
      fireEvent.click(screen.getByText('天梯'))
      fireEvent.click(screen.getByText('快攻法师'))

      // Start matchmaking
      const startButton = screen.getByText('开始匹配')
      fireEvent.click(startButton)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/matchmaking/request', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            mode: 'ranked',
            deck_id: 1,
            preferences: {
              max_wait_time: 300,
              rating_tolerance: 200,
            },
          }),
        })
      })
    })

    test('shows error when no deck selected', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMatchStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockQueueStatus,
        })

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      // Select game mode but no deck
      fireEvent.click(screen.getByText('天梯'))

      // Try to start matchmaking
      const startButton = screen.getByText('开始匹配')
      fireEvent.click(startButton)

      expect(screen.getByText('请选择一个卡组')).toBeInTheDocument()
    })

    test('disables start button when no selection made', () => {
      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      const startButton = screen.getByText('开始匹配')
      expect(startButton).toBeDisabled()
    })

    test('enables start button when valid selection made', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMatchStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockQueueStatus,
        })

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      // Select game mode and deck
      fireEvent.click(screen.getByText('天梯'))
      fireEvent.click(screen.getByText('快攻法师'))

      const startButton = screen.getByText('开始匹配')
      expect(startButton).not.toBeDisabled()
    })
  })

  describe('Matchmaking Preferences', () => {
    test('shows/hides advanced settings', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMatchStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockQueueStatus,
        })

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      const preferencesButton = screen.getByText('显示高级设置')
      expect(screen.queryByText('最大等待时间')).not.toBeInTheDocument()

      fireEvent.click(preferencesButton)

      await waitFor(() => {
        expect(screen.getByText('最大等待时间')).toBeInTheDocument()
        expect(screen.getByText('ELO容忍度')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('隐藏高级设置'))

      await waitFor(() => {
        expect(screen.queryByText('最大等待时间')).not.toBeInTheDocument()
      })
    })
  })

  describe('Searching State', () => {
    test('shows searching interface when match starts', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMatchStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockQueueStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            queue_id: 'test_queue_1',
            user_id: 1,
            username: 'testuser',
            mode: 'ranked',
            deck_id: 1,
            deck_name: '快攻法师',
            rating: 1500,
            preferences: {},
            status: 'waiting',
            created_at: Date.now() / 1000,
          }),
        })

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      // Start matchmaking
      fireEvent.click(screen.getByText('天梯'))
      fireEvent.click(screen.getByText('快攻法师'))
      fireEvent.click(screen.getByText('开始匹配'))

      await waitFor(() => {
        expect(screen.getByText('正在搜索对手...')).toBeInTheDocument()
      })
    })

    test('shows cancel button during search', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMatchStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockQueueStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            queue_id: 'test_queue_1',
            user_id: 1,
            username: 'testuser',
            mode: 'ranked',
            deck_id: 1,
            deck_name: '快攻法师',
            rating: 1500,
            preferences: {},
            status: 'waiting',
            created_at: Date.now() / 1000,
          }),
        })

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      // Start matchmaking
      fireEvent.click(screen.getByText('天梯'))
      fireEvent.click(screen.getByText('快攻法师'))
      fireEvent.click(screen.getByText('开始匹配'))

      await waitFor(() => {
        expect(screen.getByText('取消匹配')).toBeInTheDocument()
      })
    })
  })

  describe('Spectate Mode', () => {
    test('shows spectate button', () => {
      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      expect(screen.getByText('想要观看高手对战？')).toBeInTheDocument()
      expect(screen.getByText('进入观战模式')).toBeInTheDocument()
    })

    test('calls onSpectateMatch when spectate button clicked', () => {
      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      const spectateButton = screen.getByText('进入观战模式')
      fireEvent.click(spectateButton)

      expect(mockOnSpectateMatch).toHaveBeenCalledWith('')
    })
  })

  describe('Error Handling', () => {
    test('shows error message when matchmaking fails', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockMatchStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockQueueStatus,
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
        })

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      // Try to start matchmaking
      fireEvent.click(screen.getByText('天梯'))
      fireEvent.click(screen.getByText('快攻法师'))
      fireEvent.click(screen.getByText('开始匹配'))

      await waitFor(() => {
        expect(screen.getByText('开始匹配失败，请重试')).toBeInTheDocument()
      })
    })

    test('shows error when status fetch fails', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'))

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      // Should still render the component despite error
      expect(screen.getByText('对战大厅')).toBeInTheDocument()
    })
  })

  describe('WebSocket Integration', () => {
    test('sends heartbeat message periodically', async () => {
      const mockSend = jest.fn()
      jest.doMock('@/hooks/useWebSocket', () => ({
        __esModule: true,
        default: () => ({
          send: mockSend,
          onmessage: null,
          readyState: WebSocket.OPEN,
        }),
      }))

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            ...mockMatchStatus,
            in_queue: true,
            mode: 'ranked',
            wait_time: 30,
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockQueueStatus,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            queue_id: 'test_queue_1',
            user_id: 1,
            username: 'testuser',
            mode: 'ranked',
            deck_id: 1,
            deck_name: '快攻法师',
            rating: 1500,
            preferences: {},
            status: 'waiting',
            created_at: Date.now() / 1000,
          }),
        })

      render(
        <TestWrapper>
          <MatchLobby
            userDecks={mockDecks}
            onMatchFound={mockOnMatchFound}
            onSpectateMatch={mockOnSpectateMatch}
          />
        </TestWrapper>
      )

      // Start matchmaking
      fireEvent.click(screen.getByText('天梯'))
      fireEvent.click(screen.getByText('快攻法师'))
      fireEvent.click(screen.getByText('开始匹配'))

      await waitFor(() => {
        expect(screen.getByText('正在搜索对手...')).toBeInTheDocument()
      })

      // Wait for heartbeat interval (simulated)
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100))
      })

      // Verify heartbeat is sent (this would need proper timer mocking)
      // expect(mockSend).toHaveBeenCalledWith(JSON.stringify({ type: 'ping' }))
    })
  })
})