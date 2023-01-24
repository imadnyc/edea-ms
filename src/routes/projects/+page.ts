import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

type Project = {
    id: number;
    number: string;
    name: string;
}

export const load = (async ({fetch,  params }) => {
    const resp = await fetch("/api/projects");
    return { projects: await (resp.json() as Promise<Project[]>)}
}) satisfies PageLoad;
