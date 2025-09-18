import { Title } from "#build/components";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2024-04-03",
  devtools: { enabled: true },
  ssr: true,
  modules: ["@pinia/nuxt", "vuetify-nuxt-module"],

  // Configure base URL for subdirectory deployment
  app: {
    baseURL: process.env.NUXT_APP_BASE_URL || '/',
    cdnURL: process.env.NUXT_APP_CDN_URL || undefined,
  },

  vuetify: {
    vuetifyOptions: "./vuetify.config.ts",
  },
});
