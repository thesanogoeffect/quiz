<template>
  <!-- Card for the whole question -->
  <v-card
    class="rounded-xl d-flex flex-column"
    elevation="2"
    :style="{ backgroundColor: questionAreaBackgroundColor }"
  >
    <!-- Question title area -->
    <v-card
      class="rounded-lg flex-shrink-0"
      elevation="2"
      :style="{ backgroundColor: questionTitleBackgroundColor }"
    >
      <v-card-text>
        <!-- Correct/incorrect was signalled by colour alone, which is invisible
             to colour-blind users and to anyone using a screen reader. -->
        <div class="d-flex align-center justify-center ga-2 mb-2" aria-live="polite">
          <v-icon :color="outcome.color" size="small">{{ outcome.icon }}</v-icon>
          <span class="text-body-2 font-weight-medium" :class="outcome.textClass">
            {{ outcome.label }}
          </span>
        </div>
        <h1 class="question-text text-center">
          {{ reviewed ? reviewed.question_title : "" }}
        </h1>
      </v-card-text>
    </v-card>

    <v-divider></v-divider>

    <!-- Answer options -->
    <div
      class="answer-area pa-1 d-flex flex-column justify-center ga-2"
      :style="{ backgroundColor: answerAreaBackgroundColor }"
    >
      <div
        v-for="(option, index) in answerOptions"
        :key="index"
        class="answer-card rounded-pill d-flex align-center"
        :style="answerCardStyle(index)"
      >
        <span class="answer-label" :style="labelStyle(index)">{{ option.label }}</span>
        <span class="answer-text">{{ option.text }}</span>
        <!-- The words are hidden on phones, so the label carries them for
             screen readers regardless of viewport. -->
        <span
          v-if="marker(index)"
          class="answer-marker"
          :aria-label="marker(index).text"
        >
          <span aria-hidden="true">{{ marker(index).symbol }}</span>
          <span class="answer-marker__text" aria-hidden="true">{{
            marker(index).text
          }}</span>
        </span>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from "vue";
import { useTheme } from "vuetify";
import { useQuestionStore } from "#imports";

const questionStore = useQuestionStore();
const theme = useTheme();
const isLight = computed(() => theme.global.name.value === "light");

const reviewed = computed(() => questionStore.getCurrentlyReviewedQuestion);

const answerOptions = computed(() => {
  if (!reviewed.value) return [];
  return reviewed.value.answers.map((answer, index) => ({
    label: String.fromCharCode(65 + index), // A, B, C, D...
    text: answer,
  }));
});

const answerAreaBackgroundColor = computed(() =>
  isLight.value ? "#d68a46" : "#6e4a42"
);
const questionAreaBackgroundColor = computed(() =>
  isLight.value ? "#d68a46" : "#282828"
);
const questionTitleBackgroundColor = computed(() =>
  isLight.value ? "#fdf2ea" : "#282828"
);

const isCorrectAnswer = (index) =>
  !!reviewed.value && index === reviewed.value.correct_answer_index;

const isGuess = (index) =>
  !!reviewed.value &&
  reviewed.value.guessed_index !== null &&
  index === reviewed.value.guessed_index;

const outcome = computed(() => {
  const q = reviewed.value;
  if (!q) return { label: "", icon: "", color: "", textClass: "" };
  if (q.skipped) {
    return {
      label: "Skipped - here is the answer",
      icon: "$skipNextCircleOutline",
      color: "warning",
      textClass: "text-warning",
    };
  }
  if (q.guessed_index === q.correct_answer_index) {
    return {
      label: "Correct!",
      icon: "$checkCircle",
      color: "success",
      textClass: "text-success",
    };
  }
  return {
    label: "Not quite",
    icon: "$closeCircle",
    color: "error",
    textClass: "text-error",
  };
});

const answerCardStyle = (index) => {
  if (isCorrectAnswer(index)) {
    return reviewed.value?.skipped
      ? { backgroundColor: "#c8e6c9", color: "#1b5e20" }
      : { backgroundColor: "#2e7d32", color: "#ffffff" };
  }
  if (isGuess(index)) {
    return { backgroundColor: "#c62828", color: "#ffffff" };
  }
  return {
    backgroundColor: isLight.value ? "#fdf2ea" : "#282828",
  };
};

const labelStyle = (index) =>
  isCorrectAnswer(index) || isGuess(index)
    ? { backgroundColor: "rgba(255,255,255,0.25)", color: "inherit" }
    : {};

// A marker so the result never depends on colour alone. The symbol stays
// visible on phones where the label text does not fit.
const marker = (index) => {
  if (isCorrectAnswer(index)) {
    return isGuess(index)
      ? { symbol: "✓", text: "Your answer" }
      : { symbol: "✓", text: "Correct answer" };
  }
  if (isGuess(index)) return { symbol: "✗", text: "Your answer" };
  return null;
};
</script>

<style scoped>
.question-text {
  font-size: 1.2rem;
  font-weight: 500;
  line-height: 1.45;
  text-align: center;
  margin: 0;
}

.answer-area {
  flex: 0 0 auto;
}

.answer-card {
  width: 100%;
  min-height: 64px;
  padding: 12px 20px 12px 12px;
  gap: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.answer-label {
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background-color: #c81919;
  color: #fff;
  font-weight: 600;
}

.answer-text {
  flex: 1 1 auto;
  line-height: 1.4;
  white-space: normal;
  overflow-wrap: anywhere;
}

.answer-marker {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  opacity: 0.95;
  white-space: nowrap;
}

@media (max-width: 599px) {
  .question-text {
    font-size: 1.05rem;
  }
  .answer-card {
    font-size: 0.95rem;
    padding: 10px 14px 10px 10px;
  }
  /* Keep the ✓ / ✗ symbol, drop only the words. */
  .answer-marker {
    font-size: 1.05rem;
  }
  .answer-marker__text {
    display: none;
  }
}
</style>
