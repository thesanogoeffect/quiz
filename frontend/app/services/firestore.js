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

// Function to increment the fields of a question.
// Resolves once the write has actually been issued, so callers can await a
// flush before navigating away. Errors are logged rather than thrown: losing a
// counter update must never interrupt the quiz.
export async function incrementQuestionFields(id, updates, negative = false) {
  if (!updates || updates.length === 0) return;

  const { $questionsRef } = useNuxtApp(); // must be read inside the Nuxt context
  const questionDocRef = doc($questionsRef, String(id));

  const updateData = {};
  updates.forEach((key) => {
    updateData[key] = increment(negative ? -1 : 1);
  });

  try {
    await updateDoc(questionDocRef, updateData);
  } catch (error) {
    console.warn(`Could not update stats for question ${id}:`, error?.message);
  }
}
