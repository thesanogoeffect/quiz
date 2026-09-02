import { warmUpFirestore } from "~/services/firestore";

// The Firebase SDK itself is not imported here - see services/firestore.js,
// which loads it on demand. This plugin only decides whether writes are allowed
// and asks for the SDK to be fetched once the browser has nothing better to do.

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

  if (readOnly) {
    console.info(
      "[quiz] Running locally: no community counters are written and the " +
        "Firestore SDK is never loaded. Append ?firestore=live to write for real."
    );
  } else {
    warmUpFirestore();
  }

  return {
    provide: {
      // services/firestore.js checks this before issuing any write.
      firestoreReadOnly: readOnly,
    },
  };
});
