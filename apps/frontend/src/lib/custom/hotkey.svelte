<script lang="ts">
  import { createEventDispatcher } from "svelte"

  const dispatch = createEventDispatcher()

  export let key: string = "cmd"
  export let value: boolean = false

  let displayKey = key
  if (key === "cmd") {
    displayKey = `<svg class="w-3 h-3" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4.90689 5.87349V8.12651H3.94741C2.8742 8.12651 2 8.96517 2 10.0455C2 11.1258 2.8742 12 3.94741 12C5.02061 12 5.89481 11.1258 5.89481 10.0455V9.09311H8.10519V10.0455C8.10519 11.1258 8.97939 12 10.0526 12C11.1258 12 12 11.1258 12 10.0455C12 8.96517 11.1258 8.12651 10.0526 8.12651H9.086V5.87349H10.0526C11.1258 5.87349 12 5.03483 12 3.95451C12 2.8742 11.1258 2 10.0526 2C8.97939 2 8.10519 2.8742 8.10519 3.95451V4.914H5.89481V3.95451C5.89481 2.8742 5.02061 2 3.94741 2C2.8742 2 2 2.8742 2 3.95451C2 5.03483 2.8742 5.87349 3.94741 5.87349H4.90689ZM3.95451 4.92111C3.42146 4.92111 2.98792 4.48756 2.98792 3.95451C2.98792 3.42146 3.42146 2.98792 3.94741 2.98792C4.47335 2.98792 4.90689 3.42146 4.90689 3.96162V4.92111H3.95451ZM10.0455 4.92111H9.086V3.96162C9.086 3.42146 9.52665 2.98792 10.0526 2.98792C10.5785 2.98792 11.0121 3.42146 11.0121 3.95451C11.0121 4.48756 10.5785 4.92111 10.0455 4.92111ZM5.89481 8.13362V5.86638H8.10519V8.13362H5.89481ZM3.95451 9.07178H4.90689V10.0384C4.90689 10.5714 4.47335 11.005 3.94741 11.005C3.42146 11.005 2.98792 10.5714 2.98792 10.0384C2.98792 9.50533 3.42146 9.07178 3.95451 9.07178ZM10.0455 9.07178C10.5785 9.07178 11.0121 9.50533 11.0121 10.0384C11.0121 10.5714 10.5785 11.005 10.0526 11.005C9.52665 11.005 9.086 10.5714 9.086 10.0384V9.07178H10.0455Z" fill="#111827" /></svg>`
  }
  else if (displayKey.length === 1) {
    displayKey = displayKey.toUpperCase()
  }
  else {
    displayKey = displayKey.charAt(0).toUpperCase() + displayKey.slice(1)
  }

  type KeyMap = {
    [key: string]: string
  }
  type KeyAliasesMap = {
    [key: string]: string[]
  }

  const KeyToHotKey: KeyMap = {
    "⌘": "Command",
    "cmd": "Command",
    "^": "Control",
    "meta": "Meta",

    "control": "Control",
    "ctrl": "Control",
    "alt": "Alt",

    "slash": "/",
  }

  const HotKeyAliases: KeyAliasesMap = {
    Command: ["Command", "Meta"],
  }

  $: hotKey = KeyToHotKey[key] || key
  $: hotKeyAliases = HotKeyAliases[hotKey] || []
  $: keysToCheck = [hotKey, ...hotKeyAliases]

  const layout: { [key: string]: string } = {
    "й": "q",
    "ц": "w",
    "у": "e",
    "к": "r",
    "е": "t",
    "н": "y",
    "г": "u",
    "ш": "i",
    "щ": "o",
    "з": "p",
    "х": "[",
    "Х": "{",
    "ъ": "]",
    "Ъ": "}",
    "/": "|",
    "ё": "`",
    "Ё": "~",
    "ф": "a",
    "ы": "s",
    "в": "d",
    "а": "f",
    "п": "g",
    "р": "h",
    "о": "j",
    "л": "k",
    "д": "l",
    "ж": ";",
    "Ж": ":",
    "э": "'",
    "Э": "\"",
    "я": "z",
    "ч": "x",
    "с": "c",
    "м": "v",
    "и": "b",
    "т": "n",
    "ь": "m",
    "б": ",",
    "Б": "<",
    "ю": ".",
    "Ю": ">",
    ".": "/",
    ",": "?",
    "\"": "@",
    "№": "#",
    ";": "$",
    ":": "^",
    "?": "&",
  }

  const isEventKeyHotKey = (event: KeyboardEvent) => {
    const altKey = event.altKey
    const ctrlKey = event.ctrlKey
    const metaKey = event.metaKey
    const shiftKey = event.shiftKey

    const eventKey = event.key
    let isHotKey = keysToCheck.includes(eventKey)
    if (
      eventKey.length === 1
      // eslint-disable-next-line regexp/no-obscure-range
      && /[а-яА-Я]/.test(eventKey)
      && layout[eventKey] !== undefined
      && !isHotKey
      && keysToCheck.includes(layout[eventKey])
    ) {
      isHotKey = true
    }

    if (!isHotKey)
      return false
    switch (hotKey) {
      case "Alt":
        return altKey || event.key === "Alt"
      case "Control":
        return ctrlKey || event.key === "Control"
      case "Meta":
        return metaKey || event.key === "Meta"
      case "Shift":
        return shiftKey || event.key === "Shift"
    }
    return isHotKey
  }

  const handleKeyPress = (event: KeyboardEvent) => {
    const isKeyDown = event.type === "keydown"
    const isKeyPressed = isEventKeyHotKey(event)
    if (isKeyPressed) {
      event.preventDefault()
      if (isKeyDown) {
        dispatch("hot", { key })
        value = true
      }
      else {
        dispatch("not", { key })
        value = false
      }
    }
  }

  const keydown = (event: KeyboardEvent) => {
    handleKeyPress(event)
  }
  const keyup = (event: KeyboardEvent) => {
    handleKeyPress(event)
  }
</script>

<svelte:window on:keydown={keydown} on:keyup={keyup} />

<kbd class="flex items-center px-1.5 py-0.5 text-xs font-semibold {$$props.class}">
  <!-- eslint-disable-next-line svelte/no-at-html-tags -->
  {@html displayKey}
</kbd>
