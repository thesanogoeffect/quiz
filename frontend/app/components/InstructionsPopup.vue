<template>
  <v-dialog v-model="generalStore.instructionsPopup" max-width="800px" scrollable>
    <v-card class="rounded-xl">
      <v-card-title class="headline text-center">Help</v-card-title>
      <v-card-text class="mx-4">
        <h3><strong>Playing</strong></h3>
        <ul>
          <li>Click an answer, or press <kbd>1</kbd>–<kbd>4</kbd> to pick one.</li>
          <li>
            <kbd>←</kbd> / <kbd>A</kbd> steps back through the questions you have
            already answered, <kbd>→</kbd> / <kbd>D</kbd> moves forward.
          </li>
          <li>
            On a new question the right arrow is a <strong>Skip</strong>. You start
            with 3 skips and earn them back by answering correctly.
          </li>
        </ul>

        <h3 class="mt-4"><strong>Helping out</strong></h3>
        <ul>
          <li>
            Use the flag button to report a question that looks wrong, so it can be
            reviewed.
          </li>
          <li>
            Upvote and downvote to show which questions are worth keeping.
          </li>
        </ul>

        <h3 class="mt-4"><strong>Top menu</strong></h3>
        <ul>
          <li>Filter the questions by chapter or by source.</li>
          <li>Switch between light and dark mode - your choice is remembered.</li>
          <li>
            The question bank page shows how many questions exist per chapter.
          </li>
          <li>Toggle the stats and question-info panels from the side icons.</li>
        </ul>

        <v-container class="text-center">
          <v-btn color="primary" @click="closeDialog">Got it</v-btn>
        </v-container>
        <p class="text-center">
          Enjoy! <br />
          Jakub
        </p>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useGeneralStore } from "~/stores/generalstore";

const generalStore = useGeneralStore();

const closeDialog = () => {
  generalStore.toggleInstructionsPopup();
};
</script>

<style scoped>
kbd {
  padding: 1px 6px;
  border: 1px solid rgba(128, 128, 128, 0.5);
  border-radius: 4px;
  font-size: 0.85em;
  font-family: inherit;
}

ul {
  padding-left: 20px;
}

li {
  margin-bottom: 6px;
}
</style>
