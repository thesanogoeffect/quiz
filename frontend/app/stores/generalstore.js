const LANDING_KEY = "landingPopupLastShownIPT";

export const useGeneralStore = defineStore("general", {
  state: () => ({
    landingPopup: false,
    instructionsPopup: false,
  }),
  actions: {
    toggleLandingPopup() {
      this.landingPopup = !this.landingPopup;
      // Remember the day it was dismissed so it only shows once per day.
      if (!this.landingPopup) {
        try {
          localStorage.setItem(LANDING_KEY, new Date().toISOString().split("T")[0]);
        } catch {
          /* private browsing - it will just show again */
        }
      }
    },
    toggleInstructionsPopup() {
      this.instructionsPopup = !this.instructionsPopup;
    },
    checkLandingPopup() {
      let lastShownDate = null;
      try {
        lastShownDate = localStorage.getItem(LANDING_KEY);
      } catch {
        /* ignore */
      }
      const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
      this.landingPopup = lastShownDate !== today;
    },
  },
  getters: {
    getLandingPopup: (state) => state.landingPopup,
    getInstructionsPopup: (state) => state.instructionsPopup,
  },
});
