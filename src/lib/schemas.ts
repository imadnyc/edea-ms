import { z } from 'zod';

export const Project = z.object({
    id: z.number().nullable(),
    short_code: z.string().nullable(),
    name: z.string(),
});

export const Specification = z.object({
    id: z.number().nullable(),
    project_id: z.number(),
    name: z.string(),
    unit: z.string().default(""),
    minimum: z.number(),
    typical: z.number(),
    maximum: z.number()
});

export type ProjectSchema = typeof Project
export type SpecificationSchema = typeof Specification
