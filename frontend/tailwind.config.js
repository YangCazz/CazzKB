/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        accent: {
          DEFAULT: 'var(--ds-accent)',
          foreground: '#ffffff',
          soft: 'var(--ds-accent-soft)',
        },
        'ds-main': 'var(--ds-bg-main)',
        'ds-sidebar': 'var(--ds-bg-sidebar)',
        'ds-canvas': 'var(--ds-bg-canvas)',
        'ds-card': 'var(--ds-surface-card)',
        'ds-elevated': 'var(--ds-surface-elevated)',
        'ds-subtle': 'var(--ds-surface-subtle)',
        'ds-hover': 'var(--ds-surface-hover)',
        'ds-border': 'var(--ds-border)',
        'ds-border-muted': 'var(--ds-border-muted)',
        'ds-ink': 'var(--ds-text)',
        'ds-muted': 'var(--ds-text-muted)',
        'ds-faint': 'var(--ds-text-faint)',
        'ds-success': 'var(--ds-success)',
        'ds-success-soft': 'var(--ds-success-soft)',
        'ds-danger': 'var(--ds-danger)',
        'ds-danger-soft': 'var(--ds-danger-soft)',
        'ds-userbubble': 'var(--ds-bubble-user)',
        'ds-userbubble-fg': 'var(--ds-bubble-user-fg)',
      },
      boxShadow: {
        'composer': 'var(--ds-shadow-composer)',
        'card-soft': 'var(--ds-shadow-card-soft)',
        'card-strong': 'var(--ds-shadow-card-strong)',
      },
      borderRadius: {
        xl: '14px',
        '2xl': '18px',
        '3xl': '22px',
      },
    },
  },
  plugins: [],
}
