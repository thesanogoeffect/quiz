<template>
  <v-app>
    <LandingPopup />
    <InstructionsPopup />
 
    <v-sheet>
      <v-layout column fill-height>
        <!-- App Bar -->
        <v-app-bar color="primary" prominent>
          <v-app-bar-nav-icon
            variant="text"
            @click="drawer = !drawer"
            icon="mdi-chart-bar"
          ></v-app-bar-nav-icon>  

          <v-toolbar-title class="app_title">
            Intro to P&T Quiz
          </v-toolbar-title>

          <v-spacer></v-spacer>
          <v-btn
            icon="mdi-filter"
            variant="text"
            @click="filterDialog = true"
          ></v-btn>
          <v-btn icon="mdi-theme-light-dark" @click="toggleTheme"></v-btn>
          <NuxtLink :to="{ name: 'about' }" class="no-blue-link">
            <v-btn icon="mdi-information" variant="text"></v-btn>
          </NuxtLink>
          <v-btn icon="mdi-help-circle" @click="openPopup"></v-btn>
          <v-btn
            icon="mdi-chart-bell-curve"
            variant="text"
            @click="openDashboardInNewTab"
          ></v-btn>

          <v-btn
            icon="mdi-format-align-right"
            variant="text"
            @click="toggleRightDrawer"
          ></v-btn>

        </v-app-bar>

        <!-- Left Navigation Drawer -->
        <v-navigation-drawer v-model="drawer" location="left">
          <LeftSidebar />
        </v-navigation-drawer>

        <!-- Right Navigation Drawer (RightSidebar) -->
        <v-navigation-drawer v-model="rightDrawer" location="right">
          <RightSidebar />
        </v-navigation-drawer>

        <v-main>
          <MainQuestionWindow />
        </v-main>
      </v-layout>

      <v-dialog v-model="filterDialog" max-width="600px">
        <v-card class="rounded-xl">
          <v-card-title class="headline">Question Filter</v-card-title>

          <v-card-text>
            <!-- Chapter Selection -->
            <div class="mb-4">
              <v-select
                multiple
                variant="outlined"
                :items="chapterItems"
                item-title="title"
                item-value="value"
                item-disabled="disabled"
                v-model="selectedChapters"
                label="Selected Chapters"
              >
                <template v-slot:append>
                  <v-tooltip bottom>
                    <template v-slot:activator="{ props }">
                      <v-btn icon="mdi-information-outline" v-bind="props" />
                    </template>
                    <span>
                    1: Introduction to Psychology<br />
                    2: Psychological Research<br />
                    3: Biopsychology<br />
                    4: States of Consciousness<br />
                    5: Sensation and Perception<br />
                    6: Learning<br />
                    7: Thinking and Intelligence<br />
                    8: Memory<br />
                    9: Lifespan Development<br />
                    10: Motivation and Emotion<br />
                    12: Social Psychology<br />
                    14: Stress, Lifestyle, and Health<br />
                  </span>

                  </v-tooltip>
                </template>
              </v-select>
              <v-btn class="my-2 rounded-xl" @click="selectAllChapters"
                >Select All Chapters</v-btn
              >
              <v-btn class="my-2 rounded-xl" @click="deselectAllChapters"
                >Deselect All Chapters</v-btn
              >

              <v-divider class=""></v-divider>

            </div>

            <!-- Source Selection -->
            <div class="mb-4">
              <v-select
                multiple
                variant="outlined"
                :items="availableSources"
                v-model="selectedSources"
                label="Selected Sources"
              ></v-select>
              <v-btn class="my-2 rounded-xl" @click="selectAllSources"
                >Select All Sources</v-btn
              >
              <v-btn class="my-2 rounded-xl" @click="deselectAllSources"
                >Deselect All Sources</v-btn
              >
            </div>
          </v-card-text>

          <v-card-actions class="justify-end">
            <v-btn @click="filterDialog = false">Cancel</v-btn>
            <v-btn
              :disabled="!canApplyFilters"
              color="primary"
              @click="applyFilters"
              >Apply</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-sheet>

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

useHead({
  title: "Intro to P&T Quiz",
  meta: [
    {
      name: "description",
      content:
        "This is a student-made quiz app for the Intro to Psychology & Technology course at TU/e Eindhoven",
    },
  ],
  link: [
    { rel: "icon", type: "image/png", href: "favicon.ico" },
  ],
});

const display = useDisplay();

const mdAndUp = computed(() => display.mdAndUp.value);

const drawer = ref(true);
const rightDrawer = ref(true);

const dashboardUrl = "https://ipt-quiz.streamlit.app/";

const theme = useTheme();
const questionStore = useQuestionStore();
const generalStore = useGeneralStore();

