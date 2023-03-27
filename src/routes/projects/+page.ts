import type { Project } from '$lib/models/models';
import type {PageLoad} from './$types';

export const load = (async ({fetch, params}) => {
    const headers = new Headers();
    headers.append('X-WebAuth-User', 'default');
    const resp = await fetch("/api/projects", {headers});
    return {projects: await (resp.json() as Promise<Project[]>)}
}) satisfies PageLoad;
