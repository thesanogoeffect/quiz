import { useNuxtApp } from "#app";  // Use the global context

// Reads live in stores/questionstats.js and come from the shipped /stats.json
// snapshot, not from Firestore. Only the counter writes go through here.

// A Firebase web API key is a project identifier, not a secret - it is meant to
// ship in client code. What actually protects the data is firestore.rules.
const firebaseConfig = {
  apiKey: "AIzaSyDdeQI0zLemr3lZRdJZbYvgh7Lh8i3xQSM",
  authDomain: "intro-psych-quiz-592fb.firebaseapp.com",
  projectId: "intro-psych-quiz-592fb",
  storageBucket: "intro-psych-quiz-592fb.appspot.com",
  messagingSenderId: "977871458212",
  appId: "1:977871458212:web:87ea3c5f93814b2c69bb31",
  measurementId: "G-98WY6TFC04",
};

// The Firestore SDK is by far the largest thing this app ships - around 140 kB
// compressed - and the only thing it does is add 1 to a counter. Importing it
// at the top of a plugin put all of it in the entry chunk, so every visitor
// waited for it before the first question could be drawn.
//
// So load it on demand. plugins/firebase.client.js calls warmUpFirestore() once
// the browser is idle, which is long before anyone has read a question and
// picked an answer, so in practice the SDK is already in memory by the time the
// first counter moves - it just is not in the way of the first paint.
let loading = null;

function loadFirestore() {
  loading ??= (async () => {
    const { collection, doc, getFirestore, increment, initializeApp, updateDoc } =
      await import("./firestore-sdk");
    const db = getFirestore(initializeApp(firebaseConfig));
    return { questionsRef: collection(db, "questions"), doc, increment, updateDoc };
  })();
  return loading;
}

export function warmUpFirestore() {
  const whenIdle =
    typeof requestIdleCallback === "function"
      ? requestIdleCallback
      : (fn) => setTimeout(fn, 2000);
  whenIdle(() => {
    loadFirestore().catch((error) => {
      console.warn("Could not load Firestore:", error?.message);
    });
  });
}

// Counter updates are fire-and-forget.
//
// updateDoc() only settles once the server acknowledges the write. When
// Firestore is unreachable - offline, blocked by a network, or the daily free
// quota exhausted - the SDK queues the write and the promise never settles at
// all. Awaiting it there froze the whole quiz after one question: the store's
// processingAnswer flag stayed latched and both navigation arrows went dead.
//
// So: issue the write, let the SDK retry it in the background, and return
// immediately. Nothing downstream depends on the acknowledgement - a lost
// counter is not worth stalling a student's revision session over.
export function incrementQuestionFields(id, updates, negative = false) {
  if (!updates || updates.length === 0) return Promise.resolve();

  // must be read inside the Nuxt context, and so before the first await
  const { $firestoreReadOnly } = useNuxtApp();

  // Local development shares the production database. Reads are harmless;
  // writes would quietly inflate the real community counters.
  if ($firestoreReadOnly) return Promise.resolve();

  loadFirestore()
    .then(({ questionsRef, doc, increment, updateDoc }) => {
      const updateData = {};
      updates.forEach((key) => {
        updateData[key] = increment(negative ? -1 : 1);
      });
      return updateDoc(doc(questionsRef, String(id)), updateData);
    })
    .catch((error) => {
      console.warn(`Could not update stats for question ${id}:`, error?.message);
    });

  return Promise.resolve();
}
