import { defaults } from 'jest-config'

export default {
  // Test environment
  testEnvironment: 'jsdom',

  // Setup files
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],

  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],

  // Module name mapping
  moduleNameMapper: {
    // Handle absolute imports
    '^@/(.*)$': '<rootDir>/src/$1',

    // Handle CSS imports
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',

    // Handle image imports
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',

    // Handle module aliases
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@types/(.*)$': '<rootDir>/src/types/$1',
    '^@assets/(.*)$': '<rootDir>/src/assets/$1',
  },

  // Transform configuration
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: {
        jsx: 'react-jsx',
        esModuleInterop: true,
        allowSyntheticDefaultImports: true,
      },
    }],
  },

  // Test match patterns
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.(ts|tsx|js)',
    '<rootDir>/src/**/*.(test|spec).(ts|tsx|js)',
  ],

  // Files to ignore
  testPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/dist/',
    '<rootDir>/build/',
    '<rootDir>/public/',
  ],

  // Coverage configuration
  collectCoverageFrom: [
    'src/**/*.(ts|tsx)',
    '!src/**/*.d.ts',
    '!src/main.tsx',
    '!src/vite-env.d.ts',
    '!src/setupTests.ts',
    '!src/**/__tests__/**',
    '!src/**/*.stories.(ts|tsx)',
  ],

  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },

  // Coverage reporters
  coverageReporters: [
    'text',
    'lcov',
    'html',
    'json-summary',
  ],

  // Coverage directory
  coverageDirectory: 'coverage',

  // Mock configuration
  clearMocks: true,
  restoreMocks: true,

  // Verbose output
  verbose: false,

  // Test timeout
  testTimeout: 10000,

  // Global variables
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.json',
    },
  },

  // Extensions to transform
  moduleDirectories: ['node_modules', 'src'],

  // Ignore transforms
  transformIgnorePatterns: [
    'node_modules/(?!(framer-motion)/)',
  ],

  // Setup files
  setupFiles: ['<rootDir>/jest.setup.js'],

  // Test environment options
  testEnvironmentOptions: {
    url: 'http://localhost:3000',
  },

  // Reporter configuration
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: 'coverage',
        outputName: 'junit.xml',
      },
    ],
  ],

  // Watch plugins
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname',
  ],

  // Error handling
  errorOnDeprecated: true,

  // Cache configuration
  cache: true,
  cacheDirectory: '<rootDir>/node_modules/.cache/jest',

  // Maximum workers
  maxWorkers: '50%',

  // Test results processor
  testResultsProcessor: undefined,

  // Snapshot configuration
  snapshotFormat: {
    escapeSpecial: false,
    printBasicPrototype: false,
  },

  // Test sequencer
  testSequencer: '@jest/test-sequencer',

  // Watchman configuration
  watchman: true,

  // Force exit
  forceExit: false,

  // Detect open handles
  detectOpenHandles: false,

  // Detect leaks
  detectLeaks: false,

  // Notify
  notify: false,

  // Notify mode
  notifyMode: 'failure-change',

  // Project configuration
  projects: [
    {
      displayName: 'Components',
      testMatch: ['<rootDir>/src/components/**/__tests__/**/*.(ts|tsx|js)'],
      setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
    },
    {
      displayName: 'Hooks',
      testMatch: ['<rootDir>/src/hooks/**/__tests__/**/*.(ts|tsx|js)'],
      setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
    },
    {
      displayName: 'Utils',
      testMatch: ['<rootDir>/src/utils/**/__tests__/**/*.(ts|tsx|js)'],
      setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
    },
  ],
}