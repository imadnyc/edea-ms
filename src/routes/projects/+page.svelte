<script lang="ts">
	import type { PageData } from './$types';
	import { columnDef, type Column, componentColumnDef } from '$lib/tables/types';
	import SimpleTable from '$lib/tables/SimpleTable.svelte';
	import { modalStore, type ModalSettings } from '@skeletonlabs/skeleton';
	import Actions from './actions.svelte';
	import { projects } from './store';
	import DetailLink from './detail_link.svelte';

	export let data: PageData;

	projects.set(data.projects);

	const columns: Column[] = [
		componentColumnDef('ID', DetailLink),
		columnDef('number', 'Project Number'),
		columnDef('name', 'Name'),
		componentColumnDef('Actions', Actions)
	];

	const modalCreateProject: ModalSettings = {
		type: 'component',
		title: 'New Project',
		body: '',
		// Pass the component registry key as a string:
		component: 'modalProjectForm',
		response: async (r: any) => {
			if (r) {
				// append new specification to the table
				$projects.push(r.message);
				projects.set($projects);
				modalStore.close();
			}
		}
	};

	function newProject() {
		modalStore.trigger(modalCreateProject);
	}
</script>

<div class="container mx-auto p-8 space-y-8">
	<h1>EDeA-MS Projects</h1>

	<div>
		<button class="btn variant-filled" on:click={newProject}>Create Project</button>
		{#if $projects.length > 0}
			<SimpleTable data={projects} columns={columns} rowsPerPage={10} />
		{:else}
			<p>No specification data available.</p>
		{/if}
	</div>
</div>
