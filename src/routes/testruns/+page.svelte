<script lang="ts">
	import { TestRunState } from '$lib/models/models';
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<div class="container mx-auto p-8 space-y-8">
	<h1>Testruns</h1>

	<div class="table-container">
	<table class="table table-hover">
		<thead>
			<th>Short Code</th>
			<th>DUT ID</th>
            <th>Hostname</th>
            <th>User</th>
            <th>Test Name</th>
            <th class="table-sort-desc">Created</th>
            <th>Started</th>
            <th>Completed</th>
            <th>State</th>
		<tbody>
			{#each data.testruns as run}
				<tr>
					<td><a href="/testrun/{run.short_code}">{run.short_code}</a></td>
                    <td>{run.dut_id}</td>
                    <td>{run.machine_hostname}</td>
                    <td>{run.user_name}</td>
                    <td>{run.test_name}</td>
                    <td>{run.created_at}</td>
                    <td>{run.started_at}</td>
                    <td>{run.completed_at}</td>
                    <td>{TestRunState[run.state]}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
</div>
