import { build, defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import istanbul from 'vite-plugin-istanbul'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({  
  base: './',
  build: {
    outDir: '../frontend/dist'       
  },
  plugins: [
    react(),
    tailwindcss(),
    istanbul({
      cypress: true,
      requireEnv: false
    })
  ]
})
