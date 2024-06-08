import { z } from "zod"

export const formSchema = z.object({
  url: z.string().min(2).max(2048),
})

export type FormSchema = typeof formSchema
