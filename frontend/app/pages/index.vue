<template>
  <v-app>
    <LandingPopup />
    <InstructionsPopup />

    <v-layout class="quiz-layout">
      <!-- App Bar -->
      <v-app-bar color="primary" density="comfortable" flat>
        <v-app-bar-nav-icon
          variant="text"
          @click="drawer = !drawer"
          icon="mdi-chart-bar"
          aria-label="Toggle your stats"
          title="Your stats"
        ></v-app-bar-nav-icon>

        <v-toolbar-title class="app_title">
          {{ mdAndUp ? "Intro to P&amp;T Quiz" : "P&amp;T Quiz" }}
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn
          icon="mdi-filter"
          variant="text"
          aria-label="Filter questions"
          title="Filter questions"
          @click="filterDialog = true"
        ></v-btn>
        <v-btn
          :icon="isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
          variant="text"
          :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          :title="isDark ? 'Light mode' : 'Dark mode'"
          @click="toggleTheme"
        ></v-btn>
        <v-btn
          icon="mdi-help-circle"
          variant="text"
          aria-label="How this works"
          title="How this works"
          @click="openPopup"
        ></v-btn>

        <!-- Secondary actions collapse into a menu on phones so nothing is
             pushed off the edge of the toolbar. -->
        <v-menu v-if="!mdAndUp">
          <template v-slot:activator="{ props }">
            <v-btn
              icon="mdi-dots-vertical"
              variant="text"
              aria-label="More"
              v-bind="props"
            ></v-btn>
          </template>
          <v-list density="compact">
            <v-list-item
              prepend-icon="mdi-chart-bell-curve"
              title="Question bank"
              :to="{ name: 'questions' }"
            ></v-list-item>
            <v-list-item
              prepend-icon="mdi-information"
              title="About"
              :to="{ name: 'about' }"
            ></v-list-item>
            <v-list-item
              prepend-icon="mdi-format-align-right"
              title="Question info"
              @click="toggleRightDrawer"
            ></v-list-item>
          </v-list>
        </v-menu>

        <template v-else>
          <v-btn
            icon="mdi-chart-bell-curve"
            variant="text"
            aria-label="Question bank"
            title="Question bank"
            :to="{ name: 'questions' }"
          ></v-btn>
          <v-btn
            icon="mdi-information"
            variant="text"
            aria-label="About this project"
            title="About"
            :to="{ name: 'about' }"
          ></v-btn>
          <v-btn
            icon="mdi-format-align-right"
            variant="text"
            aria-label="Toggle question info"
            title="Question info"
            @click="toggleRightDrawer"
          ></v-btn>
        </template>
      </v-app-bar>

      <!-- The drawers only reserve space for themselves from Vuetify's `lg`
           breakpoint (1280px) up. Below that they are temporary overlays with a
           scrim, so opening them by default covered the question on anything
           between 960px and 1279px wide - small laptops, zoomed browsers and
           tablets in landscape. `wide` and `mobile-breakpoint` must agree. -->
      <v-navigation-drawer v-model="drawer" location="left" mobile-breakpoint="lg">
        <LeftSidebar />
      </v-navigation-drawer>

      <!-- Right Navigation Drawer (RightSidebar) -->
      <v-navigation-drawer
        v-model="rightDrawer"
        location="right"
        mobile-breakpoint="lg"
      >
        <RightSidebar />
      </v-navigation-drawer>

      <v-main class="quiz-main">
        <MainQuestionWindow />
      </v-main>
    </v-layout>

    <v-dialog v-model="filterDialog" max-width="600px" scrollable>
      <v-card class="rounded-xl">
        <v-card-title class="headline">Question Filter</v-card-title>

        <v-card-text>
          <!-- Chapter Selection -->
          <div class="mb-4">
            <v-select
              multiple
              chips
              closable-chips
              variant="outlined"
              :items="chapterItems"
              item-title="title"
              item-value="value"
              item-props
              v-model="selectedChapters"
              label="Selected Chapters"
            ></v-select>
            <v-btn class="my-2 mr-2 rounded-xl" @click="selectAllChapters"
              >Select All Chapters</v-btn
            >
            <v-btn class="my-2 rounded-xl" @click="deselectAllChapters"
              >Deselect All Chapters</v-btn
            >

            <v-divider></v-divider>
          </div>

          <!-- Source Selection -->
          <div class="mb-4">
            <v-select
              multiple
              chips
              closable-chips
              variant="outlined"
              :items="sourceItems"
              v-model="selectedSources"
              label="Selected Sources"
            ></v-select>
            <v-btn class="my-2 mr-2 rounded-xl" @click="selectAllSources"
              >Select All Sources</v-btn
            >
            <v-btn class="my-2 rounded-xl" @click="deselectAllSources"
              >Deselect All Sources</v-btn
            >
          </div>

          <!-- Tells the user up front how big the pool is, so they cannot
               apply a combination that has no questions at all. -->
          <v-alert
            :type="matchingQuestionCount > 0 ? 'info' : 'warning'"
            variant="tonal"
            density="compact"
            class="rounded-lg"
          >
            {{
              matchingQuestionCount > 0
                ? `${matchingQuestionCount} question${
                    matchingQuestionCount === 1 ? "" : "s"
                  } match this selection.`
                : "No questions match this selection - not every chapter has questions from every source."
            }}
          </v-alert>
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn @click="cancelFilters">Cancel</v-btn>
          <v-btn :disabled="!canApplyFilters" color="primary" @click="applyFilters"
            >Apply</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="showFilterWarning" color="warning" timeout="5000">
      {{ questionStore.getFilterWarning }}
    </v-snackbar>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import { useTheme } from "vuetify";
