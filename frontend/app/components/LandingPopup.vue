<template>
  <v-dialog
    v-model="generalStore.landingPopup"
    max-width="800px"
    persistent
  >
    <v-card class="rounded-xl">
      <v-card-title class="headline text-center">Welcome</v-card-title>
      <v-card-text class="mx-4">
        <section class="my-3">
          <h3>Hi, welcome to the Intro to Psychology & Technology Quiz! 👋</h3>
          <v-divider class="my-3"></v-divider>
          <p>
            This app is a student-made project for the <strong>Intro to P&T</strong> course at the TU/e Eindhoven.
            It uses questions made by previous years' students like me, and from the official OpenStax book.
          </p>
          <p>
            It is not an official part of the TU/e course, just a passion project.
            I am not responsible for any mistakes or inaccuracies.
          </p>
          <p>
            You can find out how many questions there currently are <NuxtLink to="https://ipt-quiz.streamlit.app/" target="_blank">here</NuxtLink> 👀
          </p>
        </section>

        <section class="my-3">
          <h4>Disclaimer:</h4>
          <v-divider class="my-2"></v-divider>
          <p>
            Some questions <b>might be incorrect</b> as I used AI when I was processing them - please stay critical.
            <br> <b>If anything seems weird, please let me know</b>.
          </p>
          <p>
            You can upvote, downvote, and flag incorrect questions, <b>your opinions and feedback are even more valuable</b> 🙏
          </p>
        </section>

        <v-container class="text-center my-3">
          <v-btn color="primary" @click="closeDialog">Sounds Good</v-btn>
        </v-container>

        <section class="my-3 text-center">
          <h3>
            If you have any feedback or want to support the project,<br> check the
            <NuxtLink to="/about">About</NuxtLink> page! ❤️
          </h3>
          <p class="mt-4">Happy quizzing! <br /> Jakub </p>
        </section>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import { useGeneralStore } from "~/stores/generalstore";
import { useDisplay } from "#imports";
export default {
  name: "LandingPopup",
  setup() {
    const generalStore = useGeneralStore();
    const display = useDisplay();
    const mdAndUp = computed(() => display.mdAndUp);
    const mobile = computed(() => display.mobile);

    const closeDialog = () => {
      generalStore.toggleLandingPopup();
    };

    onMounted(() => {
      generalStore.checkLandingPopup();
      const urlParams = new URLSearchParams(window.location.search);
    });

    return {
      closeDialog,
      generalStore,
      mdAndUp,
      mobile,
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