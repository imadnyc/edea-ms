import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import type { TestRun, Specification } from '$lib/models/models';


export const load = (async ({ fetch, params }) => {
    const headers = new Headers();
    headers.append('X-Webauth-User', 'default');

    const run = await fetch("/api/testruns/short_code/" + params.short_code, { headers })
    .then(response => {
        if (!response.ok) {
            throw error(response.status, response.statusText)
        }
        return response.json() as Promise<TestRun>
    });

    return {
        testrun: run,
        measurements: fetch("/api/testruns/measurements/" + run.id, { headers })
            .then(response => {
                if (!response.ok) {
                    throw error(response.status, response.statusText)
                }
                return response.json() as Promise<{}>
            }),
        name: params.short_code
    }
}) satisfies PageLoad;
