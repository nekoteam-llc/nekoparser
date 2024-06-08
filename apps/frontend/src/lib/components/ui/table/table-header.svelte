<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';
	import { cn } from '$lib/utils.js';

	type $$Props = HTMLAttributes<HTMLTableSectionElement>;

	let className: $$Props['class'];
	export { className as class };
</script>

<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<thead class={cn('sticky top-0 [&_tr]:border-b', className)} {...$$restProps} on:click on:keydown>
	<slot />
</thead>
