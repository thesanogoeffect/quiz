import { doc, getDoc, updateDoc, increment } from "firebase/firestore";
import { useNuxtApp } from "#app";  // Use the global context
// TODO Uncomment
// Function to retrieve a question by ID
export async function getQuestionById(id) {
    const { $questionsRef } = useNuxtApp(); // Access the injected questionsRef
  
    // Check if id is a valid string
    if (!id || typeof id !== 'string') {
      throw new Error('Invalid ID. ID must be a non-empty string.');
    }
  
    // console.log("ID:", id);  // Debug log
  
    const questionDocRef = doc($questionsRef, id);
  
    try {
      const questionSnapshot = await getDoc(questionDocRef);
  
      if (questionSnapshot.exists()) {
        return questionSnapshot.data();
      } else {
        throw new Error("No such document!");
      }
    } catch (error) {
      console.error("Error retrieving document:", error);
      throw error;
    }
  }

// Function to increment the fields of a question
export async function incrementQuestionFields(id, updates, negative = false) {
  await new Promise(resolve => setTimeout(resolve, 0)); // Empty await

  setTimeout(async () => {
    const { $questionsRef } = useNuxtApp(); // Access the injected questionsRef
    const questionDocRef = doc($questionsRef, String(id));

    // console.log("Triggered incrementQuestionFields", id, updates, negative);  // Debug log

    const updateData = {};
    updates.forEach((key) => {
      updateData[key] = increment(negative ? -1 : 1);
    });

    await updateDoc(questionDocRef, updateData);
  }, 0);
}
