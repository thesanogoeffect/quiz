import { defineStore } from "pinia";
import { incrementQuestionFields } from "~/services/firestore";
// THIS STORE IS ONLY FOR DATA THAT GOES TO FIRESTORE!

// This store enables us to access the Firestore data easily
// It will have a function that will fetch the data from Firestore based on the question_id
// Also increment functions for the question_id

// Reader and writer used to disagree on the upvote key, which silently threw
// away every upvote on reload. Keep all three in one place.
const STORAGE_KEYS = {
  upvote: "ipt_quiz_upvote_cache",
  downvote: "ipt_downvote_cache",
  flag: "ipt_quiz_flag_cache",
};
// The upvote cache used to be written here while being read from
// "ipt_upvote_cache"; migrate whichever copy an existing user has.
const LEGACY_UPVOTE_KEY = "ipt_upvote_cache";

// Community stats come from /stats.json, a snapshot of the Firestore counters
// that ships with the build and is refreshed weekly by a GitHub Action (see
// scripts/fetch_stats_snapshot.mjs). The app never reads Firestore at runtime:
// a live read per question put a network round trip on the critical path and
// cost a document read for a number that changes by one.
//
// Module-scope because it holds a Promise, which must not be made reactive.
let inFlightSnapshot = null;

const EMPTY_STATS = {
  times_asked: 0,
  times_answered_correct: 0,
  times_skipped: 0,
  times_flagged: 0,
  times_answered: 0,
  times_upvoted: 0,
  times_downvoted: 0,
};

function readCache(key) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch (error) {
    console.warn(`Ignoring unreadable ${key}:`, error);
    return null;
  }
}

function writeCache(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.warn(`Could not persist ${key}:`, error);
  }
}

