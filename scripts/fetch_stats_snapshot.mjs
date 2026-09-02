#!/usr/bin/env node
// Fetch the per-question community counters from Firestore and write them to
// frontend/public/stats.json, which the app loads instead of reading Firestore
// at runtime. Zero dependencies: Node 18+ fetch plus the public web API key.
// Reading a question document is allowed by the security rules; :batchGet is
// evaluated as `get`, so the `allow list: if false` rule does not block it.
//
//     node scripts/fetch_stats_snapshot.mjs            # -> frontend/public/stats.json
//     node scripts/fetch_stats_snapshot.mjs --out x.json
//
// Exits non-zero on any failure so a scheduled run never commits a bad file.

import { readFileSync, writeFileSync } from "node:fs";

const PROJECT = "intro-psych-quiz-592fb";
const API_KEY = "AIzaSyDdeQI0zLemr3lZRdJZbYvgh7Lh8i3xQSM"; // public by design
const ROOT = `https://firestore.googleapis.com/v1/projects/${PROJECT}/databases/(default)/documents`;
const DOC_ROOT = `projects/${PROJECT}/databases/(default)/documents`;
const COUNTERS = [
  "times_asked",
  "times_answered",
  "times_answered_correct",
  "times_skipped",
  "times_flagged",
  "times_upvoted",
  "times_downvoted",
];
const CHUNK = 200;

const outIndex = process.argv.indexOf("--out");
const out = outIndex > 0 ? process.argv[outIndex + 1] : "frontend/public/stats.json";

const questions = JSON.parse(readFileSync("frontend/public/l3.json", "utf8"));
const ids = questions.map((q) => String(q.id));

async function batchGet(chunk) {
  const response = await fetch(`${ROOT}:batchGet?key=${API_KEY}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ documents: chunk.map((id) => `${DOC_ROOT}/questions/${id}`) }),
  });
  if (!response.ok) {
    throw new Error(`Firestore returned HTTP ${response.status}: ${(await response.text()).slice(0, 300)}`);
  }
  return (await response.json()).filter((entry) => entry.found).map((entry) => entry.found);
}

const stats = {};
for (let i = 0; i < ids.length; i += CHUNK) {
  for (const doc of await batchGet(ids.slice(i, i + CHUNK))) {
    const id = doc.name.split("/").pop();
    const fields = doc.fields || {};
    stats[id] = Object.fromEntries(
      COUNTERS.map((key) => [key, Number(fields[key]?.integerValue ?? 0)])
    );
  }
}

const found = Object.keys(stats).length;
if (found < ids.length * 0.9) {
  throw new Error(`only ${found} of ${ids.length} questions have a stats document - refusing to write`);
}

const snapshot = { fetched_at: new Date().toISOString(), questions: stats };
writeFileSync(out, JSON.stringify(snapshot) + "\n");
const totals = Object.fromEntries(
  COUNTERS.map((key) => [key, Object.values(stats).reduce((sum, row) => sum + row[key], 0)])
);
console.log(`wrote ${out}: ${found} questions, answered ${totals.times_answered.toLocaleString()} times`);
