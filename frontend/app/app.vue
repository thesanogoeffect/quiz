<template>
  <div>
    <NuxtPage />
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from "vue";
import { useQuestionStore } from "#imports";
import { useQuestionStatsStore } from "#imports";

const questionStore = useQuestionStore();
const questionStatsStore = useQuestionStatsStore();

// The pending counter updates for the question on screen are only flushed when
// the user navigates. Without this, the last question of every session - and
// any vote cast on it - was never recorded.
function flushPendingStats() {
  const id = questionStore.reviewMode
    ? questionStore.currentlyReviewedQuestion?.id
    : questionStore.currentQuestion?.id;
  if (id === undefined || id === null) return;
  questionStatsStore.saveInteractionsCacheToLocalStorage();
  questionStatsStore.incrementSpecificQuestionFields(id);
}

function onPageHide() {
  if (document.visibilityState === "hidden") flushPendingStats();
}

onMounted(async () => {
  // Must run before setUp(): the first question's increment baseline is built
  // from these caches, so loading them afterwards double-counted votes.
  questionStatsStore.loadInteractionsCacheFromLocalStorage();
  await questionStore.setUp();

  document.addEventListener("visibilitychange", onPageHide);
  window.addEventListener("pagehide", flushPendingStats);
});

onBeforeUnmount(() => {
  document.removeEventListener("visibilitychange", onPageHide);
  window.removeEventListener("pagehide", flushPendingStats);
});
</script>
