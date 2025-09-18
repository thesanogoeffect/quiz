<template>
  <!-- Card for the whole question -->
  <v-card class="rounded-xl d-flex flex-column justify-start" elevation="2"
  :style="{ backgroundColor: questionAreaBackgroundColor}">
    <!-- Question title area -->
    <v-card class="rounded-lg flex-shrink-1" elevation="2" :style="{ backgroundColor: questionTitleBackgroundColor}">
      <v-card-text>
        <p class="question-text text-center overflow-y-auto align-center">
          {{
            questionStore.getCurrentQuestion
              ? questionStore.getCurrentQuestion.question_title
              : ""
          }}
        </p>
      </v-card-text>
    </v-card>

    <v-divider></v-divider>

    <!-- Answer options -->
    <v-card
      class="ma-1 d-flex flex-column flex-shrink-1 flex-grow-1 justify-center"
      elevation="0" :style="{ backgroundColor: answerAreaBackgroundColor}"
    >
      <v-card
        v-for="(option, index) in answerOptions"
        :key="index"
        class="answer-card ma-1 rounded-pill d-flex justify-start align-center flex-shrink-1"
        :style="{ backgroundColor: answerCardBackgroundColor}"
        @click="handleAnswer(index)"
        elevation="1"
      >
        <v-btn class="ml-3" text color="primary">
          {{ option.label }}
        </v-btn>
        <p class="answer-text overflow-y-auto ma-2 flex-shrink-1">{{ option.text }}</p>
      </v-card>
    </v-card>
  </v-card>
</template>

<script>
import { defineComponent, computed } from "vue";
import { useQuestionStore } from "#imports";
import "@/assets/global.css";

export default defineComponent({
  name: "GuessQuestionWindow",
  setup() {
    const questionStore = useQuestionStore();
    const theme = useTheme();
    const answerCardBackgroundColor = computed(() =>
      theme.global.name.value==="light" ? "#fdf2ea" : "#282828"
    );
    const answerAreaBackgroundColor = computed(() =>
      theme.global.name.value=== "light" ? "#d68a46" : "#6e4a42"
    );
    const questionAreaBackgroundColor = computed(() =>
      theme.global.name.value === "light" ? "#d68a46" : "#282828"
      // so far #c8c8c7 was the best
    );
    const questionTitleBackgroundColor = computed(() =>
      theme.global.name.value === "light" ? "#fdf2ea" : "#282828"
    );


    const answerOptions = computed(() => {
      const currentQuestion = questionStore.getCurrentQuestion;
      if (!currentQuestion) {
        return [];
      }
      return currentQuestion.answers.map((answer, index) => ({
        label: String.fromCharCode(65 + index), // Convert index to letter (A, B, C, D, ...)
        text: answer,
      }));
    });

    const handleAnswer = async (index) => {
      await questionStore.answerCurrentQuestion(index);
    };

    return {
      questionStore,
      answerOptions,
      handleAnswer,
      answerCardBackgroundColor,
      answerAreaBackgroundColor,
      questionAreaBackgroundColor,
      questionTitleBackgroundColor,
    };
  },
});
</script>

<style scoped>
.question-text {
  font-size: 1.25em;
  text-align: center;
  max-height: 5em; /* Limits the maximum height of the text */
  -webkit-overflow-scrolling: auto;
}

.answer-card {
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 9vh; /* 10% of the viewport height */
  font-size: 1.05em;
  
}

.answer-text {
  max-height: 3em; /* Adjust based on how many lines you wamt */
  -webkit-overflow-scrolling: auto;
}
</style>