// vuetify.config.ts
import { defineVuetifyConfiguration } from "vuetify-nuxt-module/custom-configuration";

export default defineVuetifyConfiguration({
  theme: {
    defaultTheme: "light",
    themes: {
      light: {
        colors: {
          primary: "#C81919",
          background: "#C81919",
          surface: "#fae4d4",
        },
      },
      dark: {
        colors: {
          primary: "#C81919",
          background: "#C81919",
          surface: "#121212",
        },
      },
    },
  },
});
