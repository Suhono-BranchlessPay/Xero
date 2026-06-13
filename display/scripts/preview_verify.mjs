#!/usr/bin/env node
/**
 * Preview Xero verify-page mapping for M3+M4 QA.
 */
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { isXeroAnchor, mapXeroVerifyPage } from "../src/xeroVerifyMapping.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const fixturesDir = join(__dirname, "..", "fixtures");

function preview(anchor, label) {
  if (!isXeroAnchor(anchor)) {
    console.log(`SKIP ${label}: not a Xero anchor`);
    return;
  }
  const page = mapXeroVerifyPage(anchor);
  console.log(`\n=== ${label} ===`);
  console.log("\nOrganisation Information");
  for (const row of page.businessRows) {
    console.log(`  ${row.label}: ${row.value}`);
  }
  console.log("\nTransaction Details");
  for (const row of page.transactionRows) {
    console.log(`  ${row.label}: ${row.value}`);
  }
  console.log(`\nStatus badge: ${page.statusBadge.label} (${page.statusBadge.variant})`);
}

if (!existsSync(fixturesDir)) {
  console.log("No fixtures yet — add JSON files to display/fixtures/ after live E2E.");
  process.exit(0);
}

const files = readdirSync(fixturesDir)
  .filter((f) => f.endsWith(".json"))
  .map((f) => join(fixturesDir, f));

for (const file of files) {
  preview(JSON.parse(readFileSync(file, "utf8")), file);
}
