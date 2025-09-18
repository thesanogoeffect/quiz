import { initializeApp } from "firebase/app";  // Correct import for Firebase initialization
import { getFirestore, collection } from "firebase/firestore";  // Firestore-related imports


export default defineNuxtPlugin((nuxtApp) => {
  const firebaseConfig = {
    apiKey: "AIzaSyDdeQI0zLemr3lZRdJZbYvgh7Lh8i3xQSM",
    authDomain: "intro-psych-quiz-592fb.firebaseapp.com",
    projectId: "intro-psych-quiz-592fb",
    storageBucket: "intro-psych-quiz-592fb.appspot.com",
    messagingSenderId: "977871458212",
    appId: "1:977871458212:web:87ea3c5f93814b2c69bb31",
    measurementId: "G-98WY6TFC04"
  };

  const app = initializeApp(firebaseConfig);
  const db = getFirestore(app);
  const questionsRef = collection(db, "questions");
  

  return {
    provide: {
      db,
      questionsRef,
    },
  };
});