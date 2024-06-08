<script lang="ts">
  import { ArrowBigLeft } from "lucide-svelte"
  import { Button } from "$lib/components/ui/button/index.js"
  import HotKeys from "$lib/custom/hotkeys.svelte"

  function back(_e: Event) {
    window.history.back()
  }
</script>

<Button variant="default" on:click={back} class="my-2 {$$props.class}">
  <ArrowBigLeft class="mr-1.5 h-4 w-4" />
  Back
  <HotKeys keys={["z"]} on:hot={back} />
</Button>
