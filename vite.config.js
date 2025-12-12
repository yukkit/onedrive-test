import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    allowedHosts: ["ofnil-kms-connector.kasma.ai"],
    host: '0.0.0.0',
    port: 15400
  }
})

