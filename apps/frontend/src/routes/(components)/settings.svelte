<script lang="ts">
  import { BicepsFlexed, Coins, LoaderCircle, Rocket, Save, Settings } from "lucide-svelte"
  import { toast } from "svelte-sonner"
  import { ConfigAPI, type ConfigModel } from "$client/index"
  import Input from "$lib/components/ui/input/input.svelte"
  import * as Select from "$lib/components/ui/select"
  import * as Dialog from "$lib/components/ui/dialog"
  import { Textarea } from "$lib/components/ui/textarea"
  import Button from "$lib/components/ui/button/button.svelte"
  import HotKeys from "$lib/custom/hotkeys.svelte"

  let settingsLoading = false
  let settingsOpen = false
  let currentSettings: ConfigModel | undefined
  let currentModel: string | undefined

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
    currentSettings.chatgpt_key = (
      document.getElementById("chatgpt-key") as HTMLInputElement
    ).value
    currentSettings.pages_concurrency = Number.parseInt(
      (document.getElementById("pages") as HTMLInputElement).value,
    )
    currentSettings.products_concurrency = Number.parseInt(
      (document.getElementById("products") as HTMLInputElement).value,
    )
    currentSettings.required = (document.getElementById("required") as HTMLInputElement).value
      .split(",")
      .map(field => field.trim())
    currentSettings.not_reprocess = (
      document.getElementById("not-reprocess") as HTMLInputElement
    ).value
      .split(",")
      .map(field => field.trim())
    currentSettings.description_prompt = (
      document.getElementById("prompt-description") as HTMLTextAreaElement
    ).value
    currentSettings.keywords_prompt = (
      document.getElementById("prompt-keywords") as HTMLTextAreaElement
    ).value
    currentSettings.properties_prompt = (
      document.getElementById("prompt-properties") as HTMLTextAreaElement
    ).value

    settingsLoading = true

    return new Promise((resolve) => {
      // @ts-ignore
      currentSettings.model = currentModel ?? currentSettings.model
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

  function openOrSave() {
    if (settingsOpen) {
      saveSettings()
    }
    else {
      settingsOpen = true
    }
  }
</script>

<Dialog.Root
  open={settingsOpen}
  onOpenChange={(state) => {
    settingsOpen = state
  }}
>
  <Dialog.Trigger asChild let:builder>
    <Button
      variant="outline"
      class="ease absolute right-0 top-0 m-3 hidden cursor-pointer items-center gap-1.5 pr-2 text-primary md:flex"
      builders={[builder]}
    >
      <Settings class="h-5 w-5" />
      <div class="h-fit w-fit">Settings</div>
      <HotKeys keys={["s"]} dark={true} on:hot={openOrSave} class="!m-0"></HotKeys>
    </Button>
  </Dialog.Trigger>
  <Dialog.Content class="w-fit max-w-[900px]">
    <Dialog.Header>
      <Dialog.Title>Parser configuration</Dialog.Title>
    </Dialog.Header>
    <div class="flex w-fit gap-2">
      <div class="flex w-[400px] flex-col gap-2 p-2">
        <span class="text-sm font-normal text-muted-foreground">ChatGPT key</span>
        <Input
          class="w-full"
          id="chatgpt-key"
          type="password"
          disabled={settingsLoading}
          value={currentSettings?.chatgpt_key}
        />

        <span class="text-sm font-normal text-muted-foreground">Model</span>
        <Select.Root
          selected={currentSettings ? { value: currentSettings.model } : undefined}
          onSelectedChange={(v) => {
            currentModel = v?.value ?? "gpt-4o-mini"
          }}
        >
          <Select.Trigger class="w-full">
            <Select.Value
              placeholder={currentSettings
                ? {
                  "gpt-4o-mini": "GPT 4o Mini",
                  "gpt-3.5-turbo-1106": "GPT 3.5 Turbo 1106",
                  "gpt-4o": "GPT 4o",
                  "gpt-4-1106-preview": "GPT 4 Turbo 1106",
                }[currentSettings.model]
                : "Select model"}
            />
          </Select.Trigger>
          <Select.Content class="bg-zinc-900">
            <Select.Item
              value="gpt-4o-mini"
              class="block border border-border transition-colors ease-in-out"
            >
              <div class="flex items-center gap-2">
                <Coins class="h-4 w-4" />
                GPT 4o Mini
              </div>
              <p class="text-sm text-gray-400">Cheapest and fastest model, good for most tasks</p>
            </Select.Item>
            <Select.Item
              value="gpt-3.5-turbo-1106"
              class="block border border-border transition-colors ease-in-out"
            >
              <div class="flex items-center gap-2">
                <Coins class="h-4 w-4" />
                GPT 3.5 Turbo 1106
              </div>
              <p class="text-sm text-gray-400">Cheap and fast model, yet outdated</p>
            </Select.Item>
            <Select.Item
              value="gpt-4o"
              class="mt-1 block border border-border transition-colors ease-in-out"
            >
              <div class="flex items-center gap-2">
                <Rocket class="h-4 w-4" />
                GPT 4o
              </div>
              <p class="text-sm text-gray-400">Balance between price and quality</p>
            </Select.Item>
            <Select.Item
              value="gpt-4-1106-preview"
              class="mt-1 block border border-border transition-colors ease-in-out"
            >
              <div class="flex items-center gap-2">
                <BicepsFlexed class="h-4 w-4" />
                GPT 4 Turbo 1106
              </div>
              <p class="text-sm text-gray-400">Most powerful model, best quality, but pricy</p>
            </Select.Item>
          </Select.Content>
        </Select.Root>
        <span class="text-sm font-normal text-muted-foreground">
          Number of pages processed simultaneously
        </span>
        <Input
          class="w-full"
          id="pages"
          disabled={settingsLoading}
          value={currentSettings?.pages_concurrency}
        />
        <span class="text-sm font-normal text-muted-foreground">
          Number of products processed simultaneously
        </span>
        <Input
          class="w-full"
          id="products"
          disabled={settingsLoading}
          value={currentSettings?.products_concurrency}
        />
        <span class="text-sm font-normal text-muted-foreground">
          Required fields, comma-separated
        </span>
        <Input
          class="w-full"
          id="required"
          disabled={settingsLoading}
          value={currentSettings?.required.join(", ")}
        />
        <span class="text-sm font-normal text-muted-foreground">
          Fields that we do not reprocess, comma-separated
        </span>
        <Input
          class="w-full"
          id="not-reprocess"
          disabled={settingsLoading}
          value={currentSettings?.not_reprocess.join(", ")}
        />
      </div>
      <div class="flex w-[400px] flex-col gap-2 p-2">
        <span class="text-sm font-normal text-muted-foreground">
          Description normalization prompt
        </span>
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
    <div class="flex justify-end gap-4">
      <Dialog.Close asChild let:builder>
        <Button
          variant="outline"
          class="mt-4 flex items-center justify-between gap-1.5 pr-2"
          disabled={settingsLoading}
          builders={[builder]}
        >
          <div class="h-fit w-fit">Close</div>
          <HotKeys keys={["Esc"]} hook={false} dark={true} noprefix={true} class="!m-0" />
        </Button>
      </Dialog.Close>
      <Button
        class="mt-4 flex items-center justify-evenly gap-1.5 pr-2"
        on:click={saveSettings}
        disabled={settingsLoading}
      >
        {#if settingsLoading}
          <LoaderCircle class="h-4 w-4 animate-spin" />
        {:else}
          <Save class="h-4 w-4" />
        {/if}
        <div class="h-fit w-fit">Save</div>
        <HotKeys keys={["s"]} hook={false} dark={false} on:hot={openOrSave} class="!m-0"></HotKeys>
      </Button>
    </div>
  </Dialog.Content>
</Dialog.Root>
