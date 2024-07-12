<script lang="ts">
  import { toast } from "svelte-sonner"
  import { onMount } from "svelte"
  import { Link2Off } from "lucide-svelte"

  let toastId: string | number | undefined
  let lastPong: number = Date.now()

  function fire() {
    if (toastId !== undefined)
      return

    if (lastPong < Date.now() - 5000) {
      toastId = toast.error("Lost API connection", {
        description: "Our API is taking a nap, data might be outdated!",
        duration: Number.POSITIVE_INFINITY,
        icon: Link2Off,
      })
    }

    setTimeout(fire, 1000)
  }

  setTimeout(fire, 1000)

  onMount(() => {
    const PROTOCOL = window.location.protocol === "https:" ? "wss" : "ws"
    const SOCKET_URL = `${PROTOCOL}://${window.location.host}/api/v1/ping/wss`
    function createSocket() {
      const socket = new WebSocket(SOCKET_URL)
      socket.onclose = () => {
        setTimeout(createSocket, 1000)
      }
      socket.onmessage = (event) => {
        if (event.data === "pong") {
          lastPong = Date.now()
          if (toastId !== undefined) {
            toast.dismiss(toastId)
            toastId = undefined
          }
        }
      }
      setInterval(() => {
        socket.send("ping")
      }, 1000)
    }

    createSocket()
  })
</script>
