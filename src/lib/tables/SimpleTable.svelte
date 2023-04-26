<script lang="ts">
	import type { Readable } from 'svelte/store';
	import { DataHandler, Datatable, Th, ThFilter } from '@vincjo/datatables';
	import { columnDef, type Column } from './types';

	let tableElement: HTMLElement | undefined;

	export let data: Readable<Array<Object>>;
	export let columns: Array<Column> | undefined = undefined;
	export let filterable: boolean = false;
	export let rowsPerPage: number = 20;

	if (columns == undefined) {
		columns = Object.keys($data[0]).map((key) => columnDef(key, key));
	}

	const handler = new DataHandler($data, { rowsPerPage: rowsPerPage });

	$: $data, update();
	let rows = handler.getRows();

	const update = () => {
		if (tableElement && tableElement.parentElement) {
			const scrollTop = tableElement.parentElement.scrollTop;
			handler.setRows($data);
			setTimeout(() => {
				if (tableElement?.parentElement) {
					tableElement.parentElement.scrollTop = scrollTop;
				}
			}, 2);
		}
	};
</script>

<div class="table-container">
	<Datatable {handler}>
		<table class="table table-hover" bind:this={tableElement}>
			<thead>
				{#if columns}
					<tr>
						{#each columns as column}
							{#if column.sortable}
								<Th {handler} orderBy={column.key}>{column.header}</Th>
							{:else}
								<th>{column.header}</th>
							{/if}
						{/each}
					</tr>
					{#if filterable}
						<tr>
							<ThFilter {handler} filterBy="first_name" />
							<ThFilter {handler} filterBy="last_name" />
							<ThFilter {handler} filterBy="email" />
							{#each columns as column}
								{#if column.filterable}
									<ThFilter {handler} filterBy={column.key} />
								{:else}
									<th />
								{/if}
							{/each}
						</tr>
					{/if}
				{/if}
			</thead>
			<tbody>
				{#if columns}
					{#each $rows as row}
						<tr>
							{#each columns as column}
								{#if column.component}
									<td class="!pt-2 !pb-2"><svelte:component this={column.component} {row} /></td>
								{:else}
									<td class="!pt-2 !pb-2">{row[column.key]}</td>
								{/if}
							{/each}
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</Datatable>
</div>
