<script lang="ts">
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<div class="container mx-auto p-8 space-y-8">
	<h1>Project {data.name}</h1>

	<div>
		<h2>Specifications</h2>
		<div class="table-container">
			<table class="table table-hover">
				<thead>
					<th>Name</th>
					<th>Unit</th>
					<th>Minumum</th>
					<th>Typical</th>
					<th>Maximum</th>
				</thead>
				<tbody>
					{#each data.specifications as spec}
						<tr>
							<a href="/specification/{spec.id}">
								<td>{spec.name}</td>
								<td>{spec.unit}</td>
								<td>{spec.minimum}</td>
								<td>{spec.typical}</td>
								<td>{spec.maximum}</td>
							</a>
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
					<th>Short Code</th>
					<th>DUT ID</th>
					<th>Machine Hostname</th>
					<th>Username</th>
					<th>Test name</th>
				</thead>
				<tbody>
					{#each data.testruns as run}
						<tr>
							<a href="/testruns/{run.id}">
								<td>{run.short_code}</td>
								<td>{run.dut_id}</td>
								<td>{run.machine_hostname}</td>
								<td>{run.user_name}</td>
								<td>{run.test_name}</td>
							</a>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>
