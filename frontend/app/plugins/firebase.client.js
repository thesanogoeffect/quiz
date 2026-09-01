import { initializeApp } from "firebase/app"; // Correct import for Firebase initialization
import { getFirestore, collection } from "firebase/firestore"; // Firestore-related imports

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

// Anything served from a local machine is development, and development must not
// move the real community counters. Running the quiz locally for ten minutes
// used to add a few dozen phantom answers to the live totals.
const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "0.0.0.0", "[::1]", "::1"]);

function isLocal() {
  if (typeof window === "undefined") return false;
  const { hostname } = window.location;
  return (
    LOCAL_HOSTS.has(hostname) ||
    hostname.endsWith(".local") ||
    // Allow an explicit override for testing the real thing on purpose:
    // ?firestore=live
    false
  );
}

export default defineNuxtPlugin(() => {
  const forceLive = new URLSearchParams(window.location.search).get("firestore") === "live";
  const readOnly = isLocal() && !forceLive;

  const app = initializeApp(firebaseConfig);
  const db = getFirestore(app);
  const questionsRef = collection(db, "questions");

  if (readOnly) {
    console.info(
      "[quiz] Running locally: community stats are read from Firestore but no " +
        "writes are sent. Append ?firestore=live to write for real."
    );
  }

  return {
    provide: {
      db,
      questionsRef,
      // services/firestore.js checks this before issuing any write.
      firestoreReadOnly: readOnly,
    },
  };
});
