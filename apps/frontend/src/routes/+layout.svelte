<script>
  import "../app.css"
  import { Toaster } from "svelte-sonner"
  import Settings from "./(components)/settings.svelte"
</script>

<slot />

<Settings />
<Toaster />

<style></style>
