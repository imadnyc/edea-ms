<script lang="ts">
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<div class="container mx-auto p-8 space-y-8">
	<h1>EDeA-MS Projects</h1>

	<div class="table-container">
		<table class="table table-hover">
			<thead>
				<th>Project ID</th>
				<th>Name</th>
			</thead><tbody>
				{#each data.projects as project}
					<tr>
						<td><a href="/project/{project.number}">{project.number}</a></td><td>{project.name}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
