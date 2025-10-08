import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { motion } from 'framer-motion'
import Card from '../ui/Card'
import type { Card as CardType, CardRarity, CardType as GameCardType } from '@/types/card'

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    span: ({ children, ...props }: any) => <span {...props}>{children}</span>,
  },
}))

// Test data
const mockCard: CardType = {
  id: 1,
  name: '火球术',
  description: '造成6点伤害',
  cost: 4,
  attack: undefined,
  defense: undefined,
  durability: undefined,
  cardType: GameCardType.SPELL,
  rarity: CardRarity.COMMON,
  cardClass: 'mage' as any,
  cardSet: 'basic' as any,
  imageUrl: 'http://example.com/fireball.png',
}

const mockMinionCard: CardType = {
  id: 2,
  name: '石元素',
  description: '嘲讽',
  cost: 3,
  attack: 3,
  defense: 5,
  durability: undefined,
  cardType: GameCardType.MINION,
  rarity: CardRarity.COMMON,
  cardClass: 'neutral' as any,
  cardSet: 'basic' as any,
  imageUrl: 'http://example.com/elemental.png',
}

// Wrapper component for router context
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
)

describe('Card Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Basic Rendering', () => {
    test('renders spell card correctly', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} />
        </TestWrapper>
      )

      expect(screen.getByText('火球术')).toBeInTheDocument()
      expect(screen.getByText('造成6点伤害')).toBeInTheDocument()
      expect(screen.getByText('4')).toBeInTheDocument()
    })

    test('renders minion card correctly', () => {
      render(
        <TestWrapper>
          <Card card={mockMinionCard} showStats />
        </TestWrapper>
      )

      expect(screen.getByText('石元素')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument() // Attack
      expect(screen.getByText('5')).toBeInTheDocument() // Defense
    })

    test('renders card cost when showCost is true', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} showCost />
        </TestWrapper>
      )

      expect(screen.getByText('4')).toBeInTheDocument()
    })

    test('does not render cost when showCost is false', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} showCost={false} />
        </TestWrapper>
      )

      expect(screen.queryByText('4')).not.toBeInTheDocument()
    })
  })

  describe('Card Variations', () => {
    test('renders golden card correctly', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} isGolden />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      expect(cardElement).toHaveClass('border-yellow-400')
    })

    test('renders legendary rarity correctly', () => {
      const legendaryCard = { ...mockCard, rarity: CardRarity.LEGENDARY }
      render(
        <TestWrapper>
          <Card card={legendaryCard} />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      expect(cardElement).toHaveClass('border-orange-400')
    })

    test('renders epic rarity correctly', () => {
      const epicCard = { ...mockCard, rarity: CardRarity.EPIC }
      render(
        <TestWrapper>
          <Card card={epicCard} />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      expect(cardElement).toHaveClass('border-purple-400')
    })

    test('renders different sizes correctly', () => {
      const { rerender } = render(
        <TestWrapper>
          <Card card={mockCard} size="small" />
        </TestWrapper>
      )

      expect(screen.getByTestId('card')).toHaveClass('w-16', 'h-24')

      rerender(
        <TestWrapper>
          <Card card={mockCard} size="large" />
        </TestWrapper>
      )

      expect(screen.getByTestId('card')).toHaveClass('w-48', 'h-64')
    })
  })

  describe('Card States', () => {
    test('renders disabled state correctly', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} disabled />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      expect(cardElement).toHaveClass('opacity-50', 'cursor-not-allowed')
    })

    test('renders canPlay state correctly', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} canPlay />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      expect(cardElement).toHaveClass('ring-green-400')
    })

    test('renders selected state correctly', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} selected />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      expect(cardElement).toHaveClass('ring-yellow-400')
    })

    test('renders hover effects when not disabled', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      expect(cardElement).toHaveClass('hover:scale-105', 'hover:shadow-xl')
    })

    test('does not render hover effects when disabled', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} disabled />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      expect(cardElement).not.toHaveClass('hover:scale-105')
    })
  })

  describe('Interactions', () => {
    test('calls onClick when clicked', () => {
      const mockOnClick = jest.fn()
      render(
        <TestWrapper>
          <Card card={mockCard} onClick={mockOnClick} />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      fireEvent.click(cardElement)

      expect(mockOnClick).toHaveBeenCalledTimes(1)
    })

    test('does not call onClick when disabled', () => {
      const mockOnClick = jest.fn()
      render(
        <TestWrapper>
          <Card card={mockCard} disabled onClick={mockOnClick} />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      fireEvent.click(cardElement)

      expect(mockOnClick).not.toHaveBeenCalled()
    })

    test('calls onRightClick when right-clicked', () => {
      const mockOnRightClick = jest.fn()
      render(
        <TestWrapper>
          <Card card={mockCard} onRightClick={mockOnRightClick} />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      fireEvent.contextMenu(cardElement)

      expect(mockOnRightClick).toHaveBeenCalledTimes(1)
    })
  })

  describe('Minion Specific Features', () => {
    test('renders attack and defense for minions', () => {
      render(
        <TestWrapper>
          <Card card={mockMinionCard} showStats />
        </TestWrapper>
      )

      expect(screen.getByText('3')).toBeInTheDocument() // Attack
      expect(screen.getByText('5')).toBeInTheDocument() // Defense
    })

    test('renders current attack and defense when provided', () => {
      render(
        <TestWrapper>
          <Card
            card={mockMinionCard}
            currentAttack={5}
            currentDefense={3}
            showStats
          />
        </TestWrapper>
      )

      expect(screen.getByText('5')).toBeInTheDocument() // Current Attack
      expect(screen.getByText('3')).toBeInTheDocument() // Current Defense
    })

    test('renders taunt effect correctly', () => {
      const tauntCard = { ...mockMinionCard, mechanics: ['taunt'] }
      render(
        <TestWrapper>
          <Card card={tauntCard} />
        </TestWrapper>
      )

      expect(screen.getByText('嘲讽')).toBeInTheDocument()
    })

    test('renders divine shield effect correctly', () => {
      const divineShieldCard = { ...mockMinionCard, mechanics: ['divine_shield'] }
      render(
        <TestWrapper>
          <Card card={divineShieldCard} />
        </TestWrapper>
      )

      expect(screen.getByText('圣盾')).toBeInTheDocument()
    })

    test('renders windfury effect correctly', () => {
      const windfuryCard = { ...mockMinionCard, mechanics: ['windfury'] }
      render(
        <TestWrapper>
          <Card card={windfuryCard} />
        </TestWrapper>
      )

      expect(screen.getByText('风怒')).toBeInTheDocument()
    })
  })

  describe('Weapon Cards', () => {
    const mockWeaponCard: CardType = {
      id: 3,
      name: '死亡之咬',
      description: '消灭一个随从后获得+1攻击力',
      cost: 4,
      attack: 4,
      defense: 2,
      durability: 2,
      cardType: GameCardType.WEAPON,
      rarity: CardRarity.RARE,
      cardClass: 'warrior' as any,
      cardSet: 'classic' as any,
    }

    test('renders weapon card correctly', () => {
      render(
        <TestWrapper>
          <Card card={mockWeaponCard} showStats />
        </TestWrapper>
      )

      expect(screen.getByText('死亡之咬')).toBeInTheDocument()
      expect(screen.getByText('4')).toBeInTheDocument() // Attack
      expect(screen.getByText('2')).toBeInTheDocument() // Durability
    })

    test('renders current durability when provided', () => {
      render(
        <TestWrapper>
          <Card
            card={mockWeaponCard}
            currentDurability={1}
            showStats
          />
        </TestWrapper>
      )

      expect(screen.getByText('1')).toBeInTheDocument() // Current Durability
    })
  })

  describe('Spell Cards', () => {
    test('does not render attack/defense for spells', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} showStats />
        </TestWrapper>
      )

      // Spell cards should not show attack/defense stats
      expect(screen.queryByText('6')).not.toBeInTheDocument()
    })

    test('renders spell power indicator for spell damage cards', () => {
      const spellDamageCard = {
        ...mockCard,
        mechanics: ['spell_damage'],
        attack: 1 // Spell damage cards might have attack for spell power
      }
      render(
        <TestWrapper>
          <Card card={spellDamageCard} showStats />
        </TestWrapper>
      )

      expect(screen.getByText('1')).toBeInTheDocument() // Spell power
    })
  })

  describe('Accessibility', () => {
    test('has proper ARIA labels', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      expect(cardElement).toHaveAttribute('role', 'button')
      expect(cardElement).toHaveAttribute('tabIndex', '0')
    })

    test('supports keyboard navigation', () => {
      const mockOnClick = jest.fn()
      render(
        <TestWrapper>
          <Card card={mockCard} onClick={mockOnClick} />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      cardElement.focus()
      fireEvent.keyDown(cardElement, { key: 'Enter' })

      expect(mockOnClick).toHaveBeenCalled()
    })

    test('has accessible description for screen readers', () => {
      render(
        <TestWrapper>
          <Card card={mockCard} />
        </TestWrapper>
      )

      const cardElement = screen.getByTestId('card')
      expect(cardElement).toHaveAttribute('aria-label')
    })
  })

  describe('Performance', () => {
    test('renders efficiently with many cards', () => {
      const startTime = performance.now()

      const cards = Array.from({ length: 100 }, (_, i) => (
        <Card key={i} card={{ ...mockCard, id: i + 1 }} />
      ))

      render(
        <TestWrapper>
          <div>{cards}</div>
        </TestWrapper>
      )

      const endTime = performance.now()
      expect(endTime - startTime).toBeLessThan(1000) // Should render within 1 second
    })
  })

  describe('Error Handling', () => {
    test('handles missing card data gracefully', () => {
      const incompleteCard = { id: 1, name: 'Test Card' } as CardType

      render(
        <TestWrapper>
          <Card card={incompleteCard} />
        </TestWrapper>
      )

      expect(screen.getByText('Test Card')).toBeInTheDocument()
      // Should not crash with missing data
    })

    test('handles missing image gracefully', () => {
      const cardWithoutImage = { ...mockCard, imageUrl: undefined }

      render(
        <TestWrapper>
          <Card card={cardWithoutImage} />
        </TestWrapper>
      )

      // Should render placeholder or not show broken image
      expect(screen.getByText('火球术')).toBeInTheDocument()
    })
  })
})