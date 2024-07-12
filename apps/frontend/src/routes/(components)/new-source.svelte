<script lang="ts">
  import { ListPlus, Table2 } from "lucide-svelte"
  import { defaults, superForm } from "sveltekit-superforms"
  import { zod, zodClient } from "sveltekit-superforms/adapters"
  import { Toaster, toast } from "svelte-sonner"
  import { formSchema } from "./new-source-schema"
  import {
    type CreateSourceApiV1SourcesPostResponse,
    SourcesAPI,
    type UploadExcelFileApiV1SourcesExcelPostResponse,
  } from "$client/index"
  import * as AlertDialog from "$lib/components/ui/alert-dialog/index.js"
  import { Button } from "$lib/components/ui/button/index.js"
  import HotKeys from "$lib/custom/hotkeys.svelte"
  import { Input } from "$lib/components/ui/input"
  import * as Form from "$lib/components/ui/form"

  const form = superForm(defaults(zod(formSchema)), {
    SPA: true,
    validators: zodClient(formSchema),
    onUpdate: ({ form: f }) => {
      if (!f.valid) {
        toast.error("Please fix the errors in the form.")
        return
      }
      if (f.data.xlsx) {
        const createSourceToastId = toast.loading(`Adding source...`)
        SourcesAPI.uploadExcelFile({ formData: { file: f.data.xlsx } }).then(
          (response: UploadExcelFileApiV1SourcesExcelPostResponse) => {
            // Wait for sources to be reloaded through ws
            setTimeout(() => {
              if (response.id) {
                toast.success("Source added successfully!", {
                  id: createSourceToastId,
                })
                closePopup()
              }
              else {
                toast.error("Failed to add source.", {
                  id: createSourceToastId,
                })
              }
            }, 100)
          },
        )
      }
      else if (f.data.url) {
        const url = f.data.url

        let domain: string
        try {
          domain = new URL(url).hostname
        }
        catch {
          toast.error("Invalid URL.")
          return
        }

        const createSourceToastId = toast.loading(`Adding source...`, { description: domain })
        SourcesAPI.createSource({ url }).then((response: CreateSourceApiV1SourcesPostResponse) => {
          // Wait for sources to be reloaded through ws
          setTimeout(() => {
            if (response.id) {
              toast.success("Source added successfully!", {
                description: domain,
                id: createSourceToastId,
              })
            }
            else {
              toast.error("Failed to add source.", {
                description: domain,
                id: createSourceToastId,
              })
            }
          }, 100)
        })
      }
    },
  })

  const { form: formData, enhance } = form

  let alertOpen = false

  function handleOpenHotkey() {
    alertOpen = true
  }

  function submitOnEnter(event: KeyboardEvent) {
    if (event.key === "Enter") {
      event.preventDefault()
      form.submit()
      closePopup()
    }
  }

  function closePopup() {
    alertOpen = false
  }

  function handleXlsxUpload(e: InputEvent) {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file)
      return
    $formData.xlsx = file
    form.submit()
  }
</script>

<AlertDialog.Root
  open={alertOpen}
  onOpenChange={(state) => {
    alertOpen = state
  }}
>
  <AlertDialog.Trigger asChild let:builder>
    <Button builders={[builder]} variant="default" class="my-2 pr-2">
      <ListPlus class="mr-1.5 h-4 w-4" />
      <div class="h-fit w-fit">Add new source</div>
      <HotKeys keys={["a"]} on:hot={handleOpenHotkey}></HotKeys>
    </Button>
  </AlertDialog.Trigger>
  <AlertDialog.Content>
    <form method="POST" use:enhance enctype="multipart/form-data">
      <AlertDialog.Header>
        <AlertDialog.Title>You are adding a new source</AlertDialog.Title>
        <Form.Field {form} name="url">
          <Form.Control let:attrs>
            <Form.Label>URL of the source</Form.Label>
            <Input {...attrs} bind:value={$formData.url} on:keydown={submitOnEnter} />
          </Form.Control>
          <Form.FieldErrors />
        </Form.Field>
      </AlertDialog.Header>
      <AlertDialog.Footer>
        <AlertDialog.Cancel class="pr-2">
          Cancel
          <HotKeys keys={["Esc"]} hook={false} dark={true} noprefix={true} />
        </AlertDialog.Cancel>
        <Form.Button class="pr-2">
          Add
          <HotKeys keys={["Enter"]} hook={false} noprefix={true} />
        </Form.Button>
      </AlertDialog.Footer>
      <div class="my-4 flex w-full items-center">
        <div class="h-[1px] w-full bg-border"></div>
        <div class="px-4 text-muted-foreground">or</div>
        <div class="h-[1px] w-full bg-border"></div>
      </div>
      <Form.Field {form} name="xlsx">
        <Form.Control let:attrs>
          <div class="flex w-full justify-center">
            <Form.Label
              class="flex w-fit cursor-pointer items-center gap-2 rounded-lg border border-border px-4 py-2 transition-all ease-in-out hover:bg-accent"
            >
              <Table2 class="h-6 w-6" />
              Upload .xlsx file
            </Form.Label>
          </div>
          <Input
            {...attrs}
            type="file"
            class="hidden"
            accept=".xlsx, .xls"
            on:input={handleXlsxUpload}
          />
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
    </form>
  </AlertDialog.Content>
</AlertDialog.Root>
<Toaster />
