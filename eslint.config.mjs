import js from "@eslint/js";
import globals from "globals";

export default [
  // 1. Global ignores (from former .eslintignore)
  {
    ignores: [
      "app/static/js/lib/",
      "app/static/js/vendor/",
      "dist/",
      "build/",
      "node_modules/",
      ".venv/",
      "app/templates/**/*.js"
    ]
  },

  // 2. Configuration for JavaScript files
  {
    files: ["**/*.{js,mjs,cjs}"], // Specify the files this config applies to

    // Start with ESLint's recommended JavaScript settings
    // This spreads recommended rules, languageOptions (like ecmaVersion, sourceType), etc.
    ...js.configs.recommended,

    // Customize languageOptions further, e.g., adding browser globals
    languageOptions: {
      // Preserve and merge with languageOptions from js.configs.recommended
      ...(js.configs.recommended.languageOptions || {}),
      globals: {
        // Preserve and merge globals from js.configs.recommended (e.g., es2021 globals)
        ...(js.configs.recommended.languageOptions?.globals || {}),
        // Add browser-specific globals
        ...globals.browser,
      }
    },

    // Add or override specific rules
    rules: {
      // Preserve and merge rules from js.configs.recommended so you can override them
      ...(js.configs.recommended.rules || {}),
      // Add any custom rules or overrides here, for example:
      // "no-console": "warn",
    }
  }
  // You can add other configuration objects here if needed for other plugins or file types
];
