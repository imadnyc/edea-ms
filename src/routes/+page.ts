import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import type { TestRun } from '$lib/models/models';

export const load = (async ({ fetch, params }) => {

    return {
        testruns: fetch("/api/testruns/overview")
            .then(response => {
                if (!response.ok) {
                    throw error(response.status, response.statusText)
                }
                return response.json() as Promise<TestRun[]>
            })
    }
}) satisfies PageLoad;
