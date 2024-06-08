import antfu from "@antfu/eslint-config"

export default antfu(
  {
    svelte: true,
    ignores: ["**/src/client/", "**/src/lib/components/", "**/.svelte-kit/"],
    stylistic: {
      indent: 2,
      quotes: "double",
    },
  },
  {
    rules: {
      "style/indent-binary-ops": "off",
    },
  },
)
