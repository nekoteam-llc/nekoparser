<script lang="ts">
  import { onMount } from "svelte"
  import DataSource from "./data-source.svelte"
  import { type Source } from "$client/index"
  import Skeleton from "$lib/components/ui/skeleton/skeleton.svelte"

  let sources: [Source] | undefined | null

  onMount(() => {
    const PROTOCOL = window.location.protocol === "https:" ? "wss" : "ws"
    const SOCKET_URL = `${PROTOCOL}://${window.location.host}/api/v1/sources/wss`
    function createSocket() {
      const socket = new WebSocket(SOCKET_URL)
      socket.onmessage = (event) => {
        const data: [Source] = JSON.parse(event.data)
        if (JSON.stringify(data) !== JSON.stringify(sources)) {
          if (data === undefined || data === null) {
            sources = null
            return
          }
          data.sort((a, b) => a.title.localeCompare(b.title))
          sources = data
        }
      }
      socket.onclose = () => {
        setTimeout(createSocket, 1000)
      }
    }

    createSocket()
  })
</script>

<div class="grid grid-cols-3 gap-4">
  {#if sources !== undefined}
    {#each sources ?? [] as source}
      <DataSource
        id={source.id}
        icon={source.icon}
        title={source.title}
        description={source.description}
        state={source.state}
      />
    {/each}
  {:else}
    {#each Array.from({ length: 6 }) as _}
      <Skeleton class="h-[200px] w-[450px] rounded-xl" />
    {/each}
  {/if}
</div>
