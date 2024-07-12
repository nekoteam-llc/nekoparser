import { z } from "zod"

export const formSchema = z
  .object({
    url: z.string().min(2).max(2048).optional(),
    xlsx: z
      .instanceof(File)
      .refine(
        (file) => {
          return file.name.endsWith(".xlsx")
        },
        { message: "The file should be an Excel file." },
      )
      .refine(
        (file) => {
          return file.size < 1024 * 1024 * 50
        },
        { message: "The file should be less than 50MB." },
      )
      .optional(),
  })
  .refine(
    (value) => {
      const { url, xlsx } = value
      if ((url && xlsx) || (!url && !xlsx)) {
        throw new Error("Either 'url' or 'xlsx' should be provided, but not both or neither.")
      }
      return true
    },
    { message: "Either 'url' or 'xlsx' should be provided, but not both or neither." },
  )

export type FormSchema = typeof formSchema
