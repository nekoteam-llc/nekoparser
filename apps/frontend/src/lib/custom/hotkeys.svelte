<script lang="ts">
  import { createEventDispatcher } from "svelte"
  import HotKey from "./hotkey.svelte"
  import { getPlatformPrefix } from "$lib/utils"

  const dispatch = createEventDispatcher()

  export let keys: string[] = ["cmd", "k"]
  export let value: boolean = false
  export let hook: boolean = true
  export let dark: boolean = false
  export let condition: boolean = true
  export let noprefix: boolean = false

  type KeyPressedMap = {
    [key: string]: boolean
  }
  let HotKeyPressedMap: KeyPressedMap = {}
  let KeyPressedMapCount = 0

  const reset = () => {
    HotKeyPressedMap = {}
    KeyPressedMapCount = 0
  }

  const isComboPressed = () => {
    const correctNumberOfKeys = KeyPressedMapCount === keys.length
    const allKeysPressed = keys.every(pressed => HotKeyPressedMap[pressed] === true)
    return correctNumberOfKeys && allKeysPressed
  }

  const hot = (key: string) => {
    HotKeyPressedMap[key] = true
    KeyPressedMapCount++
    KeyPressedMapCount = Math.min(keys.length, KeyPressedMapCount)

    const readyToFire = isComboPressed()
    if (readyToFire) {
      dispatch("hot", key)
      value = true
    }
  }

  const not = (key: string) => {
    HotKeyPressedMap[key] = false
    KeyPressedMapCount--
    KeyPressedMapCount = Math.max(0, KeyPressedMapCount)
    dispatch("not", key)
    value = false
    reset()
  }

  let skeleton = true

  if (!noprefix) {
    getPlatformPrefix().then((platformPrefix) => {
      if (!keys.includes(platformPrefix))
        keys.unshift(platformPrefix)
      skeleton = false
    })
  }
  else {
    skeleton = false
  }
</script>

{#if skeleton || !condition}
  <div
    class="flex h-5 w-10 animate-pulse items-center justify-center gap-1 rounded-sm border {dark
      ? "border bg-zinc-900 text-gray-200"
      : "border-gray-400 bg-zinc-100 text-gray-800"} ml-2 {$$props.class}"
  >
    {#each Array.from({ length: 3 }) as _, i}
      <div
        class="h-1 w-1 rounded-full {dark
          ? "bg-slate-gray-600"
          : "bg-zinc-700"} ease animate-bounce"
        style="animation-delay: {i * 0.1}s; animation-duration: 900ms;"
      ></div>
    {/each}
  </div>
{:else}
  <div
    class="inline-flex {$$props.class} transfrom ml-2 scale-90 {dark
      ? "border bg-zinc-900 text-gray-300"
      : "border-gray-400 bg-zinc-100 text-gray-800"} shadow-outer rounded-sm border font-['Inter'] {$$props.class}"
  >
    {#each keys as key, i}
      {#if hook}
        <HotKey
          {key}
          on:hot={() => hot(key)}
          on:not={() => not(key)}
          class="{i > 0 ? "pl-1" : ""} {i < keys.length - 1
            ? "rounded-br-none rounded-tr-none border-r-0 pr-0"
            : "rounded-bl-none rounded-tl-none border-l-0"}"
        >
          {key}
        </HotKey>
      {:else}
        <HotKey
          {key}
          class="{i > 0 ? "pl-1" : ""} {i < keys.length - 1
            ? "rounded-br-none rounded-tr-none border-r-0 pr-0"
            : "rounded-bl-none rounded-tl-none border-l-0"}"
        >
          {key}
        </HotKey>
      {/if}
    {/each}
  </div>
{/if}
