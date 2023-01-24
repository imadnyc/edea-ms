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

export const load = (({ fetch, params }) => {
    return {
        testruns: fetch("/api/testruns/project/" + params.slug)
            .then(response => {
                if (!response.ok) {
                    throw error(response.status, response.statusText)
                }
                return response.json() as Promise<TestRun[]>
            }),
        specifications: fetch("/api/specifications/project/" + params.slug)
            .then(response => {
                if (!response.ok) {
                    throw error(response.status, response.statusText)
                }
                return response.json() as Promise<Specification[]>
            }),
        name: params.slug
    }
}) satisfies PageLoad;
