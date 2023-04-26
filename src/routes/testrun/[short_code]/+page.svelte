<script lang="ts">
	import type { PageData } from './$types';
	import SimpleTable from '$lib/tables/SimpleTable.svelte';
	import { readable } from 'svelte/store';

	export let data: PageData;
</script>

<div class="container mx-auto p-8 space-y-8">
	<h1>Testrun {data.name}</h1>

	{#if data.measurements.length > 0}
		<SimpleTable data={readable(data.measurements)} />
	{:else}
		<p>No Testrun data available.</p>
	{/if}
</div>