export const useQuestionStatsStore = defineStore("questionstats", {
  state: () => ({
    current_question_stats: null, // a dictionary, as retrieved from Firestore or cache
    current_question_id: null,
    question_cache: {}, // a dictionary of question_id to question_stats
    // the following keep track whether the user has upvoted, downvoted, flagged etc.
    upvote_cache: {}, // a dictionary of question_id to true/false
    downvote_cache: {}, // a dictionary of question_id to true/false
    // a dictionary of question_id to true/false
    flag_cache: {}, // a dictionary of question_id to true/false

    current_questions_increment_fields: {}, // {int: dict} a dictionary of question_id to fields to increment, current proposed changes
    cached_questions_increment_fields: {}, // keeping track of what was already sent to Firestore

    snapshot: null, // {question_id: counters} from /stats.json, once loaded
    snapshotFetchedAt: null, // ISO timestamp of the snapshot
    statsAvailable: true, // false when the snapshot could not be loaded

    PERSISTENT_KEYS_ACROSS_SESSIONS: [
      "times_flagged",
      "times_upvoted",
      "times_downvoted",
    ],

    new_question_increment_fields: {
      times_asked: null,
      times_answered_correct: null,
      times_skipped: null,
      times_flagged: null,
      times_answered: null,
      times_upvoted: null,
      times_downvoted: null,
    }, // a dictionary of fields to increment
  }),

  getters: {
    // Get the stats for the current question
    currentQuestionStats: (state) => {
      return state.current_question_stats;
    },
    getQuestionStatsById: (state) => (question_id) => {
      return state.question_cache[question_id];
    },
    getCurrentIncrementFieldsbyId: (state) => (question_id) => {
      return state.current_questions_increment_fields[question_id] || {};
    },
    getCachedIncrementFieldsbyId: (state) => (question_id) => {
      return state.cached_questions_increment_fields[question_id] || {};
    },
    getUpvoteCache: (state) => {
      return state.upvote_cache;
    },
    getDownvoteCache: (state) => {
      return state.downvote_cache;
    },
    getFlagCache: (state) => {
      return state.flag_cache;
    },
    getUpvoteCacheById: (state) => (question_id) => {
      return !!state.upvote_cache[question_id];
    },
    getDownvoteCacheById: (state) => (question_id) => {
      return !!state.downvote_cache[question_id];
    },
    getFlagCacheById: (state) => (question_id) => {
      return !!state.flag_cache[question_id];
    },
    getStatsAvailable: (state) => state.statsAvailable,
    getSnapshotFetchedAt: (state) => state.snapshotFetchedAt,
  },

  actions: {
    // Question ids are numbers in l3.json but Firestore document ids are
    // strings. Everything in this store keys off the string form so the caches
    // and the documents cannot drift apart.
    key(question_id) {
      return String(question_id);
    },
    // Loads the snapshot once; every caller shares the same promise. Never
    // rejects - a missing snapshot only hides the community numbers.
    loadSnapshot() {
      if (this.snapshot) return Promise.resolve();
      inFlightSnapshot ??= this._loadSnapshot().finally(() => {
        inFlightSnapshot = null;
      });
      return inFlightSnapshot;
    },
    async _loadSnapshot() {
      try {
        const buildId = useRuntimeConfig().app.buildId;
        const data = await $fetch(`/stats.json?v=${buildId}`);
        if (!data || typeof data.questions !== "object") {
          throw new Error("stats.json has no questions object");
        }
        this.snapshot = data.questions;
        this.snapshotFetchedAt = data.fetched_at || null;
        this.statsAvailable = true;
      } catch (error) {
        console.warn("Community stats snapshot unavailable:", error?.message);
        this.snapshot = {};
        this.statsAvailable = false;
      }
    },
    async fetchQuestionStats(question_id) {
      const id = this.key(question_id);
      this.current_question_id = id;

      if (!(id in this.question_cache)) {
        await this.loadSnapshot();
        // The session copy is bumped locally as the student answers and votes,
        // so the numbers on screen include their own actions.
        this.question_cache[id] = { ...EMPTY_STATS, ...(this.snapshot[id] || {}) };
      }
      this.current_question_stats = this.question_cache[id];
      // Rebuilt, not preserved: a question served a second time in one
      // session needs a fresh baseline, or its counters are never sent.
      this.preBuildIncrementFields(id, { force: true });
    },
    loadUpvoteCacheFromLocalStorage() {
      this.upvote_cache =
        readCache(STORAGE_KEYS.upvote) || readCache(LEGACY_UPVOTE_KEY) || {};
    },
    loadDownvoteCacheFromLocalStorage() {
      this.downvote_cache = readCache(STORAGE_KEYS.downvote) || {};
    },
    loadFlagCacheFromLocalStorage() {
      this.flag_cache = readCache(STORAGE_KEYS.flag) || {};
    },
    loadInteractionsCacheFromLocalStorage() {
      this.loadUpvoteCacheFromLocalStorage();
      this.loadDownvoteCacheFromLocalStorage();
      this.loadFlagCacheFromLocalStorage();
    },
    saveUpvoteCacheToLocalStorage() {
      writeCache(STORAGE_KEYS.upvote, this.upvote_cache);
    },
    saveDownvoteCacheToLocalStorage() {
      writeCache(STORAGE_KEYS.downvote, this.downvote_cache);
    },
    saveFlagCacheToLocalStorage() {
      writeCache(STORAGE_KEYS.flag, this.flag_cache);
    },

    saveInteractionsCacheToLocalStorage() {
      this.saveUpvoteCacheToLocalStorage();
      this.saveDownvoteCacheToLocalStorage();
      this.saveFlagCacheToLocalStorage();
    },

    // Records a pending counter increment for a question. Safe to call before
    // the question's fields have been pre-built.
    markPending(question_id, field) {
      const id = this.key(question_id);
      if (!this.current_questions_increment_fields[id]) {
        this.preBuildIncrementFields(id);
      }
      this.current_questions_increment_fields[id][field] = true;
    },

    async batchFetchQuestionStats(question_ids) {
      for (const question_id of question_ids) {
        await this.fetchQuestionStats(question_id);
      }
    },
    async incrementSpecificQuestionFields(question_id) {
      const id = this.key(question_id);
      // get the current proposed changes to Firestore
      const fields = this.getCurrentIncrementFieldsbyId(id);
      // look to see if the fields were already sent to Firestore
      const cached_fields = this.getCachedIncrementFieldsbyId(id);
      // get only the key: value pairs that differ from the cached fields
      const fields_to_increment = [];
      const fields_to_decrement = [];
      for (const [key, value] of Object.entries(fields)) {
        if (Boolean(value) === Boolean(cached_fields[key])) continue;
        const target = value ? fields_to_increment : fields_to_decrement;
        target.push(key);
        // Votes and flags are mirrored into the local stats the moment the user
        // clicks, so only the passive counters are adjusted here.
        if (!this.PERSISTENT_KEYS_ACROSS_SESSIONS.includes(key)) {
          this.bumpCachedStat(id, key, value ? 1 : -1);
        }
      }

      if (fields_to_increment.length === 0 && fields_to_decrement.length === 0) {
        return; // nothing changed since the last flush
      }

      // Record what is being sent BEFORE awaiting. pagehide and
      // visibilitychange both fire when a tab closes, and both flush; without
      // this the second call sees an unchanged baseline and double-counts.
      this.cached_questions_increment_fields[id] = { ...fields };

      await incrementQuestionFields(id, fields_to_increment, false);
      await incrementQuestionFields(id, fields_to_decrement, true);
    },
    bumpCachedStat(question_id, field, delta) {
      const id = this.key(question_id);
      if (!this.question_cache[id]) {
        this.question_cache[id] = { ...EMPTY_STATS };
      }
      const current = Number(this.question_cache[id][field]) || 0;
      this.question_cache[id][field] = Math.max(0, current + delta);
    },
    upvoteSpecificQuestion(question_id) {
      const id = this.key(question_id);
      this.upvote_cache[id] = true;
      this.markPending(id, "times_upvoted");
      this.bumpCachedStat(id, "times_upvoted", 1);
      if (this.getDownvoteCacheById(id)) {
        this.cancelDownvoteSpecificQuestion(id);
      }
      this.saveUpvoteCacheToLocalStorage();
    },
    downvoteSpecificQuestion(question_id) {
      const id = this.key(question_id);
      this.downvote_cache[id] = true;
      this.markPending(id, "times_downvoted");
      this.bumpCachedStat(id, "times_downvoted", 1);
      if (this.getUpvoteCacheById(id)) {
        this.cancelUpvoteSpecificQuestion(id);
      }
      this.saveDownvoteCacheToLocalStorage();
    },
    flagSpecificQuestion(question_id) {
      const id = this.key(question_id);
      this.flag_cache[id] = true;
      this.markPending(id, "times_flagged");
      this.bumpCachedStat(id, "times_flagged", 1);
      this.saveFlagCacheToLocalStorage();
    },
    cancelUpvoteSpecificQuestion(question_id) {
      const id = this.key(question_id);
      this.upvote_cache[id] = false;
      this.markPending(id, "times_upvoted");
      this.current_questions_increment_fields[id]["times_upvoted"] = null;
      this.bumpCachedStat(id, "times_upvoted", -1);
      this.saveUpvoteCacheToLocalStorage();
    },
    cancelDownvoteSpecificQuestion(question_id) {
      const id = this.key(question_id);
      this.downvote_cache[id] = false;
      this.markPending(id, "times_downvoted");
      this.current_questions_increment_fields[id]["times_downvoted"] = null;
      this.bumpCachedStat(id, "times_downvoted", -1);
      this.saveDownvoteCacheToLocalStorage();
    },
    cancelFlagSpecificQuestion(question_id) {
      const id = this.key(question_id);
      this.flag_cache[id] = false;
      this.markPending(id, "times_flagged");
      this.current_questions_increment_fields[id]["times_flagged"] = null;
      this.bumpCachedStat(id, "times_flagged", -1);
      this.saveFlagCacheToLocalStorage();
    },

    // force: reset the baseline for a fresh serve of this question.
    // Without force it only initialises, so markPending() can be called before
    // the question has been fetched without wiping a pending edit.
    preBuildIncrementFields(id, { force = false } = {}) {
      // populate the current_questions_increment_fields and cached_questions_increment_fields with new_question_increment_fields
      const key = this.key(id);
      if (!force && this.current_questions_increment_fields[key]) return;

      this.current_questions_increment_fields[key] = {
        ...this.new_question_increment_fields,
      };
      this.cached_questions_increment_fields[key] = {
        ...this.new_question_increment_fields,
      };
      // now look into the local storage if the user already upvoted, downvoted or flagged the question
      for (const [cacheName, field] of [
        ["upvote_cache", "times_upvoted"],
        ["downvote_cache", "times_downvoted"],
        ["flag_cache", "times_flagged"],
      ]) {
        if (this[cacheName][key]) {
          this.current_questions_increment_fields[key][field] = true;
          this.cached_questions_increment_fields[key][field] = true;
        }
      }
    },
  },
});
