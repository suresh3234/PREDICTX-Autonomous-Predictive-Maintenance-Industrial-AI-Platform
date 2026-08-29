/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f4ff',
          100: '#dbe4fe',
          200: '#bfd0fe',
          300: '#93b2fd',
          400: '#608afa',
          500: '#3b66f5',
          600: '#2547eb',
          700: '#1d35d8',
          800: '#1e2cb0',
          900: '#1e2a8c',
          950: '#0c113b',
        },
        navy: {
          800: '#111827',
          850: '#0d131f',
          900: '#080c14',
          950: '#04070c',
        },
        status: {
          healthy: '#10b981',
          warning: '#f59e0b',
          critical: '#ef4444',
          offline: '#6b7280',
          ai: '#8b5cf6',
          info: '#3b82f6',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'elevated': '0 4px 20px -2px rgba(0, 0, 0, 0.25)',
        'glow-primary': '0 0 20px -5px rgba(59, 102, 245, 0.4)',
        'glow-critical': '0 0 20px -5px rgba(239, 68, 68, 0.4)',
      }
    },
  },
  plugins: [],
}
