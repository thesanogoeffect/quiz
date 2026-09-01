// vuetify.config.ts
import { defineVuetifyConfiguration } from "vuetify-nuxt-module/custom-configuration";

export default defineVuetifyConfiguration({
  theme: {
    defaultTheme: "light",
    themes: {
      light: {
        dark: false,
        colors: {
          primary: "#C81919",
          // `background` is the app canvas, not an accent. It used to be the
          // same red as `primary`, which showed through as red bands wherever a
          // surface did not cover the viewport.
          background: "#fae4d4",
          surface: "#fae4d4",
          error: "#C62828",
          success: "#2E7D32",
          warning: "#EF6C00",
          info: "#0277BD",
        },
      },
      dark: {
        dark: true,
        colors: {
          primary: "#C81919",
          background: "#121212",
          surface: "#1E1E1E",
          error: "#EF5350",
          success: "#66BB6A",
          warning: "#FFA726",
          info: "#4FC3F7",
        },
      },
    },
  },
});
