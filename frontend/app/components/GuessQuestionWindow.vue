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
        <h1 class="question-text text-center">
          {{ currentQuestion ? currentQuestion.question_title : "" }}
        </h1>
      </v-card-text>
    </v-card>

    <v-divider></v-divider>

    <!-- Answer options -->
    <div
      class="answer-area pa-1 d-flex flex-column justify-center ga-2"
      :style="{ backgroundColor: answerAreaBackgroundColor }"
      role="group"
      aria-label="Answer options"
    >
      <button
        v-for="(option, index) in answerOptions"
        :key="index"
        type="button"
        class="answer-card rounded-pill d-flex align-center text-left"
        :style="{ backgroundColor: answerCardBackgroundColor }"
        :disabled="questionStore.getProcessingAnswer"
        @click="handleAnswer(index)"
      >
        <span class="answer-label">{{ option.label }}</span>
        <span class="answer-text">{{ option.text }}</span>
      </button>
    </div>
  </v-card>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount } from "vue";
import { useTheme } from "vuetify";
import { useQuestionStore } from "#imports";
import "@/assets/global.css";

const questionStore = useQuestionStore();
const theme = useTheme();
const isLight = computed(() => theme.global.name.value === "light");

const answerCardBackgroundColor = computed(() =>
  isLight.value ? "#fdf2ea" : "#282828"
);
const answerAreaBackgroundColor = computed(() =>
  isLight.value ? "#d68a46" : "#6e4a42"
);
const questionAreaBackgroundColor = computed(() =>
  isLight.value ? "#d68a46" : "#282828"
);
const questionTitleBackgroundColor = computed(() =>
  isLight.value ? "#fdf2ea" : "#282828"
);

const currentQuestion = computed(() => questionStore.getCurrentQuestion);

const answerOptions = computed(() => {
  if (!currentQuestion.value) return [];
  return currentQuestion.value.answers.map((answer, index) => ({
    label: String.fromCharCode(65 + index), // Convert index to letter (A, B, C, D, ...)
    text: answer,
  }));
});

const handleAnswer = async (index) => {
  if (questionStore.getProcessingAnswer || questionStore.getReviewMode) return;
  await questionStore.answerCurrentQuestion(index);
};

// Answer straight from the keyboard with 1-4 or A-D. The navigation component
// owns the arrow/A-D-for-navigation keys, so only digits and the answer letters
// are handled here, and only while a question is actually on screen.
function handleKeydown(event) {
  if (event.metaKey || event.ctrlKey || event.altKey) return;
  const target = event.target;
  if (
    target instanceof HTMLElement &&
    (target.isContentEditable ||
      ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName))
  ) {
    return;
  }
  if (document.querySelector(".v-overlay--active")) return; // a dialog is open
  if (questionStore.getReviewMode || questionStore.getProcessingAnswer) return;

  const count = answerOptions.value.length;
  if (!count) return;

  let index = -1;
  if (/^[1-9]$/.test(event.key)) index = Number(event.key) - 1;
  else if (/^[a-dA-D]$/.test(event.key)) {
    // A and D are the navigation keys; B and C are unambiguous.
    if (/^[bcBC]$/.test(event.key)) index = event.key.toLowerCase().charCodeAt(0) - 97;
  }

  if (index >= 0 && index < count) {
    event.preventDefault();
    handleAnswer(index);
  }
}

onMounted(() => window.addEventListener("keydown", handleKeydown));
onBeforeUnmount(() => window.removeEventListener("keydown", handleKeydown));
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

/* Answers used to be clamped to 3em with a hidden scrollbar, which silently cut
   off ~10% of the options in the question set. They grow instead. */
.answer-card {
  width: 100%;
  min-height: 64px;
  padding: 12px 20px 12px 12px;
  gap: 12px;
  border: none;
  cursor: pointer;
  font: inherit;
  color: inherit;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.answer-card:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.25);
}

.answer-card:focus-visible {
  outline: 3px solid #1d1d1d;
  outline-offset: 2px;
}

.answer-card:disabled {
  cursor: default;
  opacity: 0.7;
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

@media (max-width: 599px) {
  .question-text {
    font-size: 1.05rem;
  }
  .answer-card {
    font-size: 0.95rem;
    padding: 10px 14px 10px 10px;
  }
}
</style>
