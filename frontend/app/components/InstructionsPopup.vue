<template>
  <v-dialog v-model="generalStore.instructionsPopup" max-width="800px">
    <v-card class="rounded-xl">
      <v-card-title class="headline text-center">Help</v-card-title>
      <v-card-text class="mx-4">
        <h3><strong>Instructions:</strong></h3>
        <ol>
          <li>
            Use the left-right arrows (or A and D keys) to navigate through
            questions.
          </li>
          <li>
            The right arrow works as a "Skip" button if you don't know the
            answer. You only get 3 skips, but you might earn more by doing well.
          </li>
          <li>
            Flag questions that seem incorrect so they can be reviewed by an LLM
            or others.
          </li>
          <li>
            You can upvote/downvote questions to improve question quality for
            everyone.
          </li>
        </ol>

        <h3><strong>Top menu:</strong></h3>
        <ul>
          <li>You can filter questions by chapters or by source.</li>
          <li>
            There is an About page, where you can find more info and how to
            contact me if needed.
          </li>
          <li>
            The dark mode is under construction, but you can try it in the top
            menu!
          </li>
          <li>
            You can toggle the stats/info sidebars by clicking the icons on the
            sides.
          </li>
        </ul>
        <v-container class="text-center">
          <v-btn color="primary" @click="closeDialog">Got it</v-btn>
          <br />
        </v-container>
        <p>
          Enjoy! <br />
          Jakub
        </p>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
  
  <script>
import { ref, onMounted } from "vue";
import { useGeneralStore } from "~/stores/generalstore";
import { useDisplay } from "#imports";

export default {
  name: "InstructionsPopup",
  setup() {
    const generalStore = useGeneralStore();
    const display = useDisplay();
    const mdAndUp = computed(() => display.mdAndUp);

    const closeDialog = () => {
      generalStore.toggleInstructionsPopup();
    };

    return {
      closeDialog,
      generalStore,
      mdAndUp,
    };
  },
};
</script>
  
  <style scoped>
.notice {
  font-size: 0.8rem;
  color: gray;
}
</style>
  