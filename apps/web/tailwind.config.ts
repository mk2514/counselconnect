import type { Config } from 'tailwindcss';
import tailwindcssAnimate from 'tailwindcss-animate';

/**
 * CounselConnect Tailwind configuration.
 *
 * Design tokens are derived from the approved palette in docs/rules/02-ui-design.md.
 * Terracotta is an accent color, not the dominant color.
 * Border radius range: 6px-10px per project rules.
 *
 * shadcn/ui components are customized to match the approved judicial/government
 * visual language. Default shadcn styling is overridden where it conflicts.
 */
const config: Config = {
  darkMode: ['class'],
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        /* CounselConnect design tokens */
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        surface: '#FFFFFF',
        sidebar: 'hsl(var(--sidebar-background))',
        'primary-text': '#1F2428',
        'secondary-text': '#667085',

        /* shadcn/ui semantic colors mapped to CounselConnect palette */
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))',
        },

        /* CounselConnect-specific tokens */
        terracotta: {
          DEFAULT: '#B85C3A',
          dark: '#8E432B',
          soft: '#E8B49F',
          bg: '#F6E7E0',
        },
        status: {
          success: '#16a34a',
          'success-bg': '#f0fdf4',
          pending: '#d97706',
          'pending-bg': '#fffbeb',
          error: '#dc2626',
          'error-bg': '#fef2f2',
          info: '#2563eb',
          'info-bg': '#eff6ff',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.06)',
        dropdown: '0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [tailwindcssAnimate],
};

export default config;
