<script lang="ts">
    import {getDrawerStore} from '@skeletonlabs/skeleton';

    function drawerClose(): void {
        getDrawerStore().close();
    }
</script>

<nav class="list-nav p-4">
    <ul>
        <li><a href="/" on:click={drawerClose}>Homepage</a></li>
        <li><a href="/projects" on:click={drawerClose}>Projects</a></li>
        <li><a href="/testruns" on:click={drawerClose}>Testruns</a></li>
    </ul>
</nav>
