// The only five things this app uses from the Firebase SDK.
//
// services/firestore.js imports this module dynamically, which is what keeps
// the SDK out of the entry chunk. It has to go through a wrapper like this one
// rather than `import("firebase/firestore")` directly: a bare dynamic import
// pulls in the whole module, because the bundler cannot see through the
// destructuring on the other side of the await. Re-exporting the five names
// here gives it something static to tree-shake against, which is worth about
// 160 kB of Firestore internals that would otherwise ship.
export { initializeApp } from "firebase/app";
export { collection, doc, getFirestore, increment, updateDoc } from "firebase/firestore";
