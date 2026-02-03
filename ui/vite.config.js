import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/static/',
  server: {
    proxy: {
      '/run-workflow': 'http://localhost:8003',
      '/run-ocr': 'http://localhost:8003',
      '/mcp': 'http://localhost:8003',
      '/docs': 'http://localhost:8003',
      '/sample_data': 'http://localhost:8003',
      '/demo_workflow.yaml': 'http://localhost:8003',
      '/demo_input.json': 'http://localhost:8003',
    },
  },
});
