<script lang="ts">
	import '../theme.postcss';
	import '@skeletonlabs/skeleton/styles/skeleton.css';
	import '../app.postcss';
	import {
		AppBar,
		AppShell,
		Drawer,
		drawerStore,
		Modal,
		Toast,
		type ModalComponent
	} from '@skeletonlabs/skeleton';
	import Navigation from '$lib/navigation/Navigation.svelte';
	import { LightSwitch } from '@skeletonlabs/skeleton';
	import SpecificationForm from '$lib/modals/SpecificationForm.svelte';
	import ProjectForm from '$lib/modals/ProjectForm.svelte';

	function drawerOpen() {
		drawerStore.open({});
	}

	const modalComponentRegistry: Record<string, ModalComponent> = {
		modalSpecificationForm: {
			ref: SpecificationForm
		},
		modalProjectForm: {
			ref: ProjectForm
		}
	};
</script>

<Drawer>
	<Navigation />
</Drawer>

<Modal components={modalComponentRegistry} />

<AppShell slotSidebarLeft="bg-surface-500/5 w-0 lg:w-64">
	<svelte:fragment slot="header">
		<!-- App Bar -->
		<AppBar background="bg-primary-500">
			<svelte:fragment slot="lead">
				<div class="flex items-center">
					<button class="lg:hidden btn btn-sm mr-4" on:click={drawerOpen}>
						<span>
							<svg viewBox="0 0 100 80" class="fill-token w-4 h-4">
								<rect width="100" height="20" />
								<rect y="30" width="100" height="20" />
								<rect y="60" width="100" height="20" />
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
				<LightSwitch />
			</svelte:fragment>
		</AppBar>
	</svelte:fragment>
	<svelte:fragment slot="sidebarLeft">
		<Navigation />
	</svelte:fragment>
	<Toast />
	<!-- Page Route Content -->
	<slot />
</AppShell>
