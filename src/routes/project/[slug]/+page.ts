import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

type TestRun = {
    id: number;
    project_id: number;
    short_code: string;
    dut_id: string;
    machine_hostname: string;
    user_name: string;
    test_name: string;
    data?: {}
}

type Specification = {
    id?: number;
    project_id: number;
    name: string;
    unit: string;
    minimum?: number;
    typical?: number;
    maximum?: number;
}

type Project = {
    id: number;
    number: string;
    name: string;
}

export const load = (async ({ fetch, params }) => {
    const headers = new Headers();
    headers.append('X-Webauth-User', 'default');

    const project = await fetch("/api/projects/" + params.slug, { headers })
        .then(response => {
            if (!response.ok) {
                throw error(response.status, response.statusText)
            }
            return response.json() as Promise<Project>
        });

    return {
        testruns: fetch("/api/testruns/project/" + project.id, { headers })
            .then(response => {
                if (!response.ok) {
                    throw error(response.status, response.statusText)
                }
                return response.json() as Promise<TestRun[]>
            }),
        specifications: fetch("/api/specifications/project/" + project.id, { headers })
            .then(response => {
                if (!response.ok) {
                    throw error(response.status, response.statusText)
                }
                return response.json() as Promise<Specification[]>
            }),
        project: project,
    }
}) satisfies PageLoad;
