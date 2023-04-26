import { z } from 'zod';

export const Specification = z.object({
    id: z.number().nullable(),
    project_id: z.number(),
    name: z.string(),
    unit: z.string().default(""),
    minimum: z.number(),
    typical: z.number(),
    maximum: z.number()
});

export type SpecificationSchema = typeof Specification
