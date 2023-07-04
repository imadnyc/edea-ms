<script lang="ts">
	import type { PageData } from './$types';
	import { specifications, selected_ids } from './store';
	import SimpleTable from '$lib/tables/SimpleTable.svelte';
	import { columnDef, type Column, componentColumnDef } from '$lib/tables/types';
	import { readable } from 'svelte/store';
	import { modalStore, type ModalSettings } from '@skeletonlabs/skeleton';
	import Actions from './actions.svelte';
	import DetailLink from './detail_link.svelte';
	import CheckBox from './select_box.svelte';
	import { goto } from '$app/navigation';

	export let data: PageData;

	specifications.set(data.specifications);
	let testruns = readable(data.testruns);

	const specColumns: Column[] = [
		columnDef('id', 'ID'),
		columnDef('project_id', 'Project ID'),
		columnDef('name', 'Name'),
		columnDef('minimum', 'Minimum'),
		columnDef('typical', 'Typical'),
		columnDef('maximum', 'Maximum'),
		columnDef('unit', 'Unit'),
		componentColumnDef('Actions', Actions)
	];

	const testrunColumns: Column[] = [
		componentColumnDef('Select', CheckBox),
		componentColumnDef('ID', DetailLink),
		columnDef('short_code', 'Short code'),
		columnDef('dut_id', 'DUT ID'),
		columnDef('machine_hostname', 'Machine Hostname'),
		columnDef('user_name', 'Username'),
		columnDef('test_name', 'Test Name')
	];

	const modalCreateSpec: ModalSettings = {
		type: 'component',
		title: 'New specification for ' + data.project.name,
		body: '',
		meta: { project_id: data.project.id },
		// Pass the component registry key as a string:
		component: 'modalSpecificationForm',
		response: async (r: any) => {
			if (r) {
				// append new specification to the table
				$specifications.push(r.message);
				specifications.set($specifications);
				modalStore.close();
			}
		}
	};

	function newSpec() {
		modalStore.trigger(modalCreateSpec);
	}

	function compareTestruns() {
		let values = Array.from($selected_ids.values());
		goto(`/project/compare?id=${data.project.number}&testruns=${values.join()}`);
	}
</script>

<div class="container mx-auto p-8 space-y-8">
	<h1>Project {data.project.name}</h1>

	<div>
		<h2>Specifications</h2>
		<button class="btn variant-filled" on:click={newSpec}>Create Specification</button>
		{#if $specifications.length > 0}
			<SimpleTable data={specifications} columns={specColumns} rowsPerPage={10} />
		{:else}
			<p>No specification data available.</p>
		{/if}
	</div>
	<div>
		<h2>Testruns</h2>
		{#if $testruns.length > 0}
			<div>
				{#if $selected_ids.size > 1}
					<button class="btn variant-filled" on:click={compareTestruns}>Compare Selected</button>
				{:else}
					<button class="btn variant-filled" disabled>Compare Selected</button>
				{/if}
				<p>Only testruns with charts can be compared for now.</p>
			</div>
			<SimpleTable data={testruns} columns={testrunColumns} rowsPerPage={10} />
		{:else}
			<p>No testruns available.</p>
		{/if}
	</div>
</div>
