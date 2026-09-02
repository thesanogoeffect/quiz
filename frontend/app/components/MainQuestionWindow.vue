<template>
  <v-sheet class="main-sheet">
    <v-container class="quiz-container">
      <!-- Something went wrong loading the question set -->
      <div
        v-if="questionStore.getLoadError"
        class="d-flex flex-column align-center justify-center text-center flex-grow-1 ga-4"
      >
        <v-icon size="48" color="warning">$cloudAlert</v-icon>
        <p class="text-body-1">{{ questionStore.getLoadError }}</p>
        <v-btn color="primary" @click="reload">Try again</v-btn>
      </div>

      <!-- Normal quiz flow -->
      <template v-else-if="questionStore.getCurrentQuestion">
        <GuessQuestionWindow v-if="!questionStore.reviewMode" />
        <ReviewQuestionWindow v-else />
        <QuestionNavigation />
      </template>

      <!-- Initial load -->
      <div
        v-else
        class="d-flex flex-column align-center justify-center flex-grow-1 ga-4"
      >
        <v-progress-circular color="primary" indeterminate></v-progress-circular>
        <span class="text-medium-emphasis">Loading questions…</span>
      </div>
    </v-container>
  </v-sheet>
</template>

<script setup>
import { useQuestionStore } from "#imports";
import GuessQuestionWindow from "./GuessQuestionWindow.vue";
import ReviewQuestionWindow from "./ReviewQuestionWindow.vue";
import QuestionNavigation from "./QuestionNavigation.vue";

const questionStore = useQuestionStore();

function reload() {
  window.location.reload();
}
</script>

<style scoped>
.main-sheet {
  display: flex;
  justify-content: center;
  min-height: calc(100dvh - 64px);
}

/* The question card sits directly under the app bar, level with the sidebar
   cards, and grows with its content so long questions push the page into a
   normal scroll instead of being clipped. Centring it vertically left a
   viewport-sized blank band above the question on any large screen. */
.quiz-container {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 12px;
  min-height: calc(100dvh - 64px);
  max-width: 1000px;
  padding-bottom: 16px;
}
</style>

<style>
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-thumb {
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.35);
}
</style>
