import { defineConfig } from "@hey-api/openapi-ts"

export default defineConfig({
  base: "https://nekoparser.dan.tatar",
  input: "http://localhost:31222/openapi.json",
  output: {
    path: "./src/client",
    format: "prettier",
  },
  client: "axios",
  services: {
    export: true,
    name: "{{name}}API",
    asClass: true,
    operationId: true,
    methodNameBuilder: (service: string, operationId: string) => {
      const strippedApi = operationId.includes("ApiV1")
        ? operationId.split("ApiV1")[0]
        : operationId

      return strippedApi.endsWith(service) ? strippedApi.slice(0, -service.length) : strippedApi
    },
  },
})
