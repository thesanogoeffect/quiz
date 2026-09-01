import { doc, getDoc, updateDoc, increment } from "firebase/firestore";
import { useNuxtApp } from "#app";  // Use the global context

// Function to retrieve a question by ID
export async function getQuestionById(id) {
  const { $questionsRef } = useNuxtApp(); // Access the injected questionsRef

  if (!id || typeof id !== "string") {
    throw new Error("Invalid ID. ID must be a non-empty string.");
  }

  const questionSnapshot = await getDoc(doc($questionsRef, id));

  if (!questionSnapshot.exists()) {
    // Distinguish "this question has no stats yet" from "Firestore is down" so
    // the caller can keep showing community stats for the questions that do.
    const error = new Error(`No stats document for question ${id}`);
    error.code = "not-found";
    throw error;
  }
  return questionSnapshot.data();
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

  // must be read inside the Nuxt context
  const { $questionsRef, $firestoreReadOnly } = useNuxtApp();

  // Local development shares the production database. Reads are harmless;
  // writes would quietly inflate the real community counters.
  if ($firestoreReadOnly) return Promise.resolve();

  const questionDocRef = doc($questionsRef, String(id));

  const updateData = {};
  updates.forEach((key) => {
    updateData[key] = increment(negative ? -1 : 1);
  });

  try {
    updateDoc(questionDocRef, updateData).catch((error) => {
      console.warn(`Could not update stats for question ${id}:`, error?.message);
    });
  } catch (error) {
    // updateDoc can throw synchronously on a malformed reference.
    console.warn(`Could not queue stats update for question ${id}:`, error?.message);
  }
  return Promise.resolve();
}
