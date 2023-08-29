import { sveltekit } from '@sveltejs/kit/vite';
import type { UserConfig } from 'vite';
import { purgeCss } from 'vite-plugin-tailwind-purgecss';

const config: UserConfig = {
	plugins: [sveltekit(), purgeCss()],
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}']
	},
	server: {
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true,
				headers: {
					'X-WebAuth-User': 'default',
					'X-WebAuth-Groups': 'default-group,test-group,secret-group',
					'X-WebAuth-Roles': 'default-role,admin'
				},
				rewrite: path => path.replace(/^\/api/, '')
			}
		},
	},
};

export default config;
