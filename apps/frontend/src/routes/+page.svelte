<script lang="ts">
  import DataSources from "./(components)/data-sources.svelte"
  import NewSource from "./(components)/new-source.svelte"
  import type { PageData } from "./$types.js"
  import { OpenAPI } from "$client/index"
  import StatusTracker from "$lib/custom/status-tracker.svelte"
  import { dev } from "$app/environment"

  export let data: PageData

  if (dev) {
    OpenAPI.BASE = "https://nekoparser-dev.dan.tatar"
  }
</script>

<div class="hidden h-screen flex-1 flex-col space-y-8 p-8 md:flex">
  <div>
    <h2 class="text-2xl font-bold tracking-tight">Welcome back!</h2>
    <p class="text-muted-foreground">Here you can interact with the sources</p>
    <NewSource data={data.form} />
  </div>
  <DataSources />
</div>

<StatusTracker />
