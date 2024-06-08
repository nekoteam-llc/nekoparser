<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';
	import { cn } from '$lib/utils.js';

	type $$Props = HTMLAttributes<HTMLTableSectionElement>;

	let className: $$Props['class'];
	export { className as class };
</script>

<tfoot class={cn('bg-primary font-medium text-primary-foreground', className)} {...$$restProps}>
	<slot />
</tfoot>
