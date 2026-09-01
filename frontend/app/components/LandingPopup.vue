<template>
  <v-dialog v-model="generalStore.landingPopup" max-width="800px" persistent scrollable>
    <v-card class="rounded-xl">
      <v-card-title class="headline text-center">Welcome</v-card-title>
      <v-card-text class="mx-4">
        <section class="my-3">
          <h3>Hi, welcome to the Intro to Psychology &amp; Technology Quiz! 👋</h3>
          <v-divider class="my-3"></v-divider>
          <p>
            This app is a student-made project for the <strong>Intro to P&amp;T</strong>
            course at TU/e Eindhoven. It uses questions written by previous years'
            students like me, and from the official OpenStax book. It is not an
            official part of the TU/e course, just a passion project.
          </p>
          <p class="mt-3">
            There are <strong>{{ questionCount }}</strong> questions across
            {{ chapterCount }} chapters - see the
            <NuxtLink :to="{ name: 'questions' }">question bank</NuxtLink> for the
            breakdown. 👀
          </p>
        </section>

        <section class="my-3">
          <h3>Disclaimer</h3>
          <v-divider class="my-2"></v-divider>
          <p>
            ⚠️ <strong>I am not responsible for any mistakes or inaccuracies.</strong> ⚠️
          </p>
          <p>
            Some questions <b>might be incorrect</b> - AI was used to process them,
            so please stay vigilant.
            <br />
            <b>If anything seems out of place, flag it</b> with the flag button.
          </p>
        </section>

        <v-container class="text-center my-3">
          <v-btn color="primary" @click="closeDialog">Sounds Good</v-btn>
        </v-container>

        <section class="my-3 text-center">
          <h3>
            If you have any feedback or want to support the project,<br />
            check the <NuxtLink :to="{ name: 'about' }">About</NuxtLink> page! ❤️
          </h3>
          <p class="mt-4">Happy quizzing! <br /> Jakub</p>
        </section>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useGeneralStore } from "~/stores/generalstore";
import { useQuestionStore } from "#imports";

const generalStore = useGeneralStore();
const questionStore = useQuestionStore();

const questionCount = computed(() => questionStore.getTotalQuestions || "…");
const chapterCount = computed(() => questionStore.getAllChapters.length || "…");

const closeDialog = () => {
  generalStore.toggleLandingPopup();
};

onMounted(() => {
  generalStore.checkLandingPopup();
});
</script>

<style scoped>
.headline {
  font-size: 1.5rem;
  font-weight: bold;
}
</style>
