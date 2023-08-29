import { getTestRunData } from '$lib/helpers';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import type { Project, TestRun } from '$lib/models/models';

export const load = (async ({ fetch, url }) => {
    let project_id = url.searchParams.get("id");
    let run_ids = url.searchParams.get("testruns")?.split(",").sort();

    const project = await fetch("/api/projects/" + project_id)
        .then(response => {
            if (!response.ok) {
                throw error(response.status, response.statusText)
            }
            return response.json() as Promise<Project>
        });

    let runs: [TestRun, Object[]][] = [];

    run_ids?.forEach(async id => {
        const { run, measurements } = await getTestRunData(fetch, id);
        runs.push([run, measurements]);
    });

    return {
        project: project,
        runs: runs,
    };
}) satisfies PageLoad;
