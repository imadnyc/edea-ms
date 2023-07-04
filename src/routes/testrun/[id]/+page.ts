import type { PageLoad } from './$types';
import { getTestRunData } from "$lib/helpers";


export const load = (async ({ fetch, params }) => {
    const headers = new Headers();
    headers.append('X-Webauth-User', 'default');

    const { run, measurements } = await getTestRunData(fetch, params.id, headers);

    return {
        testrun: run,
        measurements: measurements,
        name: params.id
    }
}) satisfies PageLoad;
