import { useQuestionStatsStore } from "#imports";
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

    selected_chapters: [],
    all_chapters: [],
    selected_sources: [],
    all_sources: [],
    processingAnswer: false,

    DEFAULT_CHAPTERS: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14], // all chapters available at the start
    BANLIST_CHAPTERS: [11, 13, 16], // chapters to exclude
    answerHistory: [], // Store the full question objects with guesses for easier UI display
    reviewMode: false,
    currentReviewPosition: 0, //
    currentlyReviewedQuestion: null,
    BOOK_CHAPTER_NAMES:{
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
    filteredQuestions:
      (state) =>
      (chapter_ids = [], sources = [], question_ids = []) => {
        let filtered = state.all_questions;

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
        let filteredQuestions = state.filteredQuestions(
          chapter_ids,
          sources,
          question_ids
        );
    
        // Shuffle using Fisher-Yates
        return state.shuffleArray(filteredQuestions);
      },

    getReviewMode: (state) => state.reviewMode,

    getAnswerHistory: (state) => state.answerHistory,
    getAnswerHistoryLength: (state) => state.answerHistory.length,
    getCurrentReviewPosition: (state) => state.currentReviewPosition,

    getCurrentlyReviewedQuestion: (state) => state.currentlyReviewedQuestion,

    getChapterById: (state) => (chapter_id) =>
      state.BOOK_CHAPTER_NAMES[chapter_id],

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
      return state.all_questions.filter(
        (question) =>
          state.selected_chapters.includes(question.chapter_id) &&
          state.selected_sources.includes(question.source)
      );
    },

    isQueueEmpty: (state) => state.questionQueue.length === 0,

    getTotalQuestions: (state) => state.all_questions.length,

    getAnsweredCorrectlyPercentage: (state) => {
      if (state.total_answered_questions === 0) return 0;
      return (
        (state.total_correct_answers / state.total_answered_questions) * 100
      );
    },
  },

  actions: {
    resetAlreadySeenQuestions() {
      this.alreadySeenQuestions = {};
    },
    incrementTotalShownQuestions() {
      this.total_shown_questions++;
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
      localStorage.setItem(
        "selected_chapters_ipt",
        JSON.stringify(this.selected_chapters)
      );
      localStorage.setItem(
        "selected_sources_ipt",
        JSON.stringify(this.selected_sources)
      );
    },
    loadSelectedFiltersFromLocalStorage() {
      // disabling this logic for now
      // const selectedChapters = localStorage.getItem("selected_chapters_ipt");
      const selectedSources = localStorage.getItem("selected_sources_ipt");

      // if (selectedChapters) {
      //   this.selected_chapters = JSON.parse(selectedChapters);
      // } else {
      //   this.selected_chapters = this.DEFAULT_CHAPTERS;
      // }
      if (selectedSources) {
        this.selected_sources = JSON.parse(selectedSources);
      } else {
        this.selected_sources = this.all_sources;
      }
    },
    async toggleReviewMode() {
      const questionStatsStore = useQuestionStatsStore();
      await questionStatsStore.incrementSpecificQuestionFields(
        this.reviewMode
          ? this.currentlyReviewedQuestion.id
          : this.currentQuestion.id
      );
      questionStatsStore.saveInteractionsCacheToLocalStorage();
      this.reviewMode = !this.reviewMode;
      if (!this.reviewMode) {
        // if we just exited review mode, the user has seen the question
        questionStatsStore.current_questions_increment_fields[
          this.currentQuestion.id
        ]["times_asked"] = true;
        if (!this.alreadySeenQuestions[this.currentQuestion.id]) {
          this.incrementTotalShownQuestions();
          this.alreadySeenQuestions[this.currentQuestion.id] = true;
        }
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
      } else {
        this.decrementCurrentReviewPosition();
        await questionStatsStore.incrementSpecificQuestionFields(
          this.currentlyReviewedQuestion.id
        );
        questionStatsStore.saveInteractionsCacheToLocalStorage();
        this.currentlyReviewedQuestion =
          this.answerHistory[this.currentReviewPosition];
      }
    },
    async nextReviewedQuestion() {
      const questionStatsStore = useQuestionStatsStore();
      if (this.currentReviewPosition == this.getAnswerHistoryLength - 1) {
        // cannot go forward
      } else {
        this.incrementCurrentReviewPosition();
        await questionStatsStore.incrementSpecificQuestionFields(
          this.currentlyReviewedQuestion.id
        );
        questionStatsStore.saveInteractionsCacheToLocalStorage();
        this.currentlyReviewedQuestion =
          this.answerHistory[this.currentReviewPosition];
        // also increment to Firestore
      }
    },
    async loadQuestionsFromJSON() {
      try {
        // const response = await $fetch(`/l3.json?timestamp=${Date.now()}`); // to avoid caching,
        //  but we want caching now because we won't really maintain the project now
        const response = await $fetch('/l3.json'); // to avoid caching,
        this.all_questions = response;
        console.log("All Questions loaded from JSON:", this.all_questions.values());
      } catch (error) {
        console.error(error.message);
      }
    },

    async fill_filters_from_questions() {
      let chapters = new Set();
      let sources = new Set();
      this.all_questions.forEach((question) => {
        if (this.BANLIST_CHAPTERS.includes(question.chapter_id)) {
          return; // skip this iteration
        }
        chapters.add(question.chapter_id);
        sources.add(question.source);
      });
      this.all_chapters = Array.from(chapters);
      this.all_sources = Array.from(sources);
    },
    async setUp() {
      console.log("calling setUp");
      await this.loadQuestionsFromJSON();
      const questionStatsStore = useQuestionStatsStore();

      // Check if all_questions is loaded
      // console.log("All Questions:", this.all_questions);

      await this.fill_filters_from_questions();

      // Load selected filters from localStorage
      this.loadSelectedFiltersFromLocalStorage();

      // Generate the initial queue
      await this.generateQueue(this.selected_chapters, this.selected_sources);
      this.incrementTotalShownQuestions();
      this.currentQuestion = await this.getFromQueue(true);
      questionStatsStore.current_questions_increment_fields[
        this.currentQuestion.id
      ]["times_asked"] = true;
      // here, pop withou calling .getFromQueue
    },
    async reSetUpAfterFiltersChange() {
      const questionStatsStore = useQuestionStatsStore();
      // first, flush to Firestore
      await questionStatsStore.incrementSpecificQuestionFields(
        this.reviewMode
          ? this.currentlyReviewedQuestion.id
          : this.currentQuestion.id
      );
      questionStatsStore.saveInteractionsCacheToLocalStorage();
      console.log("Re-setting up after filters change");
      console.log("Selected Chapters:", this.selected_chapters);
      console.log("Selected Sources:", this.selected_sources);
      // Generate the initial queue
      await this.generateQueue(this.selected_chapters, this.selected_sources);
      // here, call .getFromQueue with blockAnalytics set to true
      this.currentQuestion = await this.getFromQueue(true);
      this.incrementTotalShownQuestions();
      questionStatsStore.current_questions_increment_fields[
        this.currentQuestion.id
      ]["times_asked"] = true;
      this.reviewMode = false;
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
      this.questionQueue = this.randomQuestions(
        chapter_ids,
        sources,
        question_ids
      ).map((question) => {
        // Create the answers array
        const answers = [
          question.correct_answer,
          question.distractor_1,
          question.distractor_2,
          question.distractor_3,
        ];

        // Shuffle the answers array using Fisher-Yates
        const shuffledAnswers = this.shuffleArray(answers);

        // Find the index of the correct answer in the shuffled array
        const correctAnswerIndex = shuffledAnswers.indexOf(
          question.correct_answer
        );

        // Return the formatted question object
        return {
          id: question.id,
          question_title: question.question_title,
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
    async getFromQueue(blockAnalytics = false) {
      const questionStatsStore = useQuestionStatsStore();

      if (this.questionQueue.length === 0) {
        console.info("The question queue is empty! Refilling the queue...");
        this.resetAlreadySeenQuestions();

        // Await generateQueue to ensure it completes before proceeding
        await this.generateQueue(this.selected_chapters, this.selected_sources);

        if (this.questionQueue.length === 0) {
          console.error("No questions available after queue refill.");
          this.currentQuestion = null; // Set currentQuestion to null if no questions are available
          return null;
        }
      }
      // Pop the first question from the queue and set it as the current question
      const nextQuestion = this.questionQueue.shift();
      await questionStatsStore.fetchQuestionStats(String(nextQuestion.id)); // TODO change later so that more than one question can be fetched at a time this.currentQuestion = nextQuestion;
      await questionStatsStore.preBuildIncrementFields([nextQuestion.id]);
      return nextQuestion;
    },
    async skipQuestion() {
      const questionStatsStore = useQuestionStatsStore();
      if (!this.currentQuestion) {
        console.error("No current question to skip.");
        return;
      }

      if (this.skipsRemaining <= 0) {
        console.error("No skips remaining.");
        return;
      }

      this.skipsRemaining -= 1;

      // Mark the current question as skipped
      this.currentQuestion.skipped = true;
      // Add the current question to answerHistory
      this.answerHistory.push(this.currentQuestion);

      questionStatsStore.current_questions_increment_fields[
        this.currentQuestion.id
      ]["times_skipped"] = true;
      // Pop the next question and set it as the current question
      await this.toggleReviewMode();
      this.currentQuestion = await this.getFromQueue();
      // Increment counters
      this.incrementTotalSkippedQuestions();
    },
    async answerCurrentQuestion(guessed_index) {
      this.processingAnswer = true;
      const questionStatsStore = useQuestionStatsStore();
      if (!this.currentQuestion) {
        console.error("No current question to answer.");
        return;
      }

      this.currentQuestion.guessed_index = guessed_index;
      this.currentQuestion.skipped = false;
      const isCorrect =
        guessed_index === this.currentQuestion.correct_answer_index;

      if (isCorrect) {
        questionStatsStore.current_questions_increment_fields[
          this.currentQuestion.id
        ]["times_answered_correct"] = true;
      }
      questionStatsStore.current_questions_increment_fields[
        this.currentQuestion.id
      ]["times_answered"] = true;

      // Add the current question to answerHistory
      this.answerHistory.push(this.currentQuestion);

      // Increment counters
      this.incrementTotalAnsweredQuestions();
      if (isCorrect) {
        this.incrementTotalCorrectAnswers();

        // Generate a random integer between 2 and 5
        const randomInt = Math.floor(Math.random() * (5 - 2 + 1)) + 2;

        // Add a skip based on the randomly generated number of correct answers
        if (this.total_correct_answers % randomInt === 0) {
          if (this.skipsRemaining < 3) {
            this.skipsRemaining += 1;
          }
        }
      }

      // console.log("answerHistory:", this.answerHistory);
      await this.toggleReviewMode();

      // Pop the next question and set it as the current question
      this.currentQuestion = await this.getFromQueue();
      this.processingAnswer = false;
    },
  },
});
