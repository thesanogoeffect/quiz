<template>
  <v-app>
    <v-app-bar color="primary" density="comfortable" flat>
      <v-btn
        icon="mdi-arrow-left"
        variant="text"
        aria-label="Back to the quiz"
        :to="{ name: 'index' }"
      ></v-btn>
      <v-toolbar-title>Question Bank</v-toolbar-title>
    </v-app-bar>

    <v-main>
      <v-container class="page">
        <div v-if="!loaded" class="text-center py-12">
          <v-progress-circular color="primary" indeterminate></v-progress-circular>
        </div>

        <template v-else>
          <div class="summary-grid mb-6">
            <v-card class="summary-card rounded-xl pa-4 text-center" flat>
              <div class="summary-number">{{ total }}</div>
              <div class="text-medium-emphasis">Questions</div>
            </v-card>
            <v-card class="summary-card rounded-xl pa-4 text-center" flat>
              <div class="summary-number">{{ chapters.length }}</div>
              <div class="text-medium-emphasis">Chapters covered</div>
            </v-card>
            <v-card class="summary-card rounded-xl pa-4 text-center" flat>
              <div class="summary-number">{{ averagePerChapter }}</div>
              <div class="text-medium-emphasis">Average per chapter</div>
            </v-card>
          </div>

          <h2 class="text-h6 mb-3">By chapter</h2>
          <v-card class="rounded-xl pa-4 mb-6" flat>
            <div v-for="row in chapters" :key="row.id" class="bar-row">
              <span class="bar-label">
                {{ row.id }}. {{ row.name }}
              </span>
              <div class="bar-track">
                <div
                  class="bar-fill"
                  :style="{ width: `${(row.count / maxChapterCount) * 100}%` }"
                ></div>
              </div>
              <span class="bar-count">{{ row.count }}</span>
            </div>
          </v-card>

          <h2 class="text-h6 mb-3">By source</h2>
          <v-card class="rounded-xl pa-4 mb-6" flat>
            <div v-for="row in sources" :key="row.name" class="bar-row">
              <span class="bar-label">{{ row.name }}</span>
              <div class="bar-track">
                <div
                  class="bar-fill"
                  :style="{ width: `${(row.count / maxSourceCount) * 100}%` }"
                ></div>
              </div>
              <span class="bar-count">{{ row.count }}</span>
            </div>
          </v-card>

          <h2 class="text-h6 mb-3">Chapter × source</h2>
          <v-card class="rounded-xl pa-4" flat>
            <div class="table-scroll">
              <table class="matrix">
                <thead>
                  <tr>
                    <th scope="col">Chapter</th>
                    <th v-for="s in sourceNames" :key="s" scope="col">{{ s }}</th>
                    <th scope="col">Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in chapters" :key="row.id">
                    <th scope="row">{{ row.id }}. {{ row.name }}</th>
                    <td
                      v-for="s in sourceNames"
                      :key="s"
                      :class="{ zero: !matrix[row.id]?.[s] }"
                    >
                      {{ matrix[row.id]?.[s] || 0 }}
                    </td>
                    <td class="total">{{ row.count }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p class="text-caption text-medium-emphasis mt-3 mb-0">
              Empty cells mean that chapter has no questions from that source, so
              filtering on both together returns nothing.
            </p>
          </v-card>
        </template>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useQuestionStore } from "#imports";

useHead({ title: "Question Bank · Intro to P&T Quiz" });

const questionStore = useQuestionStore();

// app.vue loads the set on every route, but a deep link lands here before that
// finishes - setUp() is idempotent, so just make sure it has run.
onMounted(() => questionStore.setUp());

const loaded = computed(() => questionStore.getTotalQuestions > 0);

// Everything below is derived from l3.json, which the app already loads, so
// this page needs no backend of its own.
const visibleQuestions = computed(() =>
  questionStore.all_questions.filter(
    (q) => !questionStore.BANLIST_CHAPTERS.includes(q.chapter_id)
  )
);

const total = computed(() => visibleQuestions.value.length);

const chapters = computed(() => {
  const counts = new Map();
  for (const q of visibleQuestions.value) {
    counts.set(q.chapter_id, (counts.get(q.chapter_id) || 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([id, count]) => ({
      id,
      count,
      name: questionStore.getChapterById(id) || "Unknown chapter",
    }));
});

const sources = computed(() => {
  const counts = new Map();
  for (const q of visibleQuestions.value) {
    counts.set(q.source, (counts.get(q.source) || 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([name, count]) => ({ name, count }));
});

const sourceNames = computed(() => sources.value.map((s) => s.name));

const matrix = computed(() => {
  const m = {};
  for (const q of visibleQuestions.value) {
    (m[q.chapter_id] ||= {})[q.source] = (m[q.chapter_id][q.source] || 0) + 1;
  }
  return m;
});

const maxChapterCount = computed(() =>
  Math.max(1, ...chapters.value.map((c) => c.count))
);
const maxSourceCount = computed(() =>
  Math.max(1, ...sources.value.map((s) => s.count))
);
const averagePerChapter = computed(() =>
  chapters.value.length
    ? (total.value / chapters.value.length).toFixed(1)
    : "0"
);
</script>

<style scoped>
.page {
  max-width: 900px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.summary-card {
  border: 1px solid rgba(128, 128, 128, 0.2);
}

.summary-number {
  font-size: 2.4rem;
  font-weight: 700;
  color: #c81919;
  line-height: 1.1;
}

.bar-row {
  display: grid;
  grid-template-columns: minmax(120px, 220px) 1fr 44px;
  align-items: center;
  gap: 12px;
  padding: 5px 0;
}

.bar-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.9rem;
}

.bar-track {
  height: 12px;
  border-radius: 6px;
  background: rgba(128, 128, 128, 0.18);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 6px;
  background: #c81919;
}

.bar-count {
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}

/* Wide tables scroll inside their own container instead of pushing the page. */
.table-scroll {
  overflow-x: auto;
}

.matrix {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.matrix th,
.matrix td {
  padding: 7px 10px;
  text-align: right;
  white-space: nowrap;
  border-bottom: 1px solid rgba(128, 128, 128, 0.2);
}

.matrix thead th,
.matrix tbody th {
  text-align: left;
  font-weight: 600;
}

.matrix td.zero {
  opacity: 0.35;
}

.matrix td.total {
  font-weight: 700;
}

@media (max-width: 599px) {
  .bar-row {
    grid-template-columns: minmax(90px, 140px) 1fr 36px;
  }
}
</style>
