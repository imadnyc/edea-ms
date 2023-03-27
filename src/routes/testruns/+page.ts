import type { TestRun } from '$lib/models/models';
import type {PageLoad} from './$types';

export const load = (async ({fetch, params}) => {
    const headers = new Headers();
    headers.append('X-WebAuth-User', 'default');
    const resp = await fetch("/api/testruns", {headers});
    return {testruns: await (resp.json() as Promise<TestRun[]>)}
}) satisfies PageLoad;
