export default defineNuxtConfig({
  compatibilityDate: "2025-09-18",
  app: {
    // The site lives at https://quiz.jakubwerner.com/ipt/ , so the built output
    // must be deployed into an /ipt/ directory. See .github/workflows/deploy.yml.
    baseURL: "/ipt/",
    // Baked into the static shell. With ssr:false, useHead() only runs in the
    // browser, so anything left there is missing from the generated HTML -
    // which is what a crawler, a link preview or a browser tab reads first.
    head: {
      htmlAttrs: { lang: "en" },
      title: "Intro to P&T Quiz",
      meta: [
        {
          name: "description",
          content:
            "A student-made quiz app for the Intro to Psychology & Technology course at TU/e Eindhoven.",
        },
        { property: "og:title", content: "Intro to P&T Quiz" },
        {
          property: "og:description",
          content:
            "Practice questions for Intro to Psychology & Technology at TU/e Eindhoven.",
        },
        { property: "og:type", content: "website" },
        { property: "og:url", content: "https://quiz.jakubwerner.com/ipt/" },
      ],
      link: [{ rel: "icon", type: "image/x-icon", href: "/ipt/favicon.ico" }],
    },
  },
  devtools: { enabled: false },
  // The quiz is entirely client-driven: questions are fetched in onMounted and
  // every screen depends on browser state. Prerendering it produced a broken
  // first paint - Vuetify's component CSS is only injected once the entry chunk
  // runs, and useDisplay() sees width 0 during prerender, so the HTML was baked
  // with a mobile layout and both navigation drawers open. A plain SPA shell
  // loads the full stylesheet before first paint instead.
  ssr: false,
  modules: ["@pinia/nuxt", "vuetify-nuxt-module"],
  vuetify: {
    vuetifyOptions: "./vuetify.config.ts",
  },
});