const filterDialog = ref(false);

const availableChapters = computed<number[]>(() =>
  [...(questionStore.getAllChapters as number[])].sort((a, b) => a - b)
);
const availableSources = computed<string[]>(() =>
  [...(questionStore.getAllSources as string[])]
);

const selectedChapters = ref<number[]>([]);
const selectedSources = ref<string[]>([]);

const banlistChapters = computed<number[]>(() => (questionStore as any).BANLIST_CHAPTERS ?? []);
const chapterItems = computed(() => {
  const toLabel = (id: number) => {
    const name = questionStore.getChapterById(id);
    return name ? `Chapter ${id}: ${name}` : `Chapter ${id}`;
  };
  const allowed = (availableChapters.value || []).map((id) => ({
    title: toLabel(id),
    value: id,
    disabled: false,
  }));
  const banned = (banlistChapters.value || [])
    .filter((id: number) => !availableChapters.value.includes(id))
    .map((id: number) => ({
      title: `${toLabel(id)} (disabled)`,
      value: id,
      disabled: true,
    }));
  return [...allowed, ...banned].sort((a, b) => a.value - b.value);
});

const selectAllTUEChapters = () => {
  const banned = new Set(banlistChapters.value);
  selectedChapters.value = availableChapters.value.filter((id) => !banned.has(id));
};

onMounted(() => {
  document.body.style.overflow = 'hidden';
});

onBeforeUnmount(() => {
  const banned = new Set(banlistChapters.value);
  selectedChapters.value = [...availableChapters.value]
    .filter((id) => !banned.has(id))
    .sort((a, b) => a - b);
});

watch(
  [availableChapters, availableSources],
  ([newChapters, newSources]) => {
    if (newChapters && newChapters.length > 0) {
      selectAllTUEChapters();
    }
    if (newSources && newSources.length > 0) {
      selectedSources.value = [...newSources];
    }
  },
  { immediate: true }
);

// Safety: ensure no banned chapters can end up selected
watch(
  selectedChapters,
  (newVal) => {
    const banned = new Set(banlistChapters.value);
    const sanitized = (newVal || []).filter((id) => !banned.has(id));
    if (sanitized.length !== (newVal || []).length) {
      selectedChapters.value = sanitized;
    }
  },
  { deep: true }
);

watch(mdAndUp, (newVal) => {
  if (!newVal) {
    drawer.value = false;
    rightDrawer.value = false;
  } else {
    drawer.value = true;
    rightDrawer.value = true;
  }
});

function toggleTheme() {
  theme.global.name.value =
    theme.global.name.value === "light" ? "dark" : "light";
}

function toggleRightDrawer() {
  rightDrawer.value = !rightDrawer.value;
}

function openDashboardInNewTab() {
  window.open(dashboardUrl, '_blank', 'noopener,noreferrer')
}

async function applyFilters() {
  (questionStore as any).selected_chapters = selectedChapters.value;
  (questionStore as any).selected_sources = selectedSources.value;
  // save to local storage
  questionStore.saveSelectedFiltersToLocalStorage();
  await questionStore.reSetUpAfterFiltersChange();
  filterDialog.value = false;
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

const canApplyFilters = computed(() => {
  return selectedChapters.value.length > 0 && selectedSources.value.length > 0;
});

const openPopup = () => {
  generalStore.toggleInstructionsPopup();
};

onMounted(() => {
  // const selectedChaptersLocal = localStorage.getItem("selected_chapters_ipt");
  const selectedSourcesLocal = localStorage.getItem("selected_sources_ipt");
  // if (selectedChaptersLocal) {
  //   selectedChapters.value = JSON.parse(selectedChaptersLocal);
  // }
  if (selectedSourcesLocal) {
    selectedSources.value = JSON.parse(selectedSourcesLocal);
  }
  const currentHour = new Date().getHours();
  theme.global.name.value =
    currentHour >= 19 || currentHour < 6 ? "dark" : "light";

  // set the drawers to false on mobile
  if (!mdAndUp.value) {
    drawer.value = false;
    rightDrawer.value = false;
  }
});


</script>

<style scoped>
.v-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}


.headline {
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  padding-bottom: 10px;
}

.v-card-text {
  padding-bottom: 0;
}

.mb-4 {
  margin-bottom: 16px;
}

.mx-2 {
  margin-left: 8px;
  margin-right: 8px;
}

.my-3 {
  margin-top: 12px;
  margin-bottom: 12px;
}

.justify-end {
  display: flex;
  justify-content: flex-end;
}

.bottom-right {
  position: fixed;
  bottom: 10px;
  right: 10px;
}

.no-blue-link {
  color: inherit;
  text-decoration: none;
}
</style>
