<script lang="ts">
	import type { PageData } from './$types';
	import SimpleTable from '$lib/tables/SimpleTable.svelte';
	import { readable } from 'svelte/store';

	import { VegaLite } from 'svelte-vega';

	export let data: PageData;

	const vegaData = { measurements: data.measurements };
	const hasVegaViz = data.testrun.data?.vega_lite ? true : false;

	function exportTestrunData(e: Event) {
		// TODO
	}
</script>

<div class="table-container mx-auto p-8 space-y-8">
	<section class="space-y-2">
		<div class="flex justify-between">
			<h1 class="h1">Testrun {data.name}</h1>
			<button class="btn variant-filled" on:click={exportTestrunData}>Export</button>
		</div>

		{#if data.measurements.length > 0}
			<SimpleTable data={readable(data.measurements)} />
		{:else}
			<p>No Testrun data available.</p>
		{/if}
	</section>

	{#if data.measurements.length > 0 && hasVegaViz && data.testrun.data?.vega_lite}
		<section class="space-y-2">
			<h2 class="h2">Visualizations</h2>
			<VegaLite data={vegaData} spec={data.testrun.data.vega_lite} />
		</section>
	{/if}
</div>
