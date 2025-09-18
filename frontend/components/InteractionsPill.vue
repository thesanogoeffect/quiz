<template>
  <v-card class="rounded-pill d-flex justify-space-evenly pa-2" elevation="3" outlined :style="{ backgroundColor: pillColor}">
    <!-- Upvote Button -->
    <v-btn
      :icon="upvoted ? 'mdi-arrow-up-bold' : 'mdi-arrow-up-bold-outline'"
      variant="plain"
      v-ripple
      class=" upvote-button pl-2"
      @click="handleUpvote"
      :color="upvoted ? 'success' : ''"
      :class="{ voted: upvoted }"
    ></v-btn>

    <!-- Karma Display -->
    <v-chip class="rounded-pill d-flex justify-center flex-shrink-0" style="min-width: 45px;">
      <v-avatar>
        <v-icon>mdi-karma</v-icon>
      </v-avatar>
      <!-- Conditionally set the color of the karma number -->
      <span
        :style="{
          color: karma > 0 ? '#4CAF50' : karma < 0 ? '#F44336' : '',
        }"
        >{{ karma }}</span
      >
    </v-chip>

    <!-- Downvote Button -->
    <v-btn
      :icon="downvoted ? 'mdi-arrow-down-bold' : 'mdi-arrow-down-bold-outline'"
      variant="plain"
      v-ripple
      class=""
      @click="handleDownvote"
      :color="downvoted ? 'error' : ''"
      :class="{ voted: downvoted }"
    ></v-btn>

    <!-- Flag Button -->
    <v-btn
      :icon="flagged ? 'mdi-flag' : 'mdi-flag-outline'"
      variant="plain"
      v-ripple
      class="pr-2"
      @click="toggleFlagged"
      :class="{ flagged: flagged }"
    ></v-btn>
  </v-card>
</template>

<script setup>
import { ref, computed } from "vue";
import { useQuestionStatsStore } from "#imports";
import { useQuestionStore } from "#imports";
import { useDisplay } from "#imports";

// Initialize the store
const questionStatsStore = useQuestionStatsStore();
const questionStore = useQuestionStore();
const display = useDisplay();


// Computed properties
const mdAndUp = computed(() => display.mdAndUp.value);
const theme = useTheme();

const pillColor = computed(() =>
      theme.global.name.value==="light" ? "#fdf2ea" : "#282828"
    );

const currentQuestion = computed(() => {
  return questionStore.getReviewMode
    ? questionStore.getCurrentlyReviewedQuestion
    : questionStore.getCurrentQuestion;
});
const currentQuestionId = computed(() => {
  return currentQuestion.value ? currentQuestion.value.id : null;
});

const statsCache = computed(() => {
  return currentQuestionId.value ? questionStatsStore.getQuestionStatsById(currentQuestionId.value) : null;
});

const upvoted = computed(() => {
  return currentQuestionId.value ? questionStatsStore.getUpvoteCacheById(currentQuestionId.value) : null;
});

const downvoted = computed(() => {
  return currentQuestionId.value ? questionStatsStore.getDownvoteCacheById(currentQuestionId.value) : null;
});

const flagged = computed(() => {
  return currentQuestionId.value ? questionStatsStore.getFlagCacheById(currentQuestionId.value) : null;
});

const karma = computed(() => {
  if (!statsCache.value) {
    return 0;
  }

  let karmaValue =
    statsCache.value.times_upvoted - statsCache.value.times_downvoted;

  return karmaValue;
});

// Handle upvote logic
const handleUpvote = () => {
  if (upvoted.value) {
    questionStatsStore.cancelUpvoteSpecificQuestion(currentQuestionId.value);
  } else {
    questionStatsStore.upvoteSpecificQuestion(currentQuestionId.value);
  }
};

// Handle downvote logic
const handleDownvote = () => {
  if (downvoted.value) {
    questionStatsStore.cancelDownvoteSpecificQuestion(currentQuestionId.value);
  } else {
    questionStatsStore.downvoteSpecificQuestion(currentQuestionId.value);
  }
};

// Toggle flagged state
const toggleFlagged = () => {
  if (flagged.value) {
    questionStatsStore.cancelFlagSpecificQuestion(currentQuestionId.value);
  } else {
    questionStatsStore.flagSpecificQuestion(currentQuestionId.value);
  }
};
</script>

<style scoped>
.rounded-pill {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.v-btn {
  transition: transform 0.2s ease-in-out;
}

.v-btn.voted {
  transform: scale(1.2);
}

.v-btn.flagged {
  color: red;
}
</style>