import { useDisplay } from "#imports";
import LeftSidebar from "~/components/LeftSidebar.vue";
import MainQuestionWindow from "~/components/MainQuestionWindow.vue";
import RightSidebar from "~/components/RightSidebar.vue";
import { useQuestionStore } from "#imports";
import LandingPopup from "~/components/LandingPopup.vue";
import InstructionsPopup from "~/components/InstructionsPopup.vue";
import { useGeneralStore } from "~/stores/generalstore";

const THEME_STORAGE_KEY = "ipt_quiz_theme";

const display = useDisplay();
const mdAndUp = computed(() => display.mdAndUp.value);
// Wide enough for both drawers to sit beside the question instead of over it.
const wide = computed(() => display.lgAndUp.value);

const drawer = ref(false);
const rightDrawer = ref(false);

const theme = useTheme();
const questionStore = useQuestionStore();
const generalStore = useGeneralStore();

const filterDialog = ref(false);
const isDark = computed(() => theme.global.name.value === "dark");

const showFilterWarning = computed({
  get: () => !!questionStore.getFilterWarning,
  set: (value: boolean) => {
    if (!value) (questionStore as any).filterWarning = null;
  },
});

const availableChapters = computed<number[]>(() =>
  [...(questionStore.getAllChapters as number[])].sort((a, b) => a - b)
);
const availableSources = computed<string[]>(() => [
  ...(questionStore.getAllSources as string[]),
]);
// The select shows friendly names but keeps the raw source string as its value.
const sourceItems = computed(() =>
  availableSources.value.map((s) => ({
    title: questionStore.getSourceLabel(s) as string,
    value: s,
  }))
);

const selectedChapters = ref<number[]>([]);
const selectedSources = ref<string[]>([]);

const chapterItems = computed(() =>
  availableChapters.value.map((id) => {
    const name = questionStore.getChapterById(id);
    return { title: name ? `Chapter ${id}: ${name}` : `Chapter ${id}`, value: id };
  })
);

// Live count for the dialog. filteredQuestions treats an empty array as "no
// filter", so an emptied selection has to short-circuit to zero rather than
// report the whole pool.
const matchingQuestionCount = computed(() => {
  if (!selectedChapters.value.length || !selectedSources.value.length) return 0;
  return (questionStore as any).filteredQuestions(
    selectedChapters.value,
    selectedSources.value
  ).length;
});

const canApplyFilters = computed(
  () =>
    selectedChapters.value.length > 0 &&
    selectedSources.value.length > 0 &&
    matchingQuestionCount.value > 0
);

