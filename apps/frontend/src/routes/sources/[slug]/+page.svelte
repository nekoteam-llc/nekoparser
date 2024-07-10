<script lang="ts">
  import { json2csv } from "json-2-csv"
  import {
    BicepsFlexed,
    Braces,
    Coins,
    ExternalLink,
    ListRestart,
    LoaderCircle,
    Rocket,
    Save,
    Settings,
    SquareDashedMousePointer,
    Table as TableIcon,
    Trash,
  } from "lucide-svelte"
  import { onMount } from "svelte"
  import { toast } from "svelte-sonner"
  import { dev } from "$app/environment"
  import { ConfigAPI, type ConfigModel, type GetSourceApiV1SourcesSourceIdGetResponse, OpenAPI, type Source, SourcesAPI } from "$client/index"
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
  import Input from "$lib/components/ui/input/input.svelte"
  import * as Select from "$lib/components/ui/select"
  import * as Dialog from "$lib/components/ui/dialog"
  import { Textarea } from "$lib/components/ui/textarea"
  import { Checkbox } from "$lib/components/ui/checkbox"

  if (dev) {
    OpenAPI.BASE = "https://nekoparser-dev.dan.tatar"
  }

  export let data: { slug: string }

  let source: GetSourceApiV1SourcesSourceIdGetResponse | null = null
  let settingsLoading = false
  let settingsOpen = false
  let currentSettings: ConfigModel | undefined
  let reprocessingToastId: number | string | undefined

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
          toast.success(`Reprocessed ${maxReprocessing} product${maxReprocessing > 1 ? "s" : ""}!`, {
            id: reprocessingToastId,
          })
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

  const keys: string[] = ["url", "main_image", "sku", "name", "description", "keywords", "properties", "price", "currency", "measure_unit"]
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

  ConfigAPI.get()
    .then((response) => {
      currentSettings = response
    })
    .catch((_) => {
      toast.error("Failed to fetch current settings.")
    })

  function saveSettings(): Promise<void> {
    if (currentSettings === undefined) {
      // eslint-disable-next-line no-unmodified-loop-condition, no-empty
      while (currentSettings === undefined) {}
    }
    currentSettings.chatgpt_key = (document.getElementById("chatgpt-key") as HTMLInputElement).value
    currentSettings.pages_concurrency = Number.parseInt((document.getElementById("pages") as HTMLInputElement).value)
    currentSettings.products_concurrency = Number.parseInt((document.getElementById("products") as HTMLInputElement).value)
    currentSettings.required = (document.getElementById("required") as HTMLInputElement).value.split(",").map(field => field.trim())
    currentSettings.not_reprocess = (document.getElementById("not-reprocess") as HTMLInputElement).value.split(",").map(field => field.trim())
    currentSettings.description_prompt = (document.getElementById("prompt-description") as HTMLTextAreaElement).value
    currentSettings.keywords_prompt = (document.getElementById("prompt-keywords") as HTMLTextAreaElement).value
    currentSettings.properties_prompt = (document.getElementById("prompt-properties") as HTMLTextAreaElement).value

    settingsLoading = true

    return new Promise((resolve) => {
      ConfigAPI.update({
        // @ts-ignore
        requestBody: currentSettings,
      })
        .then(() => {
          toast.success("Settings saved!")
          settingsLoading = false
          settingsOpen = false
          resolve()
        })
        .catch((_) => {
          toast.error("Failed to save settings.")
          settingsLoading = false
          resolve()
        })
    })
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
        reprocessingToastId = toast.loading(`Reprocessing ${toReprocess.length} product${toReprocess.length > 1 ? "s" : ""}!`, {
          duration: Number.POSITIVE_INFINITY,
        })
        checked = {}
        toReprocess = []
      })
      .catch((_) => {
        toast.error("Failed to start reprocessing.")
      })
  }
</script>

<Dialog.Root
  open={settingsOpen}
  onOpenChange={(state) => {
    settingsOpen = state
  }}
