<script lang="ts">
	import type { PageData } from './$types';
	import SimpleTable from '$lib/tables/SimpleTable.svelte';
	import { readable } from 'svelte/store';

	import { VegaLite } from '$lib/svelte-vega';

	export let data: PageData;

	const vegaData = { measurements: data.measurements };
	const hasVegaViz = data.testrun.data?.vega_lite ? true : false;
</script>

<div class="container mx-auto p-8 space-y-8">
	<h1>Testrun {data.name}</h1>

	{#if data.measurements.length > 0}
		<SimpleTable data={readable(data.measurements)} />
		{#if hasVegaViz && data.testrun.data?.vega_lite}
			<div>
				<h2>Visualizations</h2>
				<VegaLite data={vegaData} spec={data.testrun.data.vega_lite} />
			</div>
		{/if}
	{:else}
		<p>No Testrun data available.</p>
	{/if}
</div>
