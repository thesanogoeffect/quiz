export default defineNuxtConfig({
  compatibilityDate: "2025-09-18",
  app: {
    baseURL: '/ipt/'
  },
  devtools: { enabled: true },
  ssr: true,
  modules: ["@pinia/nuxt", "vuetify-nuxt-module"],
  vuetify: {
    vuetifyOptions: "./vuetify.config.ts",
  },
});
