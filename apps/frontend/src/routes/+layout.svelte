<script>
  import "../app.css"
  import { onMount } from "svelte"

  let currentUrl = ""
  onMount(() => {
    currentUrl = window.location.pathname
  })
</script>

<slot />

<img src="/nekologo.png" alt="logo" class="ease absolute right-3 top-3 m-auto h-8 transition-all {currentUrl.includes("/sources/") ? "hidden" : ""}" />

<style></style>
