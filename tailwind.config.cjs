const config = {
	content: [
		require('path').join(require.resolve('@skeletonlabs/skeleton'), '../**/*.{html,js,svelte,ts}')
	],

	theme: {
		extend: {}
	},

	plugins: [
		require('@skeletonlabs/skeleton/tailwind/skeleton.cjs')
	]
};

module.exports = config;
