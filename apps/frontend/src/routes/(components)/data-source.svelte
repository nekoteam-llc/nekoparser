<script lang="ts">
  import { TriangleAlert } from "lucide-svelte"
  import { Badge } from "$lib/components/ui/badge"
  import { Progress } from "$lib/components/ui/progress"
  import * as Card from "$lib/components/ui/card"
  import * as Avatar from "$lib/components/ui/avatar"
  import { Separator } from "$lib/components/ui/separator"

  export let id: string
  export let icon: string
  export let title: string
  export let description: string
  export let state: string

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
</script>

<a href="/sources/{id}">
  <Card.Root class="flex flex-col space-y-4 shadow-sm shadow-transparent transition-shadow hover:shadow-purple-950">
    <Card.Header>
      <div class="flex items-center space-x-2">
        <Avatar.Root class="h-6 w-6">
          <Avatar.Image src={icon} alt={title} />
          <Avatar.Fallback>{title.substring(0, 2).toUpperCase()}</Avatar.Fallback>
        </Avatar.Root>
        <Card.Title>
          <h3 class="text-lg font-semibold">{title}</h3>
        </Card.Title>
      </div>
      <p class="text-muted-foreground">
        {description.substring(0, 100)}{description.length > 100 ? "..." : ""}
      </p>
    </Card.Header>
    <Card.Content class="flex items-center space-x-2 {state === "xpaths_pending" || state === "data_pending_approval" ? "pb-0" : ""}">
      <Badge variant={state === "unavailable" ? "destructive" : "default"} class={state === "finished" ? "bg-emerald-700 text-white" : ""}>
        {state.replaceAll("_", "\xA0")}
      </Badge>
      <Progress value={statusToProgress(state)} />
    </Card.Content>
    {#if state === "xpaths_pending" || state === "data_pending_approval"}
      <Card.Footer>
        <div class="w-full">
          <Separator />
          <div class="mt-4 flex items-center">
            <TriangleAlert class="mr-1 h-5 text-yellow-500" />
            <p class="text-yellow-500">User action is required. Open the source</p>
          </div>
        </div>
      </Card.Footer>
    {/if}
  </Card.Root>
</a>
