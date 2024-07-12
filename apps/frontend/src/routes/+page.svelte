<script lang="ts">
  import DataSources from "./(components)/data-sources.svelte"
  import NewSource from "./(components)/new-source.svelte"
  import { OpenAPI } from "$client/index"
  import StatusTracker from "$lib/custom/status-tracker.svelte"
  import { dev } from "$app/environment"

  if (dev) {
    OpenAPI.BASE = "https://nekoparser-dev.dan.tatar"
  }
</script>

<div class="hidden h-screen flex-1 flex-col space-y-8 p-8 md:flex">
  <div>
    <h2 class="flex items-end text-2xl font-semibold tracking-tight">
      Welcome back to
      <img src="/nekologo.png" class="ml-2 h-6" alt="logo" />
      !
    </h2>
    <p class="text-muted-foreground">Here you can interact with the sources</p>
    <NewSource />
  </div>
  <DataSources />
</div>

<StatusTracker />
