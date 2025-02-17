<script lang="ts">
  import { Table2 } from "lucide-svelte"
  import { Badge } from "$lib/components/ui/badge"
  import { Progress } from "$lib/components/ui/progress"
  import * as Card from "$lib/components/ui/card"
  import * as Avatar from "$lib/components/ui/avatar"

  export let id: string
  export let title: string
  export let state: string
  export let icon: string | null = null
  export let description: string | null = null

  function statusToProgress(status: string) {
    const consequtiveStatuses = [
      "created",
      "scraped",
      "xpaths_pending",
      "xpaths_ready",
      "preliminary_data_collecting",
      "preliminary_data_pending_approval",
      "preliminary_data_approved",
      "data_collecting",
      "data_pending_approval",
      "finished",
    ]
    if (consequtiveStatuses.includes(status)) {
      return ((consequtiveStatuses.indexOf(status) + 1) / consequtiveStatuses.length) * 100
    }
    return 0
  }

  const actionRequired = state === "xpaths_pending" || state === "data_pending_approval"
</script>

<a href="/sources/{id}" class="mb-4 mr-4 block break-inside-avoid">
  <Card.Root
    class="{description === null
      ? "max-h-[117px]"
      : "max-h-[250px]"} flex flex-col justify-between space-y-4 border-opacity-50 shadow-sm shadow-transparent transition-all ease-in-out hover:-translate-y-1 hover:shadow-purple-950 {actionRequired
      ? "!shadow-orange-900"
      : ""}"
  >
    <Card.Header class="pb-0">
      <div class="flex items-center space-x-2">
        {#if icon}
          <Avatar.Root class="h-6 w-6">
            <Avatar.Image src={icon} alt={title} />
            <Avatar.Fallback>{title.substring(0, 2).toUpperCase()}</Avatar.Fallback>
          </Avatar.Root>
        {:else}
          <Table2 class="h-6 w-6" />
        {/if}
        <Card.Title>
          <h3 class="text-lg font-semibold">{title}</h3>
        </Card.Title>
      </div>
      {#if description}
        <p class="h-16 w-full overflow-hidden text-ellipsis text-sm text-muted-foreground">
          {description}
        </p>
      {/if}
    </Card.Header>
    <Card.Content class="flex items-center space-x-2">
      <Badge
        variant={state === "unavailable" ? "destructive" : "default"}
        class={state === "finished"
          ? "bg-emerald-700 text-white hover:bg-emerald-700/90"
          : actionRequired
          ? "bg-orange-600 text-white hover:bg-orange-600/90"
          : ""}
      >
        {state.replaceAll("_", "\xA0")}
      </Badge>
      <Progress value={statusToProgress(state)} />
    </Card.Content>
  </Card.Root>
</a>
