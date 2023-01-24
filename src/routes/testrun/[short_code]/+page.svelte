<script lang="ts">
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<div class="container mx-auto p-8 space-y-8">
	<h1>Testrun {data.name}</h1>


    <div class="table-container">
        <table class="table table-hover">
            <thead>
                <th>Measurement Columns</th>
            </thead>
            <tbody>
                {#each data.measurement_entries as entry}
                    <tr>
                        <td>TODO: join this server-side and display here</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
</div>
