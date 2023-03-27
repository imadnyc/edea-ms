<script lang="ts">
    import '@skeletonlabs/skeleton/themes/theme-skeleton.css';
    import '@skeletonlabs/skeleton/styles/all.css';
    import '../app.postcss';
    import {AppBar, AppShell, Drawer, drawerStore} from '@skeletonlabs/skeleton';
    import Navigation from '$lib/navigation/Navigation.svelte';

    function drawerOpen() {
        drawerStore.open({});
    }
</script>

<Drawer>
    <Navigation/>
</Drawer>

<AppShell slotSidebarLeft="bg-surface-500/5 w-0 lg:w-64">
    <svelte:fragment slot="header">
        <!-- App Bar -->
        <AppBar>
            <svelte:fragment slot="lead">
                <div class="flex items-center">
                    <button class="lg:hidden btn btn-sm mr-4" on:click={drawerOpen}>
            <span>
                <svg viewBox="0 0 100 80" class="fill-token w-4 h-4">
                    <rect width="100" height="20"/>
                    <rect y="30" width="100" height="20"/>
                    <rect y="60" width="100" height="20"/>
                </svg>
            </span>
                    </button>
                    <strong class="text-xl uppercase">EDeA</strong>
                </div>
            </svelte:fragment>
            <svelte:fragment slot="trail">
                <a
                        class="btn btn-sm variant-ghost-surface"
                        href="https://blog.edea.dev"
                        target="_blank"
                        rel="noreferrer"
                >
                    Blog
                </a>
                <a
                        class="btn btn-sm variant-ghost-surface"
                        href="https://tmc.edea.dev"
                        target="_blank"
                        rel="noreferrer"
                >
                    TMC Docs
                </a>
                <a
                        class="btn btn-sm variant-ghost-surface"
                        href="https://gitlab.com/edea-dev/edea-ms"
                        target="_blank"
                        rel="noreferrer"
                >
                    GitLab
                </a>
            </svelte:fragment>
        </AppBar>
    </svelte:fragment>
    <svelte:fragment slot="sidebarLeft">
        <Navigation/>
    </svelte:fragment>
    <!-- Page Route Content -->
    <slot/>
</AppShell>