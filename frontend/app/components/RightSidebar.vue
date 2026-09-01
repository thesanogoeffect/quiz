<template>
  <v-container v-if="currentQuestion" class="py-3">
    <v-card
      class="stats-container pa-3 rounded-xl"
      flat
      :style="{ backgroundColor: sidebarCardsColor }"
    >
      <h2 class="mb-2 text-center">Question Info</h2>
      <v-divider class="mb-3"></v-divider>

      <div class="info-row">
        <v-icon color="info" size="small">mdi-pound</v-icon>
        <span>ID: {{ currentQuestionId }}</span>
      </div>

      <div class="info-row">
        <v-icon color="primary" size="small">mdi-book</v-icon>
        <span>Chapter: {{ chapterLabel }}</span>
      </div>

      <div class="info-row">
        <v-icon color="secondary" size="small">mdi-book-open-page-variant</v-icon>
        <span>Source: {{ sourceLabel }}</span>
      </div>
    </v-card>

    <v-expansion-panels v-if="questionStore.getReviewMode" class="mt-4">
      <v-expansion-panel
        class="rounded-lg"
        title="Explanation"
        :style="{ backgroundColor: sidebarCardsColor }"
      >
        <v-expansion-panel-text>
          <!-- description_llm ships as small HTML fragments (<p>, <b>, <ul>).
               Rendered through a tag allowlist so a bad pipeline run cannot
               inject markup into a student's browser. -->
          <div class="explanation" v-html="llmExplanation"></div>
          <p class="text-caption text-medium-emphasis mt-3 mb-0">
            Written by an LLM - it can be wrong. Flag the question if it looks off.
          </p>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script setup>
import { computed } from "vue";
import { useTheme } from "vuetify";
import { useQuestionStore } from "#imports";
import { sanitizeHtml } from "~/utils/sanitizeHtml";

const questionStore = useQuestionStore();
const theme = useTheme();

const sidebarCardsColor = computed(() =>
  theme.global.name.value === "light" ? "#fdf2ea" : "#282828"
);

const currentQuestion = computed(() =>
  questionStore.getReviewMode
    ? questionStore.getCurrentlyReviewedQuestion
    : questionStore.getCurrentQuestion
);

const currentQuestionId = computed(() => currentQuestion.value?.id ?? "-");

const llmExplanation = computed(() => {
  const raw = currentQuestion.value?.description_llm;
  return raw ? sanitizeHtml(raw) : "No explanation available.";
});

const sourceLabel = computed(() => currentQuestion.value?.source || "N/A");
const chapterId = computed(() => currentQuestion.value?.chapter_id);
const chapterLabel = computed(() => {
  const id = chapterId.value;
  if (id === undefined || id === null) return "Unknown";
  const name = questionStore.getChapterById(id);
  return name ? `${id} - ${name}` : String(id);
});
</script>

<style scoped>
.stats-container {
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h2 {
  font-weight: bold;
  font-size: 1.35rem;
}

.info-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 10px;
  overflow-wrap: anywhere;
}

.explanation :deep(p) {
  margin-bottom: 8px;
}

.explanation :deep(ul),
.explanation :deep(ol) {
  padding-left: 20px;
  margin-bottom: 8px;
}
</style>
