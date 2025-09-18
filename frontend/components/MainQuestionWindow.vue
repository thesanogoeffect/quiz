<template><!-- Container now has margin auto for centering -->
<v-sheet class="d-flex justify-center">
    <v-container class="d-flex flex-column justify-start" v-if="questionStore.getCurrentQuestion">
      <GuessQuestionWindow
      class="flex-shrink-1 flex-grow-1"
      
        v-if="!questionStore.reviewMode"
      ></GuessQuestionWindow>
      <ReviewQuestionWindow class="flex-shrink-1 flex-grow-1" v-if="questionStore.reviewMode"></ReviewQuestionWindow>
      <QuestionNavigation class="flex-grow-1"></QuestionNavigation>
    </v-container>
    <v-container class="d-flex flex-column justify-center align-center" v-else>
    <v-progress-circular
      color="primary"
      indeterminate
    ></v-progress-circular>
    </v-container>
  </v-sheet>
</template>

<script>
import { defineComponent, computed } from "vue";
import { useQuestionStore } from "#imports";
import GuessQuestionWindow from "./GuessQuestionWindow.vue";
import ReviewQuestionWindow from "./ReviewQuestionWindow.vue";
import QuestionNavigation from "./QuestionNavigation.vue";
import { useDisplay } from "#imports";

export default defineComponent({
  name: "MainQuestionWindow",
  components: {
    GuessQuestionWindow,
    ReviewQuestionWindow,
    QuestionNavigation,
  },
  setup() {
    const questionStore = useQuestionStore();
    const display = useDisplay();

    return {
      questionStore,
    };
  },
});
</script>

<style>

  ::-webkit-scrollbar {
    -webkit-appearance: none;
    width: 7px;
  }

  ::-webkit-scrollbar-thumb {
    border-radius: 4px;
    background-color: rgba(0, 0, 0, .5);
    box-shadow: 0 0 1px rgba(255, 255, 255, .5);
  }
</style>


