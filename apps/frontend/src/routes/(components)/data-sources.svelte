<script lang="ts">
  import { onMount } from "svelte"
  import DataSource from "./data-source.svelte"
  import { type ExcelSourceModel, type WebsiteSourceModel } from "$client/index"

  let sources:
    | {
      excel_sources: ExcelSourceModel[]
      web_sources: WebsiteSourceModel[]
    }
    | undefined
    | null

  onMount(() => {
    const PROTOCOL = window.location.protocol === "https:" ? "wss" : "ws"
    const SOCKET_URL = `${PROTOCOL}://${window.location.host}/api/v1/sources/wss`
    function createSocket() {
      const socket = new WebSocket(SOCKET_URL)
      socket.onmessage = (event) => {
        const data: {
          excel_sources: ExcelSourceModel[]
          web_sources: WebsiteSourceModel[]
        } = JSON.parse(event.data)

        if (JSON.stringify(data) !== JSON.stringify(sources)) {
          if (data === undefined || data === null) {
            sources = null
            return
          }
          data.excel_sources.sort((a, b) => a.filename.localeCompare(b.filename))
          data.web_sources.sort((a, b) => a.title.localeCompare(b.title))
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

<div class="columns-3" style="font-size: 0px;">
  {#if sources !== undefined}
    {#each sources?.web_sources ?? [] as source}
      <DataSource
        id={source.id}
        icon={source.icon}
        title={source.title}
        description={source.description}
        state={source.state}
      />
    {/each}
    {#each sources?.excel_sources ?? [] as source}
      <DataSource id={source.id} title={source.filename} state={source.state} />
    {/each}
  {:else}
    {#each Array.from({ length: 16 }) as _, i}
      <div
        class="w-full break-inside-avoid pb-4 pr-4"
        style="height: {i % 2 === 0 ? "125px" : "250px"}"
      >
        <div
          class="block h-full w-full animate-shine rounded-xl border border-border/10 bg-shine bg-200 brightness-125"
        ></div>
      </div>
    {/each}
  {/if}
</div>
