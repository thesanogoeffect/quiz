<template>
  <v-container class="d-flex justify-center">
    <v-btn
      icon="mdi-arrow-left"
      :disabled="!canGoLeft"
      @click="useLeftArrow"
      class="navigation-button mt-2 d-flex-shrink-1"
    >
    </v-btn>
    <InteractionsPill class="mx-6"/>
    <v-btn
      icon="mdi-arrow-right"
      :disabled="!canGoRight"
      @click="useRightArrow"
      class="navigation-button mt-2 d-flex-shrink-1"
    >
    </v-btn>
  </v-container>
</template>

<script setup>
import { useQuestionStore } from "#imports";
import { useQuestionStatsStore } from "#imports";
import { ref, onMounted, onBeforeUnmount, computed } from "vue";
import InteractionsPill from "./InteractionsPill.vue";

const questionStore = useQuestionStore();
const clickBlocked = ref(false); // Flag to block clicks

const canGoLeft = computed(() => {
  if (questionStore.getReviewMode) {
    return questionStore.getCurrentReviewPosition > 0;
  } else {
    return questionStore.getAnswerHistoryLength > 0;
  }
});

const canGoRight = computed(() => {
  return questionStore.getReviewMode
    ? true
    : questionStore.getSkipsRemaining > 0;
});

function blockClickTemporarily() {
  clickBlocked.value = true;
  setTimeout(() => {
    clickBlocked.value = false;
  }, 300); 
}

const processingAnswer = computed(() => {
  return questionStore.getProcessingAnswer;
});

async function useLeftArrow() {
  if (clickBlocked.value || processingAnswer.value) return; // Prevent action if click is blocked
  blockClickTemporarily();

  if (questionStore.getReviewMode) {
    if (questionStore.getCurrentReviewPosition > 0) {
      await questionStore.previousReviewedQuestion();
    }
  } else {
    await questionStore.toggleReviewMode();
  }
}

async function useRightArrow() {
  if (clickBlocked.value || processingAnswer.value) return; // Prevent action if click is blocked
  blockClickTemporarily();

  if (questionStore.getReviewMode) {
    if (questionStore.getCurrentReviewPosition === questionStore.getAnswerHistoryLength - 1) {
      // this means we are at the end of the review mode and therefore we trigger next question guess again
      await questionStore.toggleReviewMode();
    } else {
      await questionStore.nextReviewedQuestion();
    }
  } else {
    questionStore.skipQuestion();
  }
}

// Handle arrow key presses
async function handleKeydown(event) {
  if ((event.key === 'ArrowLeft' || event.key === 'a' || event.key === 'A') && canGoLeft.value) {
    event.preventDefault(); // prevent default arrow key behavior
    await useLeftArrow();
  } else if ((event.key === 'ArrowRight' || event.key === 'd' || event.key === 'D') && canGoRight.value) {
    event.preventDefault(); // prevent default arrow key behavior
    await useRightArrow();
  }
}

// Mount the keydown event listener
onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});

// Remove the keydown event listener when the component is unmounted
onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.navigation-button {
  background-color: #C81919;
  color: white;
}
</style>