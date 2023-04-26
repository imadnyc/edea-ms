import { superValidate, message } from 'sveltekit-superforms/server';
import { fail } from '@sveltejs/kit';

import { Specification } from '$lib/schemas';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async (event) => {
		const data = await event.request.formData();
		const form = await superValidate(data, Specification, {
			id: 'create-specification-form'
		});

		if (!form.valid) return fail(400, { form });

		const request_body = JSON.stringify(form.data);

		const headers = new Headers();
		headers.append('X-WebAuth-User', 'default');
		headers.append('Content-Type', 'application/json');

		const auth = event.request.headers.get("X-WebAuth-User");
		if (auth) {
			headers.append('X-WebAuth-User', auth);
		}

		let url = "/api/specifications";
		let method = "POST";
		if (form.data.id) {
			url = "/api/specifications/" + form.data.id
			method = "PUT";
		}
		const resp = await event.fetch(url, {
			headers: headers,
			method: method,
			body: request_body,
		});

		const body = await resp.json();

		if (resp.ok) {
			return message(form, body)
		}
		return fail(400, body);
	}
};
