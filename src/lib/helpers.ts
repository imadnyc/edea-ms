import { error } from '@sveltejs/kit';
import type { TestRun } from '$lib/models/models';

export async function getTestRunData(fetch: (input: RequestInfo | URL, init?: RequestInit | undefined) => Promise<Response>, id: string, headers: Headers) {
    const run = await fetch("/api/testruns/" + id, { headers })
        .then(response => {
            if (!response.ok) {
                throw error(response.status, response.statusText);
            }
            return response.json() as Promise<TestRun>;
        });

    const measurements = await fetch("/api/testruns/measurements/" + run.id, { headers })
        .then(response => {
            if (!response.ok) {
                throw error(response.status, response.statusText);
            }
            return response.json() as Promise<Array<Object>>;
        });
    return { run, measurements };
}