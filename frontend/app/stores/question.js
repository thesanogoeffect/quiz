import { useQuestionStatsStore } from "#imports";

const STORAGE_KEYS = {
  chapters: "selected_chapters_ipt",
  sources: "selected_sources_ipt",
};

// Options like "None of the above" only make sense in last position, but the
// answers are shuffled. Detect them so they can be pinned to the end.
const POSITIONAL_OPTION =
  /\b(all|none|neither|both)\b[^.]*\b(above|these|options|answers|statements|listed)\b|\bof the above\b|^\s*(both|neither) (answers?|statements?) (are|is)\b/i;

// Some imported questions still carry the original exam's letter prefix
// ("a. zygote, embryo, fetus"), which collides with the A/B/C/D labels the UI
// draws. Only strip when every option carries one, so "B. F. Skinner" survives.
const LETTER_PREFIX = /^\s*[a-dA-D]\s*[.)]\s+/;

// Module-scope, not store state: it holds a Promise, which has no business
// being reactive.
let inFlightSetup = null;

function normaliseOptions(rawOptions) {
  const trimmed = rawOptions.map((o) => String(o ?? "").trim());
  if (trimmed.every((o) => LETTER_PREFIX.test(o))) {
    return trimmed.map((o) => o.replace(LETTER_PREFIX, "").trim());
  }
  return trimmed;
}

