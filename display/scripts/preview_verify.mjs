#!/usr/bin/env node
/**
 * Preview Wave verify-page mapping for M3+M4 QA.
 * Usage: node scripts/preview_verify.mjs [fixture.json]
 */
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { isWaveAnchor, mapWaveVerifyPage } from "../src/waveVerifyMapping.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const fixturesDir = join(__dirname, "..", "fixtures");

function preview(anchor, label) {
  if (!isWaveAnchor(anchor)) {
    console.log(`SKIP ${label}: not a Wave anchor`);
    return;
  }
  const page = mapWaveVerifyPage(anchor);
  console.log(`\n=== ${label} ===`);
  if (anchor.verify_url) {
    console.log(`Verify: ${anchor.verify_url}`);
  }
  console.log("\nBusiness Information");
  for (const row of page.businessRows) {
    console.log(`  ${row.label}: ${row.value}`);
  }
  console.log("\nTransaction Details");
  for (const row of page.transactionRows) {
    console.log(`  ${row.label}: ${row.value}`);
  }
  console.log(`\nStatus badge: ${page.statusBadge.label} (${page.statusBadge.variant})`);
  console.log(`\nInstructions: ${page.instructions}`);
}

const arg = process.argv[2];
const files = arg
  ? [arg.endsWith(".json") ? arg : join(fixturesDir, arg)]
  : readdirSync(fixturesDir)
      .filter((f) => f.endsWith(".json"))
      .map((f) => join(fixturesDir, f));

for (const file of files) {
  const anchor = JSON.parse(readFileSync(file, "utf8"));
  preview(anchor, anchor.anchor_id ?? file);
}
