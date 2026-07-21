#!/usr/bin/env node

/** Download and unpack the pinned local Kokoro narration runtime from npm. */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const root = path.dirname(fileURLToPath(import.meta.url));
const runtime = path.join(root, ".kokoro-runtime");
fs.mkdirSync(runtime, { recursive: true });

const packages = [
  ["expo-kokoro", "1.1.9", "expo-kokoro-1.1.9.tgz"],
  ["kokoro-js", "1.2.1", "kokoro-js-1.2.1.tgz"],
  ["onnxruntime-web", "1.21.0", "onnxruntime-web-1.21.0.tgz"],
  ["phonemizer", "1.2.1", "phonemizer-1.2.1.tgz"],
];

function run(command, args) {
  const result = spawnSync(command, args, { stdio: "inherit", shell: process.platform === "win32" });
  if (result.status !== 0) throw new Error(`${command} failed with exit code ${result.status}`);
}

for (const [name, version, archive] of packages) {
  const destination = path.join(runtime, name);
  fs.mkdirSync(destination, { recursive: true });
  const archivePath = path.join(runtime, archive);
  if (!fs.existsSync(archivePath)) {
    run("npm", ["pack", `${name}@${version}`, "--pack-destination", runtime]);
  }
  run("tar", ["-xzf", archivePath, "-C", destination]);
}

console.log(`Kokoro runtime ready at ${runtime}`);

