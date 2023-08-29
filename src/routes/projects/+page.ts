import type { Project, User } from '$lib/models/models';
import type { PageLoad } from './$types';

export const load = (async ({ fetch, params }) => {
    const projects = await fetch("/api/projects");
    const user = await fetch("/api/users/self");
    return {
        projects: await (projects.json() as Promise<Project[]>),
        user: await (user.json() as Promise<User>)
    }
}) satisfies PageLoad;
