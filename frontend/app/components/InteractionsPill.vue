<template>
  <!-- Sized to its contents rather than stretched by the flex row: the flag
       button used to be clipped off the right edge on any phone under ~430px. -->
  <v-card
    class="interactions-pill rounded-pill d-flex align-center"
    elevation="3"
    :style="{ backgroundColor: pillColor }"
  >
    <!-- Upvote Button -->
    <v-btn
      :icon="upvoted ? 'mdi-arrow-up-bold' : 'mdi-arrow-up-bold-outline'"
      variant="plain"
      density="comfortable"
      :disabled="!currentQuestionId"
      :color="upvoted ? 'success' : ''"
      :class="{ voted: upvoted }"
      :aria-label="upvoted ? 'Remove your upvote' : 'Upvote this question'"
      :title="upvoted ? 'Remove your upvote' : 'Upvote this question'"
      :aria-pressed="String(!!upvoted)"
      @click="handleUpvote"
    ></v-btn>

    <!-- Karma Display -->
    <v-chip
      class="karma-chip"
      size="small"
      :title="`Community score: ${karma}`"
    >
      <v-icon size="small" class="mr-1">mdi-karma</v-icon>
      <span
        :style="{
          color: karma > 0 ? '#2E7D32' : karma < 0 ? '#C62828' : '',
        }"
        >{{ karma }}</span
      >
    </v-chip>

    <!-- Downvote Button -->
    <v-btn
      :icon="downvoted ? 'mdi-arrow-down-bold' : 'mdi-arrow-down-bold-outline'"
      variant="plain"
      density="comfortable"
      :disabled="!currentQuestionId"
      :color="downvoted ? 'error' : ''"
      :class="{ voted: downvoted }"
      :aria-label="downvoted ? 'Remove your downvote' : 'Downvote this question'"
      :title="downvoted ? 'Remove your downvote' : 'Downvote this question'"
      :aria-pressed="String(!!downvoted)"
      @click="handleDownvote"
    ></v-btn>

    <!-- Flag Button -->
    <v-btn
      :icon="flagged ? 'mdi-flag' : 'mdi-flag-outline'"
      variant="plain"
      density="comfortable"
      :disabled="!currentQuestionId"
      :class="{ flagged: flagged }"
      :aria-label="flagged ? 'Remove your report' : 'Report a problem with this question'"
      :title="flagged ? 'Remove your report' : 'Report a problem with this question'"
      :aria-pressed="String(!!flagged)"
      @click="toggleFlagged"
    ></v-btn>
  </v-card>
</template>

<script setup>
import { computed } from "vue";
import { useTheme } from "vuetify";
import { useQuestionStatsStore } from "#imports";
import { useQuestionStore } from "#imports";

// Initialize the store
const questionStatsStore = useQuestionStatsStore();
const questionStore = useQuestionStore();
const theme = useTheme();

const pillColor = computed(() =>
  theme.global.name.value === "light" ? "#fdf2ea" : "#282828"
);

const currentQuestion = computed(() =>
  questionStore.getReviewMode
    ? questionStore.getCurrentlyReviewedQuestion
    : questionStore.getCurrentQuestion
);
const currentQuestionId = computed(() =>
  currentQuestion.value ? String(currentQuestion.value.id) : null
);

const statsCache = computed(() =>
  currentQuestionId.value
    ? questionStatsStore.getQuestionStatsById(currentQuestionId.value)
    : null
);

const upvoted = computed(() =>
  currentQuestionId.value
    ? questionStatsStore.getUpvoteCacheById(currentQuestionId.value)
    : false
);

const downvoted = computed(() =>
  currentQuestionId.value
    ? questionStatsStore.getDownvoteCacheById(currentQuestionId.value)
    : false
);

const flagged = computed(() =>
  currentQuestionId.value
    ? questionStatsStore.getFlagCacheById(currentQuestionId.value)
    : false
);

const karma = computed(() => {
  const stats = statsCache.value;
  if (!stats) return 0;
  return (Number(stats.times_upvoted) || 0) - (Number(stats.times_downvoted) || 0);
});

// Handle upvote logic
const handleUpvote = () => {
  if (!currentQuestionId.value) return;
  if (upvoted.value) {
    questionStatsStore.cancelUpvoteSpecificQuestion(currentQuestionId.value);
  } else {
    questionStatsStore.upvoteSpecificQuestion(currentQuestionId.value);
  }
};

// Handle downvote logic
const handleDownvote = () => {
  if (!currentQuestionId.value) return;
  if (downvoted.value) {
    questionStatsStore.cancelDownvoteSpecificQuestion(currentQuestionId.value);
  } else {
    questionStatsStore.downvoteSpecificQuestion(currentQuestionId.value);
  }
};

// Toggle flagged state
const toggleFlagged = () => {
  if (!currentQuestionId.value) return;
  if (flagged.value) {
    questionStatsStore.cancelFlagSpecificQuestion(currentQuestionId.value);
  } else {
    questionStatsStore.flagSpecificQuestion(currentQuestionId.value);
  }
};
</script>

<style scoped>
.interactions-pill {
  flex: 0 0 auto;
  gap: 2px;
  padding: 4px 8px;
}

.karma-chip {
  min-width: 52px;
  justify-content: center;
}

.v-btn {
  transition: transform 0.2s ease-in-out;
}

.v-btn.voted {
  transform: scale(1.15);
}

.v-btn.flagged {
  color: #c62828;
}
</style>
