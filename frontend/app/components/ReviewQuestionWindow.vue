<template>
  <!-- Card for the whole question -->
  <v-card
    class="rounded-xl d-flex flex-column justify-start"
    elevation="2"
    :style="{ backgroundColor: questionAreaBackgroundColor }"
  >
    <!-- Question title area -->
    <v-card
      class="rounded-lg flex-shrink-1"
      elevation="2"
      :style="{ backgroundColor: questionTitleBackgroundColor }"
    >
      <v-card-text>
        <p class="question-text text-center align-center">
          {{
            questionStore.currentlyReviewedQuestion
              ? questionStore.currentlyReviewedQuestion.question_title
              : ""
          }}
        </p>
      </v-card-text>
    </v-card>

    <v-divider></v-divider>

    <!-- Answer options -->
    <!-- Answer options -->
    <v-card
      class="ma-1 d-flex flex-column flex-shrink-1 flex-grow-1 justify-center"
      elevation="0"
      :style="{ backgroundColor: answerAreaBackgroundColor }"
    >
      <v-card
        v-for="(option, index) in answerOptions"
        :key="index"
        class="answer-card ma-1 rounded-pill d-flex justify-start align-center flex-shrink-1"
        :style="answerCardBackgroundColor(index)"
        elevation="1"
      >
        <v-btn class="ml-3" text color="primary">
          {{ option.label }}
        </v-btn>
        <p class="answer-text ma-2 flex-shrink-1">{{ option.text }}</p>
      </v-card>
    </v-card>
  </v-card>
</template>

<script>
import { defineComponent, computed } from "vue";
import { useQuestionStore } from "#imports";

export default defineComponent({
  name: "ReviewQuestionWindow",
  setup() {
    const questionStore = useQuestionStore();
    const theme = useTheme();
    const isMobile = computed(() => display.mobile);

    const answerFontSize = computed(() => (isMobile.value ? "1rem" : "1.1rem"));
    const questionFontSize = computed(() =>
      isMobile.value ? "1.1rem" : "1.2rem"
    );

    const answerOptions = computed(() => {
      if (!questionStore.currentlyReviewedQuestion) {
        return [];
      }
      return questionStore.currentlyReviewedQuestion.answers.map(
        (answer, index) => ({
          label: String.fromCharCode(65 + index), // A, B, C, D...
          text: answer,
        })
      );
    });

    const answerAreaBackgroundColor = computed(() =>
      theme.global.name.value === "light" ? "#d68a46" : "#6e4a42"
    );
    const questionAreaBackgroundColor = computed(() =>
      theme.global.name.value === "light" ? "#d68a46" : "#282828"
    );
    const questionTitleBackgroundColor = computed(() =>
      theme.global.name.value === "light" ? "#fdf2ea" : "#282828"
    );

    const isCorrectAnswer = (index) => {
      return (
        index === questionStore.currentlyReviewedQuestion.correct_answer_index
      );
    };

    const isIncorrectGuess = (index) => {
      return (
        index === questionStore.currentlyReviewedQuestion.guessed_index &&
        index !== questionStore.currentlyReviewedQuestion.correct_answer_index
      );
    };

    const isCorrectGuess = (index) => {
      return (
        index === questionStore.currentlyReviewedQuestion.guessed_index &&
        index === questionStore.currentlyReviewedQuestion.correct_answer_index
      );
    };

    const answerCardBackgroundColor = (index) => {
      if (
        isCorrectAnswer(index) &&
        !questionStore.currentlyReviewedQuestion.skipped
      ) {
        return { backgroundColor: "#4caf50", color: "white" }; // Success green
      }
      if (
        isCorrectAnswer(index) &&
        questionStore.currentlyReviewedQuestion.skipped
      ) {
        return { backgroundColor: "#c8e6c9", color: "black" }; // Light green for skipped correct answers
      }
      if (isIncorrectGuess(index)) {
        return { backgroundColor: "#ff9800", color: "white" }; // Warning color
      }
      return {
        backgroundColor: theme.global.name.value === "light" ? "#fdf2ea" : "#282828",
      };
    };

    return {
      questionStore,
      answerOptions,
      answerFontSize,
      questionFontSize,
      isCorrectAnswer,
      isIncorrectGuess,
      isCorrectGuess,
      answerAreaBackgroundColor,
      questionAreaBackgroundColor,
      questionTitleBackgroundColor,
      answerCardBackgroundColor, // Ensure you return the method here
    };
  },
});
</script>

<style scoped>
.question-text {
  font-size: 1.25em;
  text-align: center;
  max-height: 5em; /* Limits the maximum height of the text */
  overflow-y: auto; /* Adds a scrollbar if the text exceeds the max height */
  -webkit-overflow-scrolling: auto;
}

.answer-card {
  cursor: default;
  transition: all 0.3s ease;
  min-height: 9vh; /* 10% of the viewport height */
  font-size: 1.05em;
}

.answer-text {
  max-height: 3em; /* Adjust based on how many lines you want */
  overflow-y: auto; /* Adds a scrollbar if the text exceeds the max height */
  white-space: normal; /* Wrap the text if it exceeds the line length */
  -webkit-overflow-scrolling: auto;
}

/* Styling for different answer states */
.correct-answer {
  background-color: #4caf50; /* Vuetify success color */
  color: white;
}

.skipped-correct-answer {
  background-color: #c8e6c9; /* Light green */
  color: black;
}

.incorrect-guess {
  background-color: #ff9800; /* Vuetify warning color */
  color: white;
}

.correct-guess {
  background-color: #4caf50; /* Vuetify success color */
  color: white;
}

</style>