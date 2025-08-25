import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import {globalIgnores} from 'eslint/config'

export default tseslint.config([
	globalIgnores(['dist', 'node_modules', 'build', '*.config.{js,ts}']),
	{
		files: ['**/*.{ts,tsx}'],
		extends: [
			js.configs.recommended,
			tseslint.configs.recommended,
			reactHooks.configs['recommended-latest'],
			reactRefresh.configs.vite,
		],
		languageOptions: {
			ecmaVersion: 2020,
			globals: globals.browser,
		},
		rules: {
			// React Hooks exhaustive deps to catch dependency issues
			'react-hooks/exhaustive-deps': 'error',

			// TypeScript specific rules
			'@typescript-eslint/no-unused-vars': ['error', {
				argsIgnorePattern: '^_',
				varsIgnorePattern: '^_'
			}],
			'@typescript-eslint/no-explicit-any': 'warn',
			'@typescript-eslint/prefer-const': 'error',

			// React specific rules
			'react-refresh/only-export-components': ['warn', {
				allowConstantExport: true
			}],

			// General code quality
			'no-console': ['warn', {allow: ['warn', 'error']}],
			'prefer-const': 'error',
			'no-var': 'error',

			// Accessibility
			'jsx-a11y/alt-text': 'error',
			'jsx-a11y/aria-role': 'error',
			'jsx-a11y/aria-props': 'error',
		},
	},
	// Test files specific configuration
	{
		files: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}'],
		languageOptions: {
			globals: {
				...globals.browser,
				...globals.jest,
				vi: 'readonly',
				describe: 'readonly',
				it: 'readonly',
				expect: 'readonly',
				beforeEach: 'readonly',
				afterEach: 'readonly',
			},
		},
		rules: {
			'@typescript-eslint/no-explicit-any': 'off',
			'no-console': 'off',
		},
	},
])
