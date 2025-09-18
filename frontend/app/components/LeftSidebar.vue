<template>
  <v-container class="py-3">
    <v-row>
      <v-col>
        <v-container
          class="stats-container pa-3 rounded-xl"
          style="border: 0;"
          :style="{ backgroundColor: sidebarCardsColor }"
          elevation="1"
        >
          <h2 class="mb-2 text-center">Stats</h2>
          <v-divider></v-divider>
          <br>
          <!-- Existing User Stats -->
          <v-row>
            <v-col cols="2" xs="3">
              <v-icon color="secondary">mdi-eye-outline</v-icon>
            </v-col>
            <v-col cols="7" xs="6">Total Shown:</v-col>
            <v-col cols="3" xs="3">
              {{ questionStore.getTotalShownQuestions }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" xs="3">
              <v-icon color="primary"
                >mdi-checkbox-marked-circle-outline</v-icon
              >
            </v-col>
            <v-col cols="7" xs="6">Answered:</v-col>
            <v-col cols="3" xs="3">
              {{ questionStore.getTotalAnsweredQuestions }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" xs="3">
              <v-icon color="success">mdi-check-circle-outline</v-icon>
            </v-col>
            <v-col cols="7" xs="6">Correct:</v-col>
            <v-col cols="3" xs="3">
              {{ questionStore.getTotalCorrectAnswers }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" xs="3">
              <v-icon color="warning">mdi-skip-next-circle-outline</v-icon>
            </v-col>
            <v-col cols="7" xs="6">Skipped:</v-col>
            <v-col cols="3" xs="3">
              {{ questionStore.getSkippedQuestions }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" xs="3">
              <v-icon color="info">mdi-help-circle-outline</v-icon>
            </v-col>
            <v-col cols="7" xs="6">Skips Left:</v-col>
            <v-col cols="3" xs="3">{{ questionStore.getSkipsRemaining }}</v-col>
          </v-row>
          <v-row
            v-show="questionStore.getTotalAnsweredQuestions > 0"
            justify="center"
          >
            <v-col cols="12" class="text-center">
              <v-progress-circular
                :model-value="userPercentage"
                :color="circularColor"
                size="85"
                width="13"
              >
                <span :class="percentageClass">{{ formattedPercentage }}%</span>
              </v-progress-circular>
            </v-col>
          </v-row>

          <!-- Toggle for Global Stats -->
          <v-row class="mt-4">
            <v-col cols="12">
              <v-switch
                v-model="showGlobalStats"
                label="Show Community Question Stats"
                color="primary"
              ></v-switch>
            </v-col>
          </v-row>
          <!-- Global Stats Section -->
          <div v-if="showGlobalStats">
            
            <h2 class="mb-2 mt-4 text-center">Community Stats for Question</h2>
            <v-divider></v-divider>
            <v-row>
              <v-col cols="2" xs="3">
                <v-icon color="secondary">mdi-eye-outline</v-icon>
              </v-col>
              <v-col cols="7" xs="6">Times Asked:</v-col>
              <v-col cols="3" xs="3">{{ questionStats.times_asked }}</v-col>
            </v-row>
            <v-row>
              <v-col cols="2" xs="3">
                <v-icon color="success">mdi-check-circle-outline</v-icon>
              </v-col>
              <v-col cols="7" xs="6">Answered Correctly:</v-col>
              <v-col cols="3" xs="3">{{
                questionStats.times_answered_correct
              }}</v-col>
            </v-row>
            <v-row>
              <v-col cols="2" xs="3">
                <v-icon color="primary"
                  >mdi-checkbox-marked-circle-outline</v-icon
                >
              </v-col>
              <v-col cols="7" xs="6">Times Answered:</v-col>
              <v-col cols="3" xs="3">{{ questionStats.times_answered }}</v-col>
            </v-row>
            <v-row>
              <v-col cols="2" xs="3">
                <v-icon color="warning">mdi-skip-next-circle-outline</v-icon>
              </v-col>
              <v-col cols="7" xs="6">Times Skipped:</v-col>
              <v-col cols="3" xs="3">{{ questionStats.times_skipped }}</v-col>
            </v-row>
            <v-row>
              <v-col cols="2" xs="3">
                <v-icon color="error">mdi-flag-outline</v-icon>
              </v-col>
              <v-col cols="7" xs="6">Times Flagged:</v-col>
              <v-col cols="3" xs="3">{{ questionStats.times_flagged }}</v-col>
            </v-row>
            <v-row v-show="questionStats.times_answered > 0" justify="center">
              <v-col cols="12" class="text-center">
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
                <div>Community Percentage</div>
              </v-col>
            </v-row>
          </div>
        </v-container>
      </v-col>
    </v-row>
  </v-container>
  <v-divider></v-divider>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
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
  if (userPercentage.value >= 70) {
    return "success";
  } else if (userPercentage.value >= 40) {
    return "warning";
  } else {
    return "error";
  }
});
const percentageClass = computed(() => {
  if (userPercentage.value >= 70) {
    return "text-success";
  } else if (userPercentage.value >= 40) {
    return "text-warning";
  } else {
    return "text-error";
  }
});

const currentQuestion = computed(() =>
  questionStore.getReviewMode
    ? questionStore.getCurrentlyReviewedQuestion
    : questionStore.getCurrentQuestion
);
console.log(currentQuestion.value);
const currentQuestionId = computed(() =>
  currentQuestion.value ? currentQuestion.value.id : null
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
  } else {
    return 0;
  }
});

const globalCircularColor = computed(() => {
  if (correctPercentage.value >= 60) {
    return "success";
  } else if (correctPercentage.value >= 30) {
    return "warning";
  } else {
    return "error";
  }
});

const globalPercentageClass = computed(() => {
  if (correctPercentage.value >= 70) {
    return "text-success";
  } else if (correctPercentage.value >= 40) {
    return "text-warning";
  } else {
    return "text-error";
  }
});
</script>

<style scoped>
.stats-container {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h2 {
  font-weight: bold;
  font-size: 1.5rem;
}

h3 {
  font-weight: 500;
  font-size: 1.2rem;
  color: #666;
}

.v-progress-circular {
  margin: 10px 0;
}
</style>
