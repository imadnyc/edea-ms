<script lang="ts">
    import type {PageData} from './$types';

    export let data: PageData;

    export let mc = data.measurements.columns;
</script>

<div class="container mx-auto p-8 space-y-8">
    <h1>Testrun {data.name}</h1>


    <div class="table-container">
        <table class="table table-hover">
            <thead>
            <tr>
                {#each mc as entry}
                    <th>{entry.name}</th>
                {/each}
            </tr>
            </thead>
            <tbody>
            {#each mc[0].values as _, i}
                <tr>
                    {#each mc as entry}
                        <td>{entry.values[i]}</td>
                    {/each}
                </tr>
            {/each}

            </tbody>
        </table>
    </div>
</div>