>
  <Dialog.Trigger asChild let:builder>
    <div
      class="ease absolute right-0 top-0 m-4 transform cursor-pointer text-primary transition-transform hover:rotate-90 hover:scale-105"
      use:builder.action
      {...builder}
    >
      <Settings class="h-7 w-7" />
    </div>
  </Dialog.Trigger>
  <Dialog.Content class="w-fit max-w-[900px]">
    <Dialog.Header>
      <Dialog.Title>Parser configuration</Dialog.Title>
    </Dialog.Header>
    <div class="flex w-fit gap-2">
      <div class="flex w-[400px] flex-col gap-2 p-2">
        <span class="text-sm font-normal text-muted-foreground">ChatGPT key</span>
        <Input class="w-full" id="chatgpt-key" type="password" disabled={settingsLoading} value={currentSettings?.chatgpt_key} />

        <span class="text-sm font-normal text-muted-foreground">Model</span>
        <Select.Root
          selected={currentSettings ? { value: currentSettings.model } : undefined}
          onSelectedChange={(v) => {
            if (currentSettings)
              currentSettings.model = v?.value ?? "gpt-3.5-turbo-1106"
          }}
        >
          <Select.Trigger class="w-full">
            <Select.Value
              placeholder={currentSettings
                ? { "gpt-3.5-turbo-1106": "GPT 3.5 Turbo 1106", "gpt-4o": "GPT 4o", "gpt-4-1106-preview": "GPT 4 Turbo 1106" }[currentSettings.model]
                : "Select model"}
            />
          </Select.Trigger>
          <Select.Content>
            <Select.Item value="gpt-3.5-turbo-1106" class="flex items-center gap-2">
              <Coins class="h-4 w-4" />
              GPT 3.5 Turbo 1106
            </Select.Item>
            <Select.Item value="gpt-4o" class="flex items-center gap-2">
              <Rocket class="h-4 w-4" />
              GPT 4o
            </Select.Item>
            <Select.Item value="gpt-4-1106-preview" class="flex items-center gap-2">
              <BicepsFlexed class="h-4 w-4" />
              GPT 4 Turbo 1106
            </Select.Item>
          </Select.Content>
        </Select.Root>
        <span class="text-sm font-normal text-muted-foreground">Number of pages processed simultaneously</span>
        <Input class="w-full" id="pages" disabled={settingsLoading} value={currentSettings?.pages_concurrency} />
        <span class="text-sm font-normal text-muted-foreground">Number of products processed simultaneously</span>
        <Input class="w-full" id="products" disabled={settingsLoading} value={currentSettings?.products_concurrency} />
        <span class="text-sm font-normal text-muted-foreground">Required fields, comma-separated</span>
        <Input class="w-full" id="required" disabled={settingsLoading} value={currentSettings?.required.join(", ")} />
        <span class="text-sm font-normal text-muted-foreground">Fields that we do not reprocess, comma-separated</span>
        <Input class="w-full" id="not-reprocess" disabled={settingsLoading} value={currentSettings?.not_reprocess.join(", ")} />
      </div>
      <div class="flex w-[400px] flex-col gap-2 p-2">
        <span class="text-sm font-normal text-muted-foreground">Description normalization prompt</span>
        <Textarea
          id="prompt-description"
          class="h-[100px] w-full"
          placeholder="Description normalization prompt"
          disabled={settingsLoading}
          value={currentSettings?.description_prompt}
        />
        <span class="text-sm font-normal text-muted-foreground">Keywords extraction prompt</span>
        <Textarea
          id="prompt-keywords"
          class="h-[100px] w-full"
          placeholder="Keywords extraction prompt"
          disabled={settingsLoading}
          value={currentSettings?.keywords_prompt}
        />
        <span class="text-sm font-normal text-muted-foreground">Properties extraction prompt</span>
        <Textarea
          id="prompt-properties"
          class="h-[100px] w-full"
          placeholder="Properties extraction prompt"
          disabled={settingsLoading}
          value={currentSettings?.properties_prompt}
        />
      </div>
    </div>
    <Button class="mt-4 flex items-center gap-2" on:click={saveSettings} disabled={settingsLoading}>
      {#if settingsLoading}
        <LoaderCircle class="h-4 w-4 animate-spin" />
      {:else}
        <Save class="h-4 w-4" />
      {/if}
      Save
    </Button>
  </Dialog.Content>
</Dialog.Root>

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
    {#if toReprocess.length > 0}
      <Button class="m-0" on:click={startReprocess}>
        <ListRestart class="mr-1.5 h-4 w-4" />
        Reprocess {toReprocess.length} product{toReprocess.length > 1 ? "s" : ""}
      </Button>
    {/if}
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
          <AlertDialog.Description>This action cannot be undone. All data from this source will be lost as well!</AlertDialog.Description>
        </AlertDialog.Header>
        <AlertDialog.Footer>
          <AlertDialog.Cancel>Cancel</AlertDialog.Cancel>
          <AlertDialog.Action asChild let:builder>
            <Button builders={[builder]} on:click={deleteSource} on:keydown={handleKeydownSubmit} variant="destructive">Delete</Button>
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
            <Table.Head></Table.Head>
            <Table.Head>#</Table.Head>
            {#each keys as key}
              <Table.Head>{key_translation[key]}</Table.Head>
            {/each}
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {#each products as product, i}
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
                {#if key === "description" || key === "keywords" || key === "properties"}
                  <Table.Cell>
                    {#if product.data[key] !== "N/A"}
                      <Popover.Root>
                        <Popover.Trigger>
                          <Button class="h-auto w-full p-1 px-2 text-xs" variant="secondary">Open</Button>
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
                      <Button class="flex h-auto items-center justify-center p-1 px-2 text-xs" variant="secondary">
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
            <Table.Head></Table.Head>
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
