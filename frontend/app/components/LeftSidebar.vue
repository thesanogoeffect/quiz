<template>
  <v-container class="py-3">
    <v-card
      class="stats-container pa-3 rounded-xl"
      flat
      :style="{ backgroundColor: sidebarCardsColor }"
    >
      <h2 class="mb-2 text-center">Stats</h2>
      <v-divider class="mb-3"></v-divider>

      <!-- Existing User Stats -->
      <div class="stat-row">
        <v-icon color="secondary" size="small">mdi-eye-outline</v-icon>
        <span class="stat-label">Total Shown:</span>
        <span class="stat-value">{{ questionStore.getTotalShownQuestions }}</span>
      </div>
      <div class="stat-row">
        <v-icon color="primary" size="small">mdi-checkbox-marked-circle-outline</v-icon>
        <span class="stat-label">Answered:</span>
        <span class="stat-value">{{ questionStore.getTotalAnsweredQuestions }}</span>
      </div>
      <div class="stat-row">
        <v-icon color="success" size="small">mdi-check-circle-outline</v-icon>
        <span class="stat-label">Correct:</span>
        <span class="stat-value">{{ questionStore.getTotalCorrectAnswers }}</span>
      </div>
      <div class="stat-row">
        <v-icon color="warning" size="small">mdi-skip-next-circle-outline</v-icon>
        <span class="stat-label">Skipped:</span>
        <span class="stat-value">{{ questionStore.getSkippedQuestions }}</span>
      </div>
      <div class="stat-row">
        <v-icon color="info" size="small">mdi-help-circle-outline</v-icon>
        <span class="stat-label">Skips Left:</span>
        <span class="stat-value">{{ questionStore.getSkipsRemaining }}</span>
      </div>

      <div v-show="questionStore.getTotalAnsweredQuestions > 0" class="text-center mt-4">
        <v-progress-circular
          :model-value="userPercentage"
          :color="circularColor"
          size="85"
          width="13"
        >
          <span :class="percentageClass">{{ formattedPercentage }}%</span>
        </v-progress-circular>
        <div class="text-caption text-medium-emphasis">Your accuracy</div>
      </div>

      <!-- Toggle for Global Stats -->
      <v-switch
        v-model="showGlobalStats"
        label="Show community stats"
        color="primary"
        density="compact"
        hide-details
        class="mt-3"
      ></v-switch>

      <!-- Global Stats Section -->
      <div v-if="showGlobalStats">
        <h2 class="mb-2 mt-4 text-center">Community Stats</h2>
        <v-divider class="mb-3"></v-divider>

        <v-alert
          v-if="!questionStatsStore.getStatsAvailable"
          type="info"
          variant="tonal"
          density="compact"
          class="mb-3 rounded-lg text-caption"
        >
          Community stats are unavailable right now.
        </v-alert>

        <div class="stat-row">
          <v-icon color="secondary" size="small">mdi-eye-outline</v-icon>
          <span class="stat-label">Times Asked:</span>
          <span class="stat-value">{{ questionStats.times_asked }}</span>
        </div>
        <div class="stat-row">
          <v-icon color="success" size="small">mdi-check-circle-outline</v-icon>
          <span class="stat-label">Answered Correctly:</span>
          <span class="stat-value">{{ questionStats.times_answered_correct }}</span>
        </div>
        <div class="stat-row">
          <v-icon color="primary" size="small">mdi-checkbox-marked-circle-outline</v-icon>
          <span class="stat-label">Times Answered:</span>
          <span class="stat-value">{{ questionStats.times_answered }}</span>
        </div>
        <div class="stat-row">
          <v-icon color="warning" size="small">mdi-skip-next-circle-outline</v-icon>
          <span class="stat-label">Times Skipped:</span>
          <span class="stat-value">{{ questionStats.times_skipped }}</span>
        </div>
        <div class="stat-row">
          <v-icon color="error" size="small">mdi-flag-outline</v-icon>
          <span class="stat-label">Times Reported:</span>
          <span class="stat-value">{{ questionStats.times_flagged }}</span>
        </div>

        <div v-show="questionStats.times_answered > 0" class="text-center mt-3">
          <v-progress-circular
            :model-value="correctPercentage"
            :color="globalCircularColor"
            size="78"
            width="10"
          >
            <span :class="globalPercentageClass"
              >{{ correctPercentage.toFixed(1) }}%</span
            >
          </v-progress-circular>
          <div class="text-caption text-medium-emphasis">
            Everyone else on this question
          </div>
        </div>
      </div>
    </v-card>
  </v-container>
</template>

<script setup>
import { computed, ref } from "vue";
import { useTheme } from "vuetify";
import { useQuestionStore, useQuestionStatsStore } from "#imports";

const showGlobalStats = ref(false);
const theme = useTheme();
const sidebarCardsColor = computed(() =>
  theme.global.name.value === "light" ? "#fdf2ea" : "#282828"
);

const questionStore = useQuestionStore();
const questionStatsStore = useQuestionStatsStore();

const userPercentage = computed(
  () => questionStore.getAnsweredCorrectlyPercentage
);
const formattedPercentage = computed(() => userPercentage.value.toFixed(1));
const circularColor = computed(() => {
  if (userPercentage.value >= 70) return "success";
  if (userPercentage.value >= 40) return "warning";
  return "error";
});
const percentageClass = computed(() => {
  if (userPercentage.value >= 70) return "text-success";
  if (userPercentage.value >= 40) return "text-warning";
  return "text-error";
});

const currentQuestion = computed(() =>
  questionStore.getReviewMode
    ? questionStore.getCurrentlyReviewedQuestion
    : questionStore.getCurrentQuestion
);
const currentQuestionId = computed(() =>
  currentQuestion.value ? String(currentQuestion.value.id) : null
);
const questionStats = computed(
  () =>
    questionStatsStore.getQuestionStatsById(currentQuestionId.value) || {
      times_asked: 0,
      times_answered_correct: 0,
      times_skipped: 0,
      times_flagged: 0,
      times_answered: 0,
      times_upvoted: 0,
      times_downvoted: 0,
    }
);

const correctPercentage = computed(() => {
  if (questionStats.value.times_answered > 0) {
    return (
      (questionStats.value.times_answered_correct /
        questionStats.value.times_answered) *
      100
    );
  }
  return 0;
});

const globalCircularColor = computed(() => {
  if (correctPercentage.value >= 60) return "success";
  if (correctPercentage.value >= 30) return "warning";
  return "error";
});

const globalPercentageClass = computed(() => {
  if (correctPercentage.value >= 70) return "text-success";
  if (correctPercentage.value >= 40) return "text-warning";
  return "text-error";
});
</script>

<style scoped>
.stats-container {
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h2 {
  font-weight: bold;
  font-size: 1.35rem;
}

/* A grid rather than v-row/v-col: the old markup used xs="…" props, which do
   not exist in Vuetify 3, so the columns never reflowed as intended. */
.stat-row {
  display: grid;
  grid-template-columns: 24px 1fr auto;
  align-items: center;
  gap: 8px;
  padding: 5px 0;
}

.stat-value {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}
</style>