export const useQuestionStore = defineStore("question", {
  state: () => ({
    total_shown_questions: 0,
    total_answered_questions: 0,
    total_correct_answers: 0,
    total_skipped_questions: 0,

    all_questions: [], // as loaded from JSON file, including all original data
    questionQueue: [], // queue holding the questions waiting to be asked
    currentQuestion: null, // the current question being asked

    alreadySeenQuestions: {}, // store the question ids that have already been seen by the user

    skipsRemaining: 3, // number of skips remaining for the user
    correctSinceLastSkip: 0, // progress towards earning the next skip back
    nextSkipThreshold: 3, // how many correct answers that takes; re-rolled on each award

    selected_chapters: [],
    all_chapters: [],
    selected_sources: [],
    all_sources: [],
    processingAnswer: false,

    loadError: null, // non-null when the question set could not be loaded at all
    filterWarning: null, // set when a filter combination matched nothing

    DEFAULT_CHAPTERS: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14], // all chapters available at the start
    BANLIST_CHAPTERS: [11, 13, 16], // chapters to exclude
    answerHistory: [], // Store the full question objects with guesses for easier UI display
    reviewMode: false,
    currentReviewPosition: 0, //
    currentlyReviewedQuestion: null,
    // What the raw `source` values are called in the UI. The values themselves
    // are unchanged everywhere else (data, filters, localStorage).
    SOURCE_LABELS: {
      Book: "OpenStax book",
      "21/22_Student_Halfway": "Students 2021/22",
      "23/24_Student_Final": "Students 2023/24",
    },
    BOOK_CHAPTER_NAMES: {
      1: "Introduction to Psychology",
      2: "Psychological Research",
      3: "Biopsychology",
      4: "States of Consciousness",
      5: "Sensation and Perception",
      6: "Learning",
      7: "Thinking and Intelligence",
      8: "Memory",
      9: "Lifespan Development",
      10: "Motivation and Emotion",
      12: "Social Psychology",
      14: "Stress, Lifestyle, and Health",
    },
  }),
  getters: {
    getProcessingAnswer: (state) => state.processingAnswer,
    getLoadError: (state) => state.loadError,
    getFilterWarning: (state) => state.filterWarning,
    filteredQuestions:
      (state) =>
      (chapter_ids = [], sources = [], question_ids = []) => {
        let filtered = state.all_questions;

        // Always exclude banned chapters globally
        if (state.BANLIST_CHAPTERS && state.BANLIST_CHAPTERS.length > 0) {
          filtered = filtered.filter(
            (q) => !state.BANLIST_CHAPTERS.includes(q.chapter_id)
          );
        }

        // Apply chapter_ids filter if provided
        if (chapter_ids.length > 0) {
          filtered = filtered.filter((question) =>
            chapter_ids.includes(question.chapter_id)
          );
        }

        // Apply sources filter if provided
        if (sources.length > 0) {
          filtered = filtered.filter((question) =>
            sources.includes(question.source)
          );
        }

        // Apply question_ids filter if provided
        if (question_ids.length > 0) {
          filtered = filtered.filter((question) =>
            question_ids.includes(question.id)
          );
        }

        return filtered;
      },

    randomQuestions:
      (state) =>
      (chapter_ids = [], sources = [], question_ids = []) => {
        const filteredQuestions = state.filteredQuestions(
          chapter_ids,
          sources,
          question_ids
        );

        // Shuffle a copy - all_questions must keep its own ordering
        return state.shuffleArray([...filteredQuestions]);
      },

    getReviewMode: (state) => state.reviewMode,

    getAnswerHistory: (state) => state.answerHistory,
    getAnswerHistoryLength: (state) => state.answerHistory.length,
    getCurrentReviewPosition: (state) => state.currentReviewPosition,

    getCurrentlyReviewedQuestion: (state) => state.currentlyReviewedQuestion,

    getChapterById: (state) => (chapter_id) =>
      state.BOOK_CHAPTER_NAMES[chapter_id],

    getSourceLabel: (state) => (source) => state.SOURCE_LABELS[source] || source,

    getCurrentQuestion: (state) => state.currentQuestion,

    getSkipsRemaining: (state) => state.skipsRemaining,

    getSkippedQuestions: (state) => state.total_skipped_questions,

    getAllChapters: (state) => state.all_chapters,

    getAllSources: (state) => state.all_sources,

    getBookChapterNames: (state) => state.BOOK_CHAPTER_NAMES,

    getSelectedChapters: (state) => state.selected_chapters,

    getSelectedSources: (state) => state.selected_sources,

    getTotalShownQuestions: (state) => state.total_shown_questions,

    getTotalAnsweredQuestions: (state) => state.total_answered_questions,

    getTotalCorrectAnswers: (state) => state.total_correct_answers,

    getFilteredByChapterAndSource: (state) => {
      return state.all_questions
        .filter((q) => !state.BANLIST_CHAPTERS.includes(q.chapter_id))
        .filter(
          (question) =>
            state.selected_chapters.includes(question.chapter_id) &&
            state.selected_sources.includes(question.source)
        );
    },

    isQueueEmpty: (state) => state.questionQueue.length === 0,

    getTotalQuestions: (state) => state.all_questions.length,

    // What a student can actually be shown - the banned chapters never appear,
    // so quoting the raw total anywhere in the UI would be misleading.
    getAvailableQuestions: (state) =>
      state.all_questions.filter(
        (q) => !state.BANLIST_CHAPTERS.includes(q.chapter_id)
      ),
    getAvailableQuestionCount() {
      return this.getAvailableQuestions.length;
    },

    getAnsweredCorrectlyPercentage: (state) => {
      if (state.total_answered_questions === 0) return 0;
      return (
        (state.total_correct_answers / state.total_answered_questions) * 100
      );
    },
  },

  actions: {
    sanitizeChapterIds(ids = []) {
      if (!Array.isArray(ids)) return [];
      const banned = new Set(this.BANLIST_CHAPTERS || []);
      return ids.filter((id) => !banned.has(id));
    },
    resetAlreadySeenQuestions() {
      this.alreadySeenQuestions = {};
    },
    // Counts a question towards "Total Shown" at most once per pass through the
    // queue - callers used to increment blindly, which double-counted the first
    // question of every session and after every filter change.
    markQuestionShown(id) {
      if (id === undefined || id === null) return;
      if (!this.alreadySeenQuestions[id]) {
        this.alreadySeenQuestions[id] = true;
        this.total_shown_questions++;
      }
    },
    incrementTotalAnsweredQuestions() {
      this.total_answered_questions++;
    },
    incrementTotalCorrectAnswers() {
      this.total_correct_answers++;
    },
    incrementTotalSkippedQuestions() {
      this.total_skipped_questions++;
    },
    saveSelectedFiltersToLocalStorage() {
      try {
        localStorage.setItem(
          STORAGE_KEYS.chapters,
          JSON.stringify(this.selected_chapters)
        );
        localStorage.setItem(
          STORAGE_KEYS.sources,
          JSON.stringify(this.selected_sources)
        );
      } catch (error) {
        console.warn("Could not persist filters:", error);
      }
    },
    loadSelectedFiltersFromLocalStorage() {
      let storedChapters = null;
      let storedSources = null;
      try {
        storedChapters = JSON.parse(
          localStorage.getItem(STORAGE_KEYS.chapters) || "null"
        );
        storedSources = JSON.parse(
          localStorage.getItem(STORAGE_KEYS.sources) || "null"
        );
      } catch (error) {
        console.warn("Ignoring unreadable stored filters:", error);
      }

      const knownChapters = new Set(this.all_chapters);
      const knownSources = new Set(this.all_sources);

      // Only keep stored values that still exist in the current question set,
      // otherwise a filter saved last semester can leave the quiz with nothing
      // to show.
      const chapters = Array.isArray(storedChapters)
        ? this.sanitizeChapterIds(storedChapters).filter((id) =>
            knownChapters.has(id)
          )
        : [];
      const sources = Array.isArray(storedSources)
        ? storedSources.filter((s) => knownSources.has(s))
        : [];

      this.selected_chapters = chapters.length
        ? chapters
        : this.sanitizeChapterIds(this.DEFAULT_CHAPTERS).filter((id) =>
            knownChapters.has(id)
          );
      this.selected_sources = sources.length ? sources : [...this.all_sources];

      if (!this.selected_chapters.length) {
        this.selected_chapters = [...this.all_chapters];
      }
    },
    async toggleReviewMode() {
      const questionStatsStore = useQuestionStatsStore();
      const flushId = this.reviewMode
        ? this.currentlyReviewedQuestion?.id
        : this.currentQuestion?.id;
      if (flushId !== undefined && flushId !== null) {
        await questionStatsStore.incrementSpecificQuestionFields(flushId);
      }
      questionStatsStore.saveInteractionsCacheToLocalStorage();
      this.reviewMode = !this.reviewMode;
      if (!this.reviewMode && this.currentQuestion) {
        // if we just exited review mode, the user has seen the question
        questionStatsStore.markPending(this.currentQuestion.id, "times_asked");
        this.markQuestionShown(this.currentQuestion.id);
      }
      if (this.getAnswerHistoryLength > 0) {
        this.currentlyReviewedQuestion = this.answerHistory.at(-1);
        this.currentReviewPosition = this.getAnswerHistoryLength - 1;
      }
    },
    incrementCurrentReviewPosition() {
      this.currentReviewPosition++;
    },
    decrementCurrentReviewPosition() {
      this.currentReviewPosition--;
    },
    resetCurrentReviewPosition() {
      this.currentReviewPosition = 0;
    },
    async previousReviewedQuestion() {
      const questionStatsStore = useQuestionStatsStore();
      if (this.currentReviewPosition === 0) {
        // cannot go back,
        return;
      }
      this.decrementCurrentReviewPosition();
      if (this.currentlyReviewedQuestion) {
        await questionStatsStore.incrementSpecificQuestionFields(
          this.currentlyReviewedQuestion.id
        );
      }
      questionStatsStore.saveInteractionsCacheToLocalStorage();
      this.currentlyReviewedQuestion =
        this.answerHistory[this.currentReviewPosition];
    },
    async nextReviewedQuestion() {
      const questionStatsStore = useQuestionStatsStore();
      if (this.currentReviewPosition >= this.getAnswerHistoryLength - 1) {
        // cannot go forward
        return;
      }
      this.incrementCurrentReviewPosition();
      if (this.currentlyReviewedQuestion) {
        await questionStatsStore.incrementSpecificQuestionFields(
          this.currentlyReviewedQuestion.id
        );
      }
      questionStatsStore.saveInteractionsCacheToLocalStorage();
      this.currentlyReviewedQuestion =
        this.answerHistory[this.currentReviewPosition];
    },
    async loadQuestionsFromJSON() {
      // Cache-bust on every deploy rather than every page view: the file is
      // 1.2 MB and only changes when the question set is regenerated.
      const buildId = useRuntimeConfig().app.buildId;
      const response = await $fetch(`/l3.json?v=${buildId}`);
      if (!Array.isArray(response) || response.length === 0) {
        throw new Error("l3.json did not contain any questions");
      }
      // is_disabled is authored as a string in the export, so "0" must not
      // count as disabled - compare against the truthy values explicitly.
      this.all_questions = response.filter((q) => {
        const flag = String(q?.is_disabled ?? "").trim().toLowerCase();
        return flag !== "1" && flag !== "true" && flag !== "yes";
      });
    },

    fill_filters_from_questions() {
      const chapters = new Set();
      const sources = new Set();
      this.all_questions.forEach((question) => {
        if (this.BANLIST_CHAPTERS.includes(question.chapter_id)) {
          return; // skip this iteration
        }
        chapters.add(question.chapter_id);
        sources.add(question.source);
      });
      this.all_chapters = Array.from(chapters).sort((a, b) => a - b);
      this.all_sources = Array.from(sources).sort();
    },
    // Loads the question set and the saved filters. Safe to call from any
    // route - it deliberately does NOT pick a question, because doing that on
    // /about or /questions would record a "times_asked" for a question the
    // visitor never saw.
    //
    // Both app.vue and the page call this, and a child's onMounted runs before
    // the root's, so the in-flight promise is shared - otherwise the 1.2 MB
    // l3.json is fetched and parsed twice on every cold load.
    setUp() {
      if (this.all_questions.length > 0) return Promise.resolve();
      inFlightSetup ??= this._setUp().finally(() => {
        inFlightSetup = null;
      });
      return inFlightSetup;
    },
    async _setUp() {
      this.loadError = null;
      try {
        await this.loadQuestionsFromJSON();
      } catch (error) {
        console.error("Could not load the question set:", error);
        this.loadError =
          "The question set could not be loaded. Check your connection and try again.";
        return;
      }

      this.fill_filters_from_questions();
      this.loadSelectedFiltersFromLocalStorage();
    },
    // Serves the first question. Called from the quiz page only.
    async startQuiz() {
      if (this.currentQuestion || this.loadError) return;
      if (this.all_questions.length === 0) await this.setUp();
      if (this.loadError) return;

      await this.generateQueue(this.selected_chapters, this.selected_sources);
      const first = await this.getFromQueue();
      if (!first) {
        this.loadError =
          "No questions are available right now. Try resetting the filters.";
        return;
      }
      this.currentQuestion = first;
      this.markQuestionShown(first.id);
      useQuestionStatsStore().markPending(first.id, "times_asked");
    },
    // Returns true when the new filters produced a usable queue. On failure the
    // previous question stays on screen so the app never lands on a dead state.
    async reSetUpAfterFiltersChange() {
      const questionStatsStore = useQuestionStatsStore();
      const flushId = this.reviewMode
        ? this.currentlyReviewedQuestion?.id
        : this.currentQuestion?.id;
      if (flushId !== undefined && flushId !== null) {
        await questionStatsStore.incrementSpecificQuestionFields(flushId);
      }
      questionStatsStore.saveInteractionsCacheToLocalStorage();

      this.selected_chapters = this.sanitizeChapterIds(this.selected_chapters);

      const candidates = this.filteredQuestions(
        this.selected_chapters,
        this.selected_sources
      );
      if (candidates.length === 0) {
        // Not every chapter has questions from every source, so this is easy to
        // hit from the filter dialog. Bail out before touching the queue.
        this.filterWarning =
          "No questions match that combination of chapters and sources.";
        return false;
      }

      await this.generateQueue(this.selected_chapters, this.selected_sources);
      const next = await this.getFromQueue();
      if (!next) {
        this.filterWarning =
          "No questions match that combination of chapters and sources.";
        return false;
      }

      this.filterWarning = null;
      // A previous "no questions available" state must not outlive the fix.
      this.loadError = null;
      this.resetAlreadySeenQuestions();
      this.currentQuestion = next;
      this.markQuestionShown(next.id);
      questionStatsStore.markPending(next.id, "times_asked");
      this.reviewMode = false;
      return true;
    },
    shuffleArray(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array;
    },
    async generateQueue(chapter_ids = [], sources = [], question_ids = []) {
      // Filter and randomize the questions to generate a queue
      const safeChapters = this.sanitizeChapterIds(chapter_ids);
      this.questionQueue = this.randomQuestions(
        safeChapters,
        sources,
        question_ids
      ).map((question) => {
        const options = normaliseOptions([
          question.correct_answer,
          question.distractor_1,
          question.distractor_2,
          question.distractor_3,
        ]);
        const correctAnswer = options[0];

        const shuffledAnswers = this.shuffleArray([...options]);

        // "None of the above" style options refer to the options printed above
        // them, so they have to stay last no matter how the rest shuffled.
        const pinned = shuffledAnswers.filter((a) => POSITIONAL_OPTION.test(a));
        if (pinned.length > 0 && pinned.length < shuffledAnswers.length) {
          const rest = shuffledAnswers.filter(
            (a) => !POSITIONAL_OPTION.test(a)
          );
          shuffledAnswers.splice(0, shuffledAnswers.length, ...rest, ...pinned);
        }

        // Find the index of the correct answer in the shuffled array
        const correctAnswerIndex = shuffledAnswers.indexOf(correctAnswer);

        // Return the formatted question object
        return {
          id: question.id,
          question_title: String(question.question_title ?? "").trim(),
          answers: shuffledAnswers, // Shuffled answers
          chapter_id: question.chapter_id,
          correct_answer_index: correctAnswerIndex, // Index of the correct answer
          description_llm: question.description_llm,
          guessed_index: null,
          skipped: false,
          source: question.source,
          author: question.author,
        };
      });
    },
    async getFromQueue() {
      const questionStatsStore = useQuestionStatsStore();

      if (this.questionQueue.length === 0) {
        console.info("The question queue is empty! Refilling the queue...");
        this.resetAlreadySeenQuestions();

        // Await generateQueue to ensure it completes before proceeding
        await this.generateQueue(this.selected_chapters, this.selected_sources);

        if (this.questionQueue.length === 0) {
          console.warn("No questions available after queue refill.");
          return null;
        }
      }
      // Pop the first question from the queue and set it as the current question
      const nextQuestion = this.questionQueue.shift();
      // Community stats are a nice-to-have; a Firestore outage must not stop
      // the quiz, so fetchQuestionStats never rejects.
      await questionStatsStore.fetchQuestionStats(nextQuestion.id);
      return nextQuestion;
    },
    async skipQuestion() {
      const questionStatsStore = useQuestionStatsStore();
      if (this.processingAnswer || this.reviewMode) return;
      if (!this.currentQuestion) {
        console.warn("No current question to skip.");
        return;
      }
      if (this.skipsRemaining <= 0) {
        return;
      }

      this.processingAnswer = true;
      try {
        this.skipsRemaining -= 1;

        // Mark the current question as skipped
        this.currentQuestion.skipped = true;
        this.currentQuestion.guessed_index = null;
        // Add the current question to answerHistory
        this.answerHistory.push(this.currentQuestion);

        questionStatsStore.markPending(this.currentQuestion.id, "times_skipped");
        // Pop the next question and set it as the current question
        await this.toggleReviewMode();
        const next = await this.getFromQueue();
        if (next) this.currentQuestion = next;
        // Increment counters
        this.incrementTotalSkippedQuestions();
      } finally {
        this.processingAnswer = false;
      }
    },
    async answerCurrentQuestion(guessed_index) {
      const questionStatsStore = useQuestionStatsStore();
      if (this.processingAnswer || this.reviewMode) return;
      if (!this.currentQuestion) {
        console.warn("No current question to answer.");
        return;
      }

      this.processingAnswer = true;
      try {
        this.currentQuestion.guessed_index = guessed_index;
        this.currentQuestion.skipped = false;
        const isCorrect =
          guessed_index === this.currentQuestion.correct_answer_index;

        if (isCorrect) {
          questionStatsStore.markPending(
            this.currentQuestion.id,
            "times_answered_correct"
          );
        }
        questionStatsStore.markPending(
          this.currentQuestion.id,
          "times_answered"
        );

        // Add the current question to answerHistory
        this.answerHistory.push(this.currentQuestion);

        // Increment counters
        this.incrementTotalAnsweredQuestions();
        if (isCorrect) {
          this.incrementTotalCorrectAnswers();

          // Earn a skip back after a run of correct answers. The length of the
          // run is re-rolled each time so it stays a little unpredictable.
          this.correctSinceLastSkip += 1;
          if (this.correctSinceLastSkip >= this.nextSkipThreshold) {
            this.correctSinceLastSkip = 0;
            this.nextSkipThreshold = 2 + Math.floor(Math.random() * 4); // 2..5
            if (this.skipsRemaining < 3) {
              this.skipsRemaining += 1;
            }
          }
        }

        await this.toggleReviewMode();

        // Pop the next question and set it as the current question
        const next = await this.getFromQueue();
        if (next) this.currentQuestion = next;
      } finally {
        this.processingAnswer = false;
      }
    },
  },
});