// Mirror whatever the store settled on (stored filters, or the defaults) into
// the dialog. Previously this clobbered the user's saved selection.
watch(
  () => [questionStore.getSelectedChapters, questionStore.getSelectedSources],
  ([chapters, sources]) => {
    selectedChapters.value = [...(chapters as number[])].sort((a, b) => a - b);
    selectedSources.value = [...(sources as string[])];
  },
  { immediate: true, deep: true }
);

// Only force the drawers shut when dropping to a narrow viewport, where they
// would cover the question. Growing back to desktop leaves whatever the user
// chose alone.
watch(wide, (isWide, wasWide) => {
  if (!isWide) {
    drawer.value = false;
    rightDrawer.value = false;
  } else if (wasWide === false) {
    drawer.value = true;
    rightDrawer.value = true;
  }
});

function toggleTheme() {
  const next = isDark.value ? "light" : "dark";
  theme.global.name.value = next;
  try {
    localStorage.setItem(THEME_STORAGE_KEY, next);
  } catch {
    /* private browsing - the theme just will not persist */
  }
}

function toggleRightDrawer() {
  rightDrawer.value = !rightDrawer.value;
}

function syncFiltersFromStore() {
  selectedChapters.value = [
    ...(questionStore.getSelectedChapters as number[]),
  ].sort((a, b) => a - b);
  selectedSources.value = [...(questionStore.getSelectedSources as string[])];
}

function cancelFilters() {
  syncFiltersFromStore();
  filterDialog.value = false;
}

// Escape and a scrim click close the dialog without going through Cancel, so
// re-sync on open rather than on close - otherwise the next open shows a
// selection that was never applied.
watch(filterDialog, (open) => {
  if (open) syncFiltersFromStore();
});

async function applyFilters() {
  (questionStore as any).selected_chapters = selectedChapters.value;
  (questionStore as any).selected_sources = selectedSources.value;
  const ok = await questionStore.reSetUpAfterFiltersChange();
  if (ok) {
    questionStore.saveSelectedFiltersToLocalStorage();
    filterDialog.value = false;
  }
}

const selectAllChapters = () => {
  selectedChapters.value = [...availableChapters.value];
};

const deselectAllChapters = () => {
  selectedChapters.value = [];
};

const selectAllSources = () => {
  selectedSources.value = [...availableSources.value];
};

const deselectAllSources = () => {
  selectedSources.value = [];
};

const openPopup = () => {
  generalStore.toggleInstructionsPopup();
};

onMounted(async () => {
  drawer.value = wide.value;
  rightDrawer.value = wide.value;

  // Respect an explicit choice; otherwise fall back to the system preference,
  // then to the time of day. It used to reset to the clock on every reload,
  // undoing whatever the user had picked.
  let stored: string | null = null;
  try {
    stored = localStorage.getItem(THEME_STORAGE_KEY);
  } catch {
    /* ignore */
  }
  if (stored === "light" || stored === "dark") {
    theme.global.name.value = stored;
  } else if (window.matchMedia?.("(prefers-color-scheme: dark)").matches) {
    theme.global.name.value = "dark";
  } else {
    const currentHour = new Date().getHours();
    theme.global.name.value =
      currentHour >= 19 || currentHour < 6 ? "dark" : "light";
  }

  // The question set is loaded by app.vue on every route; serving the first
  // question happens here, so /about and /questions do not record a view for a
  // question nobody saw.
  await questionStore.startQuiz();
});

onBeforeUnmount(() => {
  filterDialog.value = false;
});
</script>

<style scoped>
/* 100dvh rather than 100vh so mobile browser chrome does not push the
   navigation buttons below the fold. */
.quiz-layout {
  min-height: 100dvh;
}

/* v-toolbar-title reserves a wide flex basis and then ellipsises; on a phone
   that turned "P&T Quiz" into "P&T…". Let it size to its own text instead. */
.app_title {
  flex: 0 1 auto;
  min-width: 0;
  white-space: nowrap;
}

@media (max-width: 599px) {
  .app_title {
    font-size: 1.05rem;
  }
}

.headline {
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  padding-bottom: 10px;
}

.mb-4 {
  margin-bottom: 16px;
}

.justify-end {
  display: flex;
  justify-content: flex-end;
}
</style>
