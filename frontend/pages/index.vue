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
            Behavioral Research 1 Quiz
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
                :items="availableChapters"
                v-model="selectedChapters"
                label="Selected Lectures"
              >
                <template v-slot:append>
                  <v-tooltip bottom>
                    <template v-slot:activator="{ props }">
                      <v-btn icon="mdi-information-outline" v-bind="props" />
                    </template>
                    <span>
                    0: Canvas Practice Quiz<br />
                    1: Overview + Asking research questions<br />
                    2: Research: Questions, Designs and Methods<br />
                    3: Ethical aspects of behavioral research<br />
                    4: Analyzing qualitative interview data + social research<br />
                    5: Measurement and reliability<br />
                    6: Causal thinking & experiment basics<br />
                    7: Choosing your experiment design<br />
                    8: Quasi-experiment & experiment as social process<br />
                    9: Survey method + Intro to statistical inference<br />
                    10: Good research practices + Theory evaluation
                  </span>

                  </v-tooltip>
                </template>
              </v-select>
              <v-btn class="my-2 rounded-xl" @click="selectAllChapters"
                >Select All Lectures</v-btn
              >
              <v-btn class="my-2 rounded-xl" @click="deselectAllChapters"
                >Deselect All Lectures</v-btn
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
import { ref, computed, watch, onMounted } from "vue";
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
  title: "Behavioral Research 1 Quiz",
  meta: [
    {
      name: "description",
      content:
        "This is a student-made quiz app for the Behavioral Research & Design 1 course at TU/e in Eindhoven",
    },
  ],
  link: [
    { rel: "icon", type: "image/png", href: "/behav-1-quiz/favicon.ico" },
  ],
});

const display = useDisplay();

const mdAndUp = computed(() => display.mdAndUp.value);

const drawer = ref(true);
const rightDrawer = ref(true);

const dashboardUrl = "https://brm-1-questions.streamlit.app/";

const theme = useTheme();
const questionStore = useQuestionStore();
const generalStore = useGeneralStore();

const filterDialog = ref(false);

const availableChapters = computed(() => questionStore.getAllChapters.sort((a, b) => a - b));
const availableSources = computed(() => questionStore.getAllSources);

const selectedChapters = ref([]);
const selectedSources = ref([]);

const selectAllTUEChapters = () => {
  selectedChapters.value = [...availableChapters.value].sort((a, b) => a - b);
};

onMounted(() => {
  document.body.style.overflow = 'hidden';
});

onBeforeUnmount(() => {
  document.body.style.overflow = ''; // Restore scrolling when leaving the page
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
  questionStore.selected_chapters = selectedChapters.value;
  questionStore.selected_sources = selectedSources.value;
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
  // const selectedChaptersLocal = localStorage.getItem("selected_chapters_brm1");
  const selectedSourcesLocal = localStorage.getItem("selected_sources_brm1");
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
