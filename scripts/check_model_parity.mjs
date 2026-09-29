// Run against an exported candidate; this is converter parity, not device QA.
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import * as tf from "@tensorflow/tfjs";

const directory = path.resolve(process.argv[2] || "ml-artifacts/candidate");
const modelJson = JSON.parse(await fs.readFile(path.join(directory,"model.json"),"utf8"));
const parity = JSON.parse(await fs.readFile(path.join(directory,"parity.json"),"utf8"));
const specs = [];
const parts = [];
for (const group of modelJson.weightsManifest) {
  specs.push(...group.weights);
  for (const filename of group.paths) {
    const file = path.resolve(directory,filename);
    assert.ok(file.startsWith(`${directory}${path.sep}`));
    parts.push(await fs.readFile(file));
  }
}
const weights = Buffer.concat(parts);
const model = await tf.loadLayersModel(tf.io.fromMemory({modelTopology:modelJson.modelTopology, weightSpecs:specs,
  weightData:weights.buffer.slice(weights.byteOffset,weights.byteOffset+weights.byteLength)}));
const count = parity.shape.reduce((a,b)=>a*b,1);
const input = tf.tensor(Float32Array.from({length:count},(_,i)=>(i/(count-1))*2-1), parity.shape);
let output;
try {
  output = model.predict(input);
  const scores = Array.from(await output.data());
  assert.equal(scores.length,parity.scores.length);
  const difference = Math.max(...scores.map((score,index)=>Math.abs(score-parity.scores[index])));
  assert.ok(difference <= 0.01,`Conversion parity failed: ${difference}`);
  console.log(`Python / TF.js CPU score difference: ${difference}. Browser/device QA still required.`);
} finally {
  input.dispose(); output?.dispose(); model.dispose();
}
