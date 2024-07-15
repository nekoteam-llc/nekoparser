<script lang="ts">
  import { json2csv } from "json-2-csv"
  import {
    Braces,
    CircleSlash,
    ExternalLink,
    ListRestart,
    LoaderCircle,
    SquareDashedMousePointer,
    Table2,
    Table as TableIcon,
    Trash,
    X,
  } from "lucide-svelte"
  import { onMount } from "svelte"
  import { toast } from "svelte-sonner"
  import { dev } from "$app/environment"
  import {
    type ExcelSourceModel,
    type GetSourceApiV1SourcesSourceIdGetResponse,
    OpenAPI,
    SourcesAPI,
    type WebsiteSourceModel,
  } from "$client/index"
  import * as AlertDialog from "$lib/components/ui/alert-dialog/index.js"
  import * as Avatar from "$lib/components/ui/avatar"
  import Badge from "$lib/components/ui/badge/badge.svelte"
  import Button from "$lib/components/ui/button/button.svelte"
  import * as Popover from "$lib/components/ui/popover"
  import { Skeleton } from "$lib/components/ui/skeleton"
  import * as Table from "$lib/components/ui/table"
  import BackBtn from "$lib/custom/back-btn.svelte"
  import HotKeys from "$lib/custom/hotkeys.svelte"
  import StatusTracker from "$lib/custom/status-tracker.svelte"
  import { Checkbox } from "$lib/components/ui/checkbox"

  if (dev) {
    OpenAPI.BASE = "https://nekoparser-dev.dan.tatar"
  }

  export let data: { slug: string }

  let source: GetSourceApiV1SourcesSourceIdGetResponse | null = null
  let reprocessingToastId: number | string | undefined

  const openWebsite = () => {
    if (!source) {
      toast.loading("Loading source data...")
      // eslint-disable-next-line no-empty, no-unmodified-loop-condition
      while (!source) {}
    }
    if (!("url" in source)) {
      toast.error("Failed to open source.")
      return
    }
    toast.success("Good luck!")

    // Weird stuff happens if you leave the page immediately programmatically
    setTimeout(() => {
      window.open(source && "url" in source ? source?.url : "/", "_blank")
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

  let sources:
    | {
      excel_sources: ExcelSourceModel[]
      web_sources: WebsiteSourceModel[]
    }
    | undefined
    | null
  let checked: Record<string, boolean> = {}
  let products: {
    id: string
    product_hash: string
    data: any
    last_processed: string
    reprocessing: boolean
  }[] = []
  let maxReprocessing: number = 0

  onMount(() => {
    const PROTOCOL = window.location.protocol === "https:" ? "wss" : "ws"
    const SOCKET_URL = `${PROTOCOL}://${window.location.host}/api/v1/sources/wss`
    function createSocket() {
      const socket = new WebSocket(SOCKET_URL)
      socket.onmessage = (event) => {
        const eventData: {
          excel_sources: ExcelSourceModel[]
          web_sources: WebsiteSourceModel[]
        } = JSON.parse(event.data)
        if (JSON.stringify(eventData) !== JSON.stringify(sources)) {
          if (eventData === undefined || eventData === null) {
            sources = null
            return
          }
          sources = eventData
          const possibleSource
            = eventData.web_sources.find(source => source.id === data.slug)
              || eventData.excel_sources.find(source => source.id === data.slug)
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
        products.forEach((product) => {
          if (product.id in checked) {
            return
          }
          checked[product.id] = false
        })
        const currentlyReprocessing = products.filter(product => product.reprocessing).length
        if (currentlyReprocessing > maxReprocessing) {
          maxReprocessing = currentlyReprocessing
        }

        if (currentlyReprocessing === 0 && maxReprocessing > 0) {
          toast.success(
            `Reprocessed ${maxReprocessing} product${maxReprocessing > 1 ? "s" : ""}!`,
            {
              id: reprocessingToastId,
            },
          )
          maxReprocessing = 0
        }
      }
      socket.onclose = () => {
        setTimeout(createDataSocket, 1000)
      }
    }

    createDataSocket()
  })

  function handleDownloadCSV() {
    let max_i = 0
    products.forEach((product) => {
      if (Object.keys(product.data).length + 1 > max_i) {
        max_i = Object.keys(product.data).length + 1
      }
    })
    const csv = json2csv(
      products.map((product) => {
        const properties: Record<string, unknown> = {}
        let current_i = 0
        if (product.data.properties !== "N/A") {
          Object.entries(product.data.properties).forEach(([key, value]) => {
            if (key === undefined || value === undefined) {
              key = ""
              value = ""
            }
            if (current_i === 0) {
              properties["Название_Характеристики"] = key
              properties["Измерение_Характеристики"] = ""
              properties["Значение_Характеристики"] = value
              current_i++
              return
            }
            properties[`Название_Характеристики__${current_i}`] = key
            properties[`Измерение_Характеристики__${current_i}`] = ""
            properties[`Значение_Характеристики__${current_i}`] = value
            current_i++
          })
        }
        for (let i = current_i === 0 ? 1 : current_i; i < max_i; i++) {
          properties[`Название_Характеристики__${i}`] = ""
          properties[`Измерение_Характеристики__${i}`] = ""
          properties[`Значение_Характеристики__${i}`] = ""
        }
        return {
          Код_товара: product.data.sku,
          Название_позиции: product.data.name,
          Поисковые_запросы: product.data.keywords,
          Описание: product.data.description,
          Цена: product.data.price,
          Валюта: product.data.currency,
          Единица_измерения: product.data.measure_unit,
          Ссылка_изображения: product.data.main_image,
          ...properties,
        }
      }),
    )
    const blob = new Blob([csv], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    const sourceUrl = source && "url" in source ? source.url : "https://unknown-source.tld"
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
    const sourceUrl = source && "url" in source ? source.url : "https://unknown-source.tld"
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
    "properties",
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
    properties: "Properties",
    price: "Price",
    currency: "Currency",
    measure_unit: "Measure unit",
  }

  let toReprocess: string[] = []

  function handleChange() {
    toReprocess = Object.entries(checked)
      .filter(([_, value]) => value)
      .map(([key, _]) => key)
  }

  setInterval(() => {
    handleChange()
  }, 300)

  function startReprocess() {
    if (toReprocess.length === 0) {
      return
    }
    SourcesAPI.reprocessProducts({ requestBody: { products: toReprocess } })
      .then(() => {
        reprocessingToastId = toast.loading(
          `Reprocessing ${toReprocess.length} product${toReprocess.length > 1 ? "s" : ""}!`,
          {
            duration: Number.POSITIVE_INFINITY,
          },
        )
        checked = {}
        toReprocess = []
      })
      .catch((_) => {
        toast.error("Failed to start reprocessing.")
      })
  }

  function handleTitleChange(event: Event) {
    const target = event.target as HTMLElement
    if (
      source
      && ("icon" in source
        ? source.title !== target.textContent
        : source.filename !== target.textContent)
    ) {
      SourcesAPI.updateSource({
        sourceId: source.id,
        requestBody: { name: target.textContent, description: null },
      })
        .then(() => {
          toast.success("Updated source title!")
        })
        .catch(() => {
          toast.error("Failed to update source title.")
        })
    }
  }

  function handleDescriptionChange(event: Event) {
    const target = event.target as HTMLElement
    if (source) {
      SourcesAPI.updateSource({
        sourceId: source.id,
        requestBody: { name: null, description: target.textContent },
      })
        .then(() => {
          toast.success("Updated source description!")
        })
        .catch(() => {
          toast.error("Failed to update source description.")
        })
    }
  }
</script>

<div class="p-8">
  {#if !source}
    <div class="flex items-center">
      <Skeleton class="h-h-8 w-8 rounded-full" />
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
      {#if "icon" in source}
        <Avatar.Root class="h-8 w-8">
          <Avatar.Image src={source.icon} alt={source.title} />
          <Avatar.Fallback>{source.title.substring(0, 2).toUpperCase()}</Avatar.Fallback>
        </Avatar.Root>
      {:else}
        <Table2 class="h-8 w-8" />
      {/if}
      <h2
        class="ml-1 rounded-md border border-transparent p-1 text-2xl font-semibold tracking-tight outline-none transition-all ease-in-out focus:border-border"
        contenteditable
        on:blur={handleTitleChange}
      >
        {"title" in source ? source.title : source.filename}
      </h2>
      <Badge class="ml-3">
        {source.state.replaceAll("_", "\xA0")}
      </Badge>
    </div>
    {#if "description" in source}
      <p
        class="ml-10 mt-2 w-1/3 rounded-md border border-transparent p-1 text-muted-foreground outline-none transition-all ease-in-out focus:border-border"
        contenteditable
        on:blur={handleDescriptionChange}
      >
        {source.description}
      </p>
    {/if}
  {/if}
  <div class="mt-6 flex gap-4">
    <BackBtn class="m-0" />
    {#if source?.state === "xpaths_pending"}
      <Button on:click={openWebsite} class="m-0 pr-2">
        <SquareDashedMousePointer class="mr-1.5 h-4 w-4" />
        Continue setup
        <HotKeys keys={["o"]} on:hot={openWebsite} />
      </Button>
    {/if}
    <Button class="m-0 pr-2" on:click={handleDownloadCSV} disabled={products.length === 0}>
      {#if !source || ["data_collecting", "data_pending_approval", "finished"].find(state => state === source?.state) !== undefined}
        {#if products.length === 0}
          <LoaderCircle class="mr-1.5 h-4 w-4 animate-spin" />
        {:else}
          <TableIcon class="mr-1.5 h-4 w-4" />
        {/if}
        Download CSV
        <HotKeys keys={["c"]} on:hot={handleDownloadCSV} condition={products.length > 0} />
      {:else}
        <CircleSlash class="mr-1.5 h-4 w-4" />
        Download CSV
        <div class="w-2"></div>
      {/if}
    </Button>
    <Button class="m-0 pr-2" on:click={handleDownloadJSON} disabled={products.length === 0}>
      {#if !source || ["data_collecting", "data_pending_approval", "finished"].find(state => state === source?.state) !== undefined}
        {#if products.length === 0}
          <LoaderCircle class="mr-1.5 h-4 w-4 animate-spin" />
        {:else}
          <Braces class="mr-1.5 h-4 w-4" />
        {/if}
        Download JSON
        <HotKeys keys={["j"]} on:hot={handleDownloadJSON} condition={products.length > 0} />
      {:else}
        <CircleSlash class="mr-1.5 h-4 w-4" />
        Download JSON
        <div class="w-2"></div>
      {/if}
    </Button>
    {#if toReprocess.length > 0}
      <Button class="m-0 pr-2" on:click={startReprocess}>
        <ListRestart class="mr-1.5 h-4 w-4" />
        Reprocess {toReprocess.length} product{toReprocess.length > 1 ? "s" : ""}
        <HotKeys keys={["r"]} on:hot={startReprocess} />
      </Button>
    {/if}
    <AlertDialog.Root
      open={alertOpen}
      onOpenChange={(state) => {
        alertOpen = state
      }}
    >
      <AlertDialog.Trigger asChild let:builder>
        <Button builders={[builder]} variant="destructive" class="pr-2">
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
          <AlertDialog.Cancel class="gap-1.5">
            <X class="h-4 w-4" />
            <div class="h-fit w-fit">Cancel</div>
          </AlertDialog.Cancel>
          <AlertDialog.Action asChild let:builder>
            <Button
              builders={[builder]}
              on:click={deleteSource}
              on:keydown={handleKeydownSubmit}
              variant="destructive"
              class="gap-1.5"
            >
              <Trash class="h-4 w-4" />
              <div class="h-fit w-fit">Delete</div>
            </Button>
          </AlertDialog.Action>
        </AlertDialog.Footer>
      </AlertDialog.Content>
    </AlertDialog.Root>
  </div>
  <div class="mt-8">
    {#if !source || ["processing", "data_collecting", "data_pending_approval", "finished"].find(state => state === source?.state) !== undefined}
      {#if products.length > 0}
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.Head></Table.Head>
              <Table.Head>#</Table.Head>
              {#each keys as key}
                <Table.Head>{key_translation[key].replace(" ", "\xA0")}</Table.Head>
              {/each}
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {#each products as product, i}
              {#if product.data.name}
                <Table.Row class={product.reprocessing ? "opacity-65 hover:!bg-transparent" : ""}>
                  <Table.Cell>
                    {#if product.reprocessing}
                      <LoaderCircle class="h-4 w-4 animate-spin" />
                    {:else}
                      <Checkbox bind:checked={checked[product.id]} />
                    {/if}
                  </Table.Cell>
                  <Table.Cell>{i + 1}</Table.Cell>
                  {#each keys as key}
                    {#if key === "url" && source?.type === "excel"}
                      <Table.Cell>
                        <a href={source?.url} target="_blank" rel="noopener noreferrer">
                          <Button
                            class="flex h-auto items-center justify-center p-1 px-2 text-xs"
                            variant="secondary"
                          >
                            Download <ExternalLink class="ml-1 h-3 w-3" />
                          </Button>
                        </a>
                      </Table.Cell>
                    {:else if product.data[key] === undefined}
                      <Table.Cell>
                        {#if product.reprocessing}
                          <LoaderCircle class="h-4 w-4 animate-spin" />
                        {:else}
                          N/A
                        {/if}
                      </Table.Cell>
                    {:else if key === "description" || key === "keywords" || key === "properties"}
                      <Table.Cell>
                        {#if product.data[key] !== "N/A"}
                          <Popover.Root>
                            <Popover.Trigger>
                              <Button class="h-auto w-full p-1 px-2 text-xs" variant="secondary"
                              >Open</Button
                              >
                            </Popover.Trigger>
                            <Popover.Content class="max-w-1/2">
                              {#if key === "properties"}
                                {#if Object.keys(product.data[key]).length > 0}
                                  <Table.Root class="w-fit">
                                    <Table.Body>
                                      {#each Object.keys(product.data[key]) as property}
                                        <Table.Row>
                                          <Table.Cell>{property}</Table.Cell>
                                          <Table.Cell>{product.data[key][property]}</Table.Cell>
                                        </Table.Row>
                                      {/each}
                                    </Table.Body>
                                  </Table.Root>
                                {:else}
                                  <p class="text-center">No properties found</p>
                                {/if}
                              {:else}
                                {#each product.data[key].split("\n") as line}
                                  <p class="mt-2">{line}</p>
                                {/each}
                              {/if}
                            </Popover.Content>
                          </Popover.Root>
                        {:else}
                          <p class="mt-2">N/A</p>
                        {/if}
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
              {/if}
            {/each}
          </Table.Body>
        </Table.Root>
      {:else}
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.Head></Table.Head>
              <Table.Head>#</Table.Head>
              {#each keys as key}
                <Table.Head>{key_translation[key]}</Table.Head>
              {/each}
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {#each Array(10) as _}
              <Table.Row>
                <Table.Cell class="w-4">
                  <Skeleton class="h-4 w-4" />
                </Table.Cell>
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
    {:else}
      <div class="flex items-center justify-center">
        <p class="text-muted-foreground">No data available (yet)</p>
      </div>
    {/if}
  </div>
</div>

<StatusTracker />
