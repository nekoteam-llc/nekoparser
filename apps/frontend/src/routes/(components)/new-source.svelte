<script lang="ts">
  import { CirclePlus } from "lucide-svelte"
  import { type Infer, type SuperValidated, superForm } from "sveltekit-superforms"
  import { zodClient } from "sveltekit-superforms/adapters"
  import { Toaster, toast } from "svelte-sonner"
  import { type FormSchema, formSchema } from "./new-source-schema"
  import { type CreateSourceApiV1SourcesPostResponse, SourcesAPI } from "$client/index"
  import * as AlertDialog from "$lib/components/ui/alert-dialog/index.js"
  import { Button } from "$lib/components/ui/button/index.js"
  import HotKeys from "$lib/custom/hotkeys.svelte"
  import { Input } from "$lib/components/ui/input"
  import * as Form from "$lib/components/ui/form"

  export let data: SuperValidated<Infer<FormSchema>>

  const form = superForm(data, {
    validators: zodClient(formSchema),
    onUpdated: ({ form: f }) => {
      if (f.valid) {
        const url = f.data.url
        let domain: string
        try {
          domain = new URL(url).hostname
        }
        catch (error) {
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
      else {
        toast.error("Please fix the errors in the form.")
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
</script>

<AlertDialog.Root
  open={alertOpen}
  onOpenChange={(state) => {
    alertOpen = state
  }}
>
  <AlertDialog.Trigger asChild let:builder>
    <Button builders={[builder]} variant="default" class="my-2">
      <CirclePlus class="mr-1.5 h-4 w-4" />
      Add new source
      <HotKeys keys={["a"]} on:hot={handleOpenHotkey}></HotKeys>
    </Button>
  </AlertDialog.Trigger>
  <AlertDialog.Content>
    <form method="POST" use:enhance on:submit={closePopup}>
      <AlertDialog.Header>
        <AlertDialog.Title>You are adding a new source</AlertDialog.Title>
        <Form.Field {form} name="url">
          <Form.Control let:attrs>
            <Form.Label>URL</Form.Label>
            <Input {...attrs} bind:value={$formData.url} on:keydown={submitOnEnter} />
          </Form.Control>
          <Form.Description>URL of the source to add</Form.Description>
          <Form.FieldErrors />
        </Form.Field>
      </AlertDialog.Header>
      <AlertDialog.Footer>
        <AlertDialog.Cancel>
          Cancel
          <HotKeys keys={["Esc"]} hook={false} dark={true} noprefix={true} />
        </AlertDialog.Cancel>
        <Form.Button>
          Add
          <HotKeys keys={["Enter"]} hook={false} noprefix={true} />
        </Form.Button>
      </AlertDialog.Footer>
    </form>
  </AlertDialog.Content>
</AlertDialog.Root>
<Toaster />
