import { Title } from "#build/components";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-09-18",
  devtools: { enabled: true },
  ssr: true,
  modules: ["@pinia/nuxt", "vuetify-nuxt-module"],
  vuetify: {
    vuetifyOptions: "./vuetify.config.ts",
  },
});
