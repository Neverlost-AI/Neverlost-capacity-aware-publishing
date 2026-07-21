#!/usr/bin/env node

/**
 * Render the seven-section judge-demo narration with local Kokoro.
 *
 * Voice: am_fenrir
 * Speed: 0.83
 * Status: REVIEW_ONLY until a human listens and approves the result.
 *
 * Runtime assets are supplied by the npm packages `expo-kokoro`, `kokoro-js`,
 * `onnxruntime-web`, and `phonemizer`. Set KOKORO_RUNTIME_ROOT to a persistent
 * unpacked runtime directory; the temporary development paths below are used
 * when that variable is not set.
 */

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const OUTPUT = path.join(ROOT, "output", "demo-audio");
const NARRATION = path.join(ROOT, "demo_narration.json");

const configuredRuntime = process.env.KOKORO_RUNTIME_ROOT ?? path.join(ROOT, ".kokoro-runtime");
const localRuntimeExists = await fs.access(configuredRuntime).then(() => true).catch(() => false);
const runtimeRoot = localRuntimeExists ? configuredRuntime : null;
const modelPath = runtimeRoot
  ? path.join(runtimeRoot, "expo-kokoro", "package", "build", "kokoro-quantized.onnx")
  : "/tmp/expo-kokoro/package/build/kokoro-quantized.onnx";
const tokenizerPath = runtimeRoot
  ? path.join(runtimeRoot, "expo-kokoro", "package", "build", "tokenizer.json")
  : "/tmp/expo-kokoro/package/build/tokenizer.json";
const voicePath = runtimeRoot
  ? path.join(runtimeRoot, "kokoro-js", "package", "voices", "am_fenrir.bin")
  : "/tmp/kokoro-pkg/package/voices/am_fenrir.bin";
const ortPath = runtimeRoot
  ? path.join(runtimeRoot, "onnxruntime-web", "package", "dist", "ort.wasm.bundle.min.mjs")
  : "/tmp/onnx-web/package/dist/ort.wasm.bundle.min.mjs";
const phonemizerPath = runtimeRoot
  ? path.join(runtimeRoot, "phonemizer", "package", "dist", "phonemizer.js")
  : "/tmp/phonemizer-pkg/package/dist/phonemizer.js";

const ort = await import(pathToFileURL(ortPath).href);
const { phonemize } = await import(pathToFileURL(phonemizerPath).href);

const VOICE = "am_fenrir";
const SPEED = 0.83;
const SAMPLE_RATE = 24000;
const STYLE_DIM = 256;
const LEAD_SILENCE = 0.22;
const TRAIL_SILENCE = 0.43;

function silence(seconds) {
  return new Float32Array(Math.round(seconds * SAMPLE_RATE));
}

function concatenate(parts) {
  const result = new Float32Array(parts.reduce((total, part) => total + part.length, 0));
  let offset = 0;
  for (const part of parts) {
    result.set(part, offset);
    offset += part.length;
  }
  return result;
}

function wav(samples) {
  const dataLength = samples.length * 2;
  const buffer = Buffer.alloc(44 + dataLength);
  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataLength, 4);
  buffer.write("WAVE", 8);
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(1, 22);
  buffer.writeUInt32LE(SAMPLE_RATE, 24);
  buffer.writeUInt32LE(SAMPLE_RATE * 2, 28);
  buffer.writeUInt16LE(2, 32);
  buffer.writeUInt16LE(16, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataLength, 40);
  for (let index = 0; index < samples.length; index += 1) {
    const sample = Math.max(-1, Math.min(1, samples[index]));
    buffer.writeInt16LE(sample < 0 ? Math.round(sample * 32768) : Math.round(sample * 32767), 44 + index * 2);
  }
  return buffer;
}

function normalizeForSpeech(text) {
  return text
    .replaceAll("Neverlost", "Never lost")
    .replace(/[‘’]/g, "'")
    .replace(/[“”]/g, '"')
    .replace(/—/g, ", ")
    .replace(/\s+/g, " ")
    .trim();
}

async function phonemesFor(text) {
  const phrases = await phonemize(normalizeForSpeech(text), "en-us");
  return phrases
    .join(" ")
    .replace(/ʲ/g, "j")
    .replace(/r/g, "ɹ")
    .replace(/x/g, "k")
    .replace(/ɬ/g, "l")
    .replace(/(?<=nˈaɪn)ti(?!ː)/g, "di")
    .trim();
}

await Promise.all([modelPath, tokenizerPath, voicePath].map(async (asset) => {
  try {
    await fs.access(asset);
  } catch {
    throw new Error(`Missing Kokoro runtime asset: ${asset}`);
  }
}));

ort.env.wasm.numThreads = 1;
ort.env.wasm.proxy = false;
const session = await ort.InferenceSession.create(await fs.readFile(modelPath), {
  executionProviders: ["wasm"],
  graphOptimizationLevel: "all",
});

const tokenizerJSON = JSON.parse(await fs.readFile(tokenizerPath, "utf8"));
const vocab = tokenizerJSON.model.vocab;
const stripPattern = new RegExp(tokenizerJSON.normalizer.pattern.Regex, "g");
const voice = new Float32Array((await fs.readFile(voicePath)).buffer);

function tokenize(phonemes) {
  const normalized = phonemes.replace(stripPattern, "");
  const ids = [0, ...[...normalized].map((character) => vocab[character] ?? 0), 0];
  if (ids.length > 511) throw new Error(`Narration section exceeds Kokoro's 510-phoneme limit (${ids.length - 2}).`);
  return ids;
}

async function generate(text) {
  const ids = tokenize(await phonemesFor(text));
  const styleOffset = 256 * Math.min(Math.max(ids.length - 2, 0), 509);
  const style = voice.slice(styleOffset, styleOffset + STYLE_DIM);
  const output = await session.run({
    input_ids: new ort.Tensor("int64", BigInt64Array.from(ids, BigInt), [1, ids.length]),
    style: new ort.Tensor("float32", style, [1, STYLE_DIM]),
    speed: new ort.Tensor("float32", new Float32Array([SPEED]), [1]),
  });
  return Float32Array.from(output.waveform.data);
}

await fs.mkdir(OUTPUT, { recursive: true });
const sections = JSON.parse(await fs.readFile(NARRATION, "utf8"));
const report = { voice: VOICE, speed: SPEED, sampleRate: SAMPLE_RATE, status: "REVIEW_ONLY", sections: [] };

for (let index = 0; index < sections.length; index += 1) {
  const number = String(index + 1).padStart(2, "0");
  const destination = path.join(OUTPUT, `section-${number}.wav`);
  const speech = await generate(sections[index]);
  const samples = concatenate([silence(LEAD_SILENCE), speech, silence(TRAIL_SILENCE)]);
  await fs.writeFile(destination, wav(samples));
  const duration = samples.length / SAMPLE_RATE;
  report.sections.push({ section: index + 1, file: path.basename(destination), duration, text: sections[index] });
  console.log(`Rendered ${path.basename(destination)} (${duration.toFixed(2)} seconds)`);
}

report.totalDuration = report.sections.reduce((total, item) => total + item.duration, 0);
await fs.writeFile(path.join(OUTPUT, "render-report.json"), `${JSON.stringify(report, null, 2)}\n`);
console.log(`Kokoro narration complete: ${report.totalDuration.toFixed(2)} seconds, ${VOICE}, speed ${SPEED}.`);
