import type { Project } from '$lib/models/models';
import { writable, type Writable } from 'svelte/store';

export const projects: Writable<Project[]> = writable([]);
