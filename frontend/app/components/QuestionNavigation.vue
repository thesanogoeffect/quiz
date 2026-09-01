<template>
  <div class="nav-row d-flex align-center justify-center ga-3 flex-wrap">
    <v-btn
      icon="mdi-arrow-left"
      :disabled="!canGoLeft || busy"
      :aria-label="leftLabel"
      :title="leftLabel"
      class="navigation-button"
      @click="useLeftArrow"
    ></v-btn>

    <InteractionsPill />

    <v-btn
      icon="mdi-arrow-right"
      :disabled="!canGoRight || busy"
      :aria-label="rightLabel"
      :title="rightLabel"
      class="navigation-button"
      @click="useRightArrow"
    ></v-btn>
  </div>
</template>

<script setup>
import { useQuestionStore } from "#imports";
import { ref, onMounted, onBeforeUnmount, computed } from "vue";
import InteractionsPill from "./InteractionsPill.vue";

const questionStore = useQuestionStore();
const clickBlocked = ref(false); // Flag to block clicks

const busy = computed(() => questionStore.getProcessingAnswer);

const canGoLeft = computed(() => {
  if (questionStore.getReviewMode) {
    return questionStore.getCurrentReviewPosition > 0;
  }
  return questionStore.getAnswerHistoryLength > 0;
});

const canGoRight = computed(() =>
  questionStore.getReviewMode ? true : questionStore.getSkipsRemaining > 0
);

const leftLabel = computed(() =>
  questionStore.getReviewMode ? "Previous reviewed question" : "Review previous answers"
);
const rightLabel = computed(() =>
  questionStore.getReviewMode
    ? "Next question"
    : `Skip this question (${questionStore.getSkipsRemaining} left)`
);

function blockClickTemporarily() {
  clickBlocked.value = true;
  setTimeout(() => {
    clickBlocked.value = false;
  }, 300);
}

async function useLeftArrow() {
  if (clickBlocked.value || busy.value) return; // Prevent action if click is blocked
  blockClickTemporarily();

  if (questionStore.getReviewMode) {
    if (questionStore.getCurrentReviewPosition > 0) {
      await questionStore.previousReviewedQuestion();
    }
  } else if (questionStore.getAnswerHistoryLength > 0) {
    await questionStore.toggleReviewMode();
  }
}

async function useRightArrow() {
  if (clickBlocked.value || busy.value) return; // Prevent action if click is blocked
  blockClickTemporarily();

  if (questionStore.getReviewMode) {
    if (
      questionStore.getCurrentReviewPosition ===
      questionStore.getAnswerHistoryLength - 1
    ) {
      // this means we are at the end of the review mode and therefore we trigger next question guess again
      await questionStore.toggleReviewMode();
    } else {
      await questionStore.nextReviewedQuestion();
    }
  } else {
    await questionStore.skipQuestion();
  }
}

// Handle arrow key presses
async function handleKeydown(event) {
  if (event.metaKey || event.ctrlKey || event.altKey) return;

  // Do not steal keys from a text field or from an open dialog - typing in the
  // filter search used to skip questions behind the modal.
  const target = event.target;
  if (
    target instanceof HTMLElement &&
    (target.isContentEditable ||
      ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName))
  ) {
    return;
  }
  if (document.querySelector(".v-overlay--active")) return;

  const key = event.key;
  if ((key === "ArrowLeft" || key === "a" || key === "A") && canGoLeft.value) {
    event.preventDefault(); // prevent default arrow key behavior
    await useLeftArrow();
  } else if (
    (key === "ArrowRight" || key === "d" || key === "D") &&
    canGoRight.value
  ) {
    event.preventDefault(); // prevent default arrow key behavior
    await useRightArrow();
  }
}

// Mount the keydown event listener
onMounted(() => {
  window.addEventListener("keydown", handleKeydown);
});

// Remove the keydown event listener when the component is unmounted
onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeydown);
});
</script>

<style scoped>
.nav-row {
  padding: 8px 0 4px;
}

.navigation-button {
  background-color: #c81919;
  color: white;
}

.navigation-button:disabled {
  opacity: 0.45;
}
</style>
