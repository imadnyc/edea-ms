<script lang="ts">
	import { superForm } from 'sveltekit-superforms/client';
	import SuperDebug from 'sveltekit-superforms/client/SuperDebug.svelte';

	// Props
	/** Exposes parent props to this component. */
	export let parent: any;
	// Stores
	import { modalStore } from '@skeletonlabs/skeleton';

	// Modal metadata, default to create modal but should also work as update form
	const form_id = $modalStore[0].meta?.form_id || 'create-specification-form';
	const project_id = $modalStore[0].meta?.project_id || $modalStore[0].meta?.row.project_id;
	const row = $modalStore[0].meta?.row || undefined;

	// Base Classes
	const cBase = 'card p-4 w-modal shadow-xl space-y-4';
	const cHeader = 'text-2xl font-bold';
	const cForm = 'border border-surface-500 p-4 space-y-4 rounded-container-token';

	const { form, errors, enhance, constraints } = superForm(parent.form, {
		onUpdated({ form }) {
			if (form.valid) {
				modalStoreUpdate(form);
			}
		},
		id: form_id
	});

	$form.project_id = project_id;

	if (row) {
		$form.id = row.id;
		$form.name = row.name;
		$form.unit = row.unit;
		$form.minimum = row.minimum;
		$form.typical = row.typical;
		$form.maximum = row.maximum;
	}

	function formClose() {
		modalStore.close();
	}

	function modalStoreUpdate(form: any) {
		if ($modalStore[0]?.response) $modalStore[0].response(form);
		modalStore.close();
	}
</script>

<!-- @component Form for creating new specifications. -->

<div class={cBase}>
	<header class={cHeader}>{$modalStore[0]?.title ?? '(title missing)'}</header>
	<article>{$modalStore[0]?.body ?? '(body missing)'}</article>
	<form id={form_id} class="modal-form {cForm}" method="POST" use:enhance>
		{#if row}
			<input type="hidden" name="id" bind:value={$form.id} />
		{/if}
		<input type="hidden" name="project_id" bind:value={$form.project_id} />
		<label class="label">
			<span>Name</span>
			<input
				name="name"
				class="input"
				type="text"
				data-invalid={$errors.name}
				bind:value={$form.name}
				{...$constraints.name}
				placeholder="Enter name..."
			/>
			{#if $errors.name}<span class="invalid">{$errors.name}</span>{/if}
		</label>
		<label class="label">
			<span>Unit</span>
			<input
				name="unit"
				class="input"
				type="text"
				data-invalid={$errors.unit}
				bind:value={$form.unit}
				{...$constraints.unit}
				placeholder="Enter unit..."
			/>
			{#if $errors.unit}<span class="invalid">{$errors.unit}</span>{/if}
		</label>
		<label class="label">
			<span>Minimum</span>
			<input
				name="minimum"
				class="input"
				type="text"
				data-invalid={$errors.minimum}
				bind:value={$form.minimum}
				{...$constraints.minimum}
				placeholder="Enter minimum..."
			/>
			{#if $errors.minimum}<span class="invalid">{$errors.minimum}</span>{/if}
		</label>
		<label class="label">
			<span>Typical</span>
			<input
				name="typical"
				class="input"
				type="text"
				data-invalid={$errors.typical}
				bind:value={$form.typical}
				{...$constraints.typical}
				placeholder="Enter typical..."
			/>
			{#if $errors.typical}<span class="invalid">{$errors.typical}</span>{/if}
		</label>
		<label class="label">
			<span>Maximum</span>
			<input
				name="maximum"
				class="input"
				type="text"
				data-invalid={$errors.maximum}
				bind:value={$form.maximum}
				{...$constraints.maximum}
				placeholder="Enter maximum..."
			/>
			{#if $errors.maximum}<span class="invalid">{$errors.maximum}</span>{/if}
		</label>
		<footer class="modal-footer {parent.regionFooter}">
			<button class="btn {parent.buttonPositive}">Submit</button>
			<button class="btn {parent.buttonNeutral}" on:click={formClose}
				>{parent.buttonTextCancel}</button
			>
		</footer>
	</form>
</div>
