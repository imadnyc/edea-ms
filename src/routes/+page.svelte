<script lang="ts">
	import type { PageData } from './$types';
	import SimpleTable from '$lib/tables/SimpleTable.svelte';
	import { columnDef, type Column } from '$lib/tables/types';
	import { readable } from 'svelte/store';
	import { goto } from '$app/navigation';
	import type { Row } from '@vincjo/datatables';
	import { TestRunState } from '$lib/models/models';

	export let data: PageData;

	let testruns = readable(data.testruns);

	const columns: Column[] = [
		columnDef('id', 'ID'),
		columnDef('short_code', 'Short Code'),
		columnDef('machine_hostname', 'Hostname'),
		columnDef('user_name', 'User'),
		columnDef('test_name', 'Test Name'),
		columnDef('created_at', 'Created', { translate: (v) => new Date(v).toLocaleString('de-DE') }),
		columnDef('started_at', 'Started', { translate: (v) => new Date(v).toLocaleString('de-DE') }),
		columnDef('completed_at', 'Completed', {
			translate: (v) => new Date(v).toLocaleString('de-DE')
		}),
		columnDef('state', 'State', { translate: (v) => TestRunState[v] })
	];

	function rowSelected(e: CustomEvent<Row>) {
		goto(`/testrun/${e.detail.id}`);
	}
</script>

<div class="container mx-auto p-8 space-y-8">
	<section class="space-y-2">
		<h1 class="h1">Welcome to EDeA-MS</h1>
		<p>
			EDeA-MS provides the server part for Test&Measurement as Code setups. See <a
				class="anchor"
				href="https://tmc.edea.dev/">EDeA-TMC</a
			> for the library.
		</p>
	</section>
	<section class="space-y-2">
		<h2 class="h2">Recent Testruns</h2>
		{#if data.testruns.length > 0}
			<SimpleTable
				data={testruns}
				{columns}
				rowsPerPage={20}
				on:selected={rowSelected}
				search={false}
			/>
		{:else}
			<p>No recent testruns.</p>
		{/if}
	</section>
</div>
