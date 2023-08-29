<script lang="ts">
	import type { PageData } from './$types';

	import { VegaLite } from 'svelte-vega';

	export let data: PageData;
</script>

<div class="container mx-auto p-8 space-y-8">
	<h2 class="h2">Compare testruns</h2>
	<table class="table table-hover">
		<thead>
			{#each data.runs as run}
				<th>ID: {run[0].id}, SC: {run[0].short_code}</th>
			{/each}
		</thead>
		<tbody>
			<tr>
				{#each data.runs as run}
					{#if run[0].data?.vega_lite}
						<td>
							<p><a href="/testruns/{run[0].id}">Run {run[0].id}</a></p>
							<p>Started at {run[0].started_at}, completed at {run[0].completed_at}</p>
							<VegaLite data={{ measurements: run[1] }} spec={run[0].data?.vega_lite} />
						</td>
					{:else}
						<p>no viz for {run[0].id}</p>
					{/if}
				{/each}
			</tr>
		</tbody>
	</table>
</div>
