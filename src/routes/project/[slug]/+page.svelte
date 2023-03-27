<script lang="ts">
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<div class="container mx-auto p-8 space-y-8">
	<h1>Project {data.project.name}</h1>

	<div>
		<h2>Specifications</h2>
		<div class="table-container">
			<table class="table table-hover">
				<thead>
					<th>Name</th>
					<th>Unit</th>
					<th>Minimum</th>
					<th>Typical</th>
					<th>Maximum</th>
				</thead>
				<tbody>
					{#each data.specifications as spec}
						<tr>
							<td><a href="/specification/{spec.id}">{spec.id}</a></td>
							<td>{spec.name}</td>
							<td>{spec.unit}</td>
							<td>{spec.minimum}</td>
							<td>{spec.typical}</td>
							<td>{spec.maximum}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
	<div>
		<h2>Testruns</h2>
		<div class="table-container">
			<table class="table table-hover">
				<thead>
					<th>ID</th>
					<th>Short Code</th>
					<th>DUT ID</th>
					<th>Machine Hostname</th>
					<th>Username</th>
					<th>Test name</th>
				</thead>
				<tbody>
					{#each data.testruns as run}
						<tr>
							<td><a href="/testrun/{run.short_code}">{run.id}</a></td>
							<td>{run.short_code}</td>
							<td>{run.dut_id}</td>
							<td>{run.machine_hostname}</td>
							<td>{run.user_name}</td>
							<td>{run.test_name}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>
