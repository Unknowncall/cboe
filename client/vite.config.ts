import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
	plugins: [react()],
	resolve: {
		alias: {
			"@": fileURLToPath(new URL('./src', import.meta.url)),
		},
	},
	server: {
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true,
			},
		},
	},
	build: {
		rollupOptions: {
			output: {
				manualChunks: {
					// Vendor libraries
					vendor: ['react', 'react-dom'],
					router: ['react-router-dom'],
					forms: ['react-hook-form', '@hookform/resolvers', 'zod'],
					ui: ['@radix-ui/react-slot', 'class-variance-authority', 'clsx', 'tailwind-merge'],
					icons: ['lucide-react'],
					utils: ['dompurify']
				}
			}
		},
		// Enable source maps for better debugging
		sourcemap: true,
		// Target modern browsers for smaller bundles
		target: 'esnext',
		// Optimize chunk size
		chunkSizeWarningLimit: 1600
	},
})
