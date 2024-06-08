<script lang="ts">
  import {
    Braces,
    ExternalLink,
    LoaderCircle,
    SquareDashedMousePointer,
    Table as TableIcon,
    Trash,
  } from "lucide-svelte"
  import { toast } from "svelte-sonner"
  import { onMount } from "svelte"
  import { json2csv } from "json-2-csv"
  import {
    type GetSourceApiV1SourcesSourceIdGetResponse,
    OpenAPI,
    type Source,
    SourcesAPI,
  } from "$client/index"
  import BackBtn from "$lib/custom/back-btn.svelte"
  import StatusTracker from "$lib/custom/status-tracker.svelte"
  import { Skeleton } from "$lib/components/ui/skeleton"
  import * as Avatar from "$lib/components/ui/avatar"
  import * as AlertDialog from "$lib/components/ui/alert-dialog/index.js"
  import { dev } from "$app/environment"
  import Button from "$lib/components/ui/button/button.svelte"
  import HotKeys from "$lib/custom/hotkeys.svelte"
  import * as Table from "$lib/components/ui/table"
  import * as Popover from "$lib/components/ui/popover"
  import Badge from "$lib/components/ui/badge/badge.svelte"

  if (dev) {
    OpenAPI.BASE = "https://nekoparser-dev.dan.tatar"
  }

  export let data: { slug: string }

  let source: GetSourceApiV1SourcesSourceIdGetResponse | null = null

  const openWebsite = () => {
    if (!source) {
      toast.loading("Loading source data...")
      // eslint-disable-next-line no-empty, no-unmodified-loop-condition
      while (!source) {}
    }
    toast.success("Good luck!")

    // Weird stuff happens if you leave the page immediately programmatically
    setTimeout(() => {
      window.open(source?.url, "_blank")
    }, 500)
  }

  let alertOpen = false

  function handleOpenHotkey() {
    alertOpen = true
  }

  function deleteSource() {
    SourcesAPI.deleteSource({ sourceId: data.slug })
      .then(() => {
        window.location.href = "/"
      })
      .catch((_) => {
        toast.error("Failed to delete source.")
      })
  }

  function handleKeydownSubmit(event: KeyboardEvent) {
    if (event.key === "Enter") {
      deleteSource()
    }
  }

  let sources: [Source] | undefined | null
  let products: {
    product_hash: string
    data: any
    last_processed: string
  }[] = []

  onMount(() => {
    const PROTOCOL = window.location.protocol === "https:" ? "wss" : "ws"
    const SOCKET_URL = `${PROTOCOL}://${window.location.host}/api/v1/sources/wss`
    function createSocket() {
      const socket = new WebSocket(SOCKET_URL)
      socket.onmessage = (event) => {
        const eventData: [Source] = JSON.parse(event.data)
        if (JSON.stringify(eventData) !== JSON.stringify(sources)) {
          if (eventData === undefined || eventData === null) {
            sources = null
            return
          }
          sources = eventData
          const possibleSource = eventData.find(source => source.id === data.slug)
          if (possibleSource !== undefined) {
            source = possibleSource
          }
        }
      }
      socket.onclose = () => {
        setTimeout(createSocket, 1000)
      }
    }

    createSocket()

    const DATA_SOCKET_URL = `${PROTOCOL}://${window.location.host}/api/v1/sources/wss/${data.slug}/data`
    function createDataSocket() {
      const socket = new WebSocket(DATA_SOCKET_URL)
      socket.onmessage = (event) => {
        products = JSON.parse(event.data)
        products = products.slice()
      }
      socket.onclose = () => {
        setTimeout(createDataSocket, 1000)
      }
    }

    createDataSocket()
  })

  function handleDownloadCSV() {
    const csv = json2csv(products.map(product => product.data))
    const blob = new Blob([csv], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    const sourceUrl = source?.url ?? "https://unknown-source.tld"
    const date = new Date()
    a.download = `products-${new URL(sourceUrl).hostname}-${date.toISOString().split("T")[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast.success("Exported products to CSV!")
  }

  function handleDownloadJSON() {
    const json = JSON.stringify(
      products.map(product => product.data),
      null,
      2,
    )
    const blob = new Blob([json], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    const sourceUrl = source?.url ?? "https://unknown-source.tld"
    const date = new Date()
    a.download = `products-${new URL(sourceUrl).hostname}-${date.toISOString().split("T")[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success("Exported products to JSON!")
  }

  const keys: string[] = [
    "url",
    "main_image",
    "sku",
    "name",
    "description",
    "keywords",
    "price",
    "currency",
    "measure_unit",
  ]
  const key_translation: Record<string, string> = {
    url: "URL",
    main_image: "Image",
    sku: "SKU",
    name: "Name",
    keywords: "Keywords",
    description: "Description",
    price: "Price",
    currency: "Currency",
    measure_unit: "Measure unit",
  }
</script>

<div class="p-8">
  {#if !source}
    <div class="flex items-center">
      <Skeleton class="h-[32px] w-[32px] rounded-full" />
      <Skeleton class="ml-2 h-[32px] w-[20%]" />
      <Skeleton class="ml-4 h-[22px] w-[10%]" />
    </div>
    <div class="ml-10 mt-2">
      <Skeleton class="h-[24px] w-[30%]" />
      <Skeleton class="mt-2 h-[24px] w-[25%]" />
      <Skeleton class="mt-2 h-[24px] w-[27%]" />
    </div>
  {:else}
    <div class="flex items-center">
      <Avatar.Root class="h-[32px] w-[32px]">
        <Avatar.Image src={source.icon} alt={source.title} />
        <Avatar.Fallback>{source.title.substring(0, 2).toUpperCase()}</Avatar.Fallback>
      </Avatar.Root>
      <h2 class="ml-2 text-2xl font-semibold tracking-tight">{source.title}</h2>
      <Badge class="ml-4">
        {source.state.replaceAll("_", "\xA0")}
      </Badge>
    </div>
    <p class="ml-10 mt-2 w-1/3 text-muted-foreground">
      {source.description}
    </p>
  {/if}
  <div class="mt-6 flex gap-4">
    <BackBtn class="m-0" />
    {#if source?.state === "xpaths_pending"}
      <Button on:click={openWebsite} class="m-0">
        <SquareDashedMousePointer class="mr-1.5 h-4 w-4" />
        Continue setup
        <HotKeys keys={["o"]} on:hot={openWebsite} />
      </Button>
    {/if}
    <Button class="m-0" on:click={handleDownloadCSV} disabled={products.length === 0}>
      {#if products.length === 0}
        <LoaderCircle class="mr-1.5 h-4 w-4 animate-spin" />
      {:else}
        <TableIcon class="mr-1.5 h-4 w-4" />
      {/if}
      Download CSV
      <HotKeys keys={["c"]} on:hot={handleDownloadCSV} condition={products.length > 0} />
    </Button>
    <Button class="m-0" on:click={handleDownloadJSON} disabled={products.length === 0}>
      {#if products.length === 0}
        <LoaderCircle class="mr-1.5 h-4 w-4 animate-spin" />
      {:else}
        <Braces class="mr-1.5 h-4 w-4" />
      {/if}
      Download JSON
      <HotKeys keys={["j"]} on:hot={handleDownloadJSON} condition={products.length > 0} />
    </Button>
    <AlertDialog.Root
      open={alertOpen}
      onOpenChange={(state) => {
        alertOpen = state
      }}
    >
      <AlertDialog.Trigger asChild let:builder>
        <Button builders={[builder]} variant="destructive">
          <Trash class="mr-1.5 h-4 w-4" />
          Delete source
          <HotKeys keys={["d"]} on:hot={handleOpenHotkey} />
        </Button>
      </AlertDialog.Trigger>
      <AlertDialog.Content>
        <AlertDialog.Header>
          <AlertDialog.Title>Are you sure you want to delete the source?</AlertDialog.Title>
          <AlertDialog.Description>
            This action cannot be undone. All data from this source will be lost as well!
          </AlertDialog.Description>
        </AlertDialog.Header>
        <AlertDialog.Footer>
          <AlertDialog.Cancel>Cancel</AlertDialog.Cancel>
          <AlertDialog.Action asChild let:builder>
            <Button
              builders={[builder]}
              on:click={deleteSource}
              on:keydown={handleKeydownSubmit}
              variant="destructive"
            >
              Delete
            </Button>
          </AlertDialog.Action>
        </AlertDialog.Footer>
      </AlertDialog.Content>
    </AlertDialog.Root>
  </div>
  <div class="mt-8">
    {#if products.length > 0}
      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.Head>#</Table.Head>
            {#each keys as key}
              <Table.Head>{key_translation[key]}</Table.Head>
            {/each}
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {#each products as product, i}
            <Table.Row>
              <Table.Cell>{i + 1}</Table.Cell>
              {#each keys as key}
                {#if key === "description" || key === "keywords"}
                  <Table.Cell>
                    <Popover.Root>
                      <Popover.Trigger>
                        <Button class="h-auto w-full p-1 px-2 text-xs" variant="secondary">
                          Open
                        </Button>
                      </Popover.Trigger>
                      <Popover.Content class="w-3/4">
                        {#each product.data[key].split("\n") as line}
                          <p class="mt-2">{line}</p>
                        {/each}
                      </Popover.Content>
                    </Popover.Root>
                  </Table.Cell>
                {:else if typeof product.data[key] === "string" && (product.data[key].startsWith("http://") || product.data[key].startsWith("https://"))}
                  <Table.Cell>
                    <a href={product.data[key]} target="_blank" rel="noopener noreferrer">
                      <Button
                        class="flex h-auto items-center justify-center p-1 px-2 text-xs"
                        variant="secondary"
                      >
                        Open <ExternalLink class="ml-1 h-3 w-3" />
                      </Button>
                    </a>
                  </Table.Cell>
                {:else}
                  <Table.Cell>{product.data[key]}</Table.Cell>
                {/if}
              {/each}
            </Table.Row>
          {/each}
        </Table.Body>
      </Table.Root>
    {:else}
      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.Head>#</Table.Head>
            {#each keys as key}
              <Table.Head>{key_translation[key]}</Table.Head>
            {/each}
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {#each Array(20) as _}
            <Table.Row>
              <Table.Cell class="w-4">
                <Skeleton class="h-4 w-4" />
              </Table.Cell>
              {#each keys as key}
                <Table.Cell class="w-[{key.length}rem]">
                  <Skeleton class="h-4 w-[{key.length}rem]" />
                </Table.Cell>
              {/each}
            </Table.Row>
          {/each}
        </Table.Body>
      </Table.Root>
    {/if}
  </div>
</div>

<StatusTracker />
