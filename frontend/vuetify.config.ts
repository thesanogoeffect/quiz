// vuetify.config.ts
import { defineVuetifyConfiguration } from "vuetify-nuxt-module/custom-configuration";

export default defineVuetifyConfiguration({
  // Icons are SVG paths from @mdi/js, not the @mdi/font webfont. The font was
  // 395 kB of woff2 plus 300 kB of CSS for 7,447 icon classes, of which this
  // app uses thirty; every visitor downloaded the lot before the first icon
  // could be painted. Listing them here makes the module import just these
  // paths from @mdi/js and register them as `$alias`, so templates say
  // `icon="$account"` instead of `icon="mdi-account"`.
  //
  // Adding an icon to a template means adding it here too - an unregistered
  // `$name` renders as nothing at all.
  icons: {
    defaultSet: "mdi-svg",
    svg: {
      mdi: {
        aliases: {
          account: "mdiAccount",
          arrowDownBold: "mdiArrowDownBold",
          arrowDownBoldOutline: "mdiArrowDownBoldOutline",
          arrowLeft: "mdiArrowLeft",
          arrowRight: "mdiArrowRight",
          arrowUpBold: "mdiArrowUpBold",
          arrowUpBoldOutline: "mdiArrowUpBoldOutline",
          book: "mdiBook",
          bookOpenPageVariant: "mdiBookOpenPageVariant",
          chartBar: "mdiChartBar",
          chartBellCurve: "mdiChartBellCurve",
          checkboxMarkedCircleOutline: "mdiCheckboxMarkedCircleOutline",
          checkCircle: "mdiCheckCircle",
          checkCircleOutline: "mdiCheckCircleOutline",
          closeCircle: "mdiCloseCircle",
          cloudAlert: "mdiCloudAlert",
          dotsVertical: "mdiDotsVertical",
          eyeOutline: "mdiEyeOutline",
          filter: "mdiFilter",
          flag: "mdiFlag",
          flagOutline: "mdiFlagOutline",
          formatAlignRight: "mdiFormatAlignRight",
          helpCircle: "mdiHelpCircle",
          helpCircleOutline: "mdiHelpCircleOutline",
          information: "mdiInformation",
          // The karma chip used to ask for `mdi-karma`, which Material Design
          // Icons dropped: it was absent from the font too, so the chip has
          // been drawing an empty box. A balance scale is what the number
          // means anyway - upvotes against downvotes.
          karma: "mdiScaleBalance",
          pound: "mdiPound",
          skipNextCircleOutline: "mdiSkipNextCircleOutline",
          weatherNight: "mdiWeatherNight",
          weatherSunny: "mdiWeatherSunny",
        },
      },
    },
  },
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
