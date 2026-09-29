import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { rankOcrCandidates, selectVisualCandidates, mergeCandidates, contradictsLabel, readBarcode, classifyImage } from "../src/recognition.js";

const python = process.env.CLEARSIP_TEST_PYTHON || "python";
const catalog = JSON.parse(execFileSync(python, ["-c", "import json; from api.recognition import recognition_catalog; print(json.dumps(recognition_catalog()))"], { encoding:"utf8" }));
for (const row of catalog.filter((row) => row.trainable)) {
  const matches = rankOcrCandidates(row.name, catalog);
  assert.ok(matches.some((match) => match.id === row.id), `Full label name must remain reachable: ${row.id}`);
  const release = { status:"validated", validation_passed:true, labels:[row.id,"__unknown__"], score_threshold:0.8, margin_threshold:0.15 };
  assert.equal(selectVisualCandidates([0.99,0.01],release,catalog)[0].id,row.id, "every specific drink can map a future image model output to its catalog ID");
  assert.deepEqual(selectVisualCandidates([0.4,0.6],release,catalog),[], "unknowns rejected");
  assert.deepEqual(selectVisualCandidates([0.81,0.79],release,catalog),[], "ambiguous scores rejected");
  assert.deepEqual(selectVisualCandidates([NaN,0.01],release,catalog),[]);
  assert.deepEqual(selectVisualCandidates([0.99,0.01],{...release,status:"candidate"},catalog),[]);
  assert.deepEqual(selectVisualCandidates([0.99,0.01],{...release,training_mode:"research-only"},catalog),[], "changing status alone cannot activate a research-only model");
  assert.deepEqual(selectVisualCandidates([0.99,0.01],{...release,evaluation_status:"deferred"},catalog),[]);
}
assert.ok(contradictsLabel("Powerade Grape", "POWER ADE ZERO SUGAR"));
assert.ok(!rankOcrCandidates("Powerade Zero Sugar Mixed Berry", catalog).some((row) => row.id === "powerade-grape"));
assert.equal(rankOcrCandidates("Powerade Zero Sugar Mixed Berry",catalog)[0].id,"powerade-zero-mixed-berry");
assert.deepEqual(rankOcrCandidates("unrelated scene",catalog),[]);
assert.equal(mergeCandidates([{id:"a",evidence:"visual"}],[{id:"a",evidence:"text"}]).length,1);
assert.equal(await readBarcode({}),null,"unsupported native barcode reader remains optional");
globalThis.fetch = async () => ({ok:true,json:async()=>({status:"awaiting_training_images",validation_passed:false,labels:[]})});
assert.deepEqual(await classifyImage({},catalog),{candidates:[],status:"awaiting_training_images"},"no pretrained generic model can masquerade as a trained drink recognizer");
for (const fields of [{training_mode:"research-only"}, {evaluation_status:"deferred"}]) {
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    assert.equal(calls, 1, "Unapproved artifacts must not fetch model weights");
    return {ok:true,json:async()=>({status:"validated",validation_passed:true,labels:["pepsi","__unknown__"],...fields})};
  };
  const isolated = await import(`../src/recognition.js?deferred-${Object.keys(fields)[0]}`);
  assert.deepEqual(await isolated.classifyImage({},catalog),{candidates:[],status:"awaiting_training_images"});
  assert.equal(calls, 1);
}
console.log(`${catalog.length} targets: all concrete variants support stable-ID visual mapping; unknown/conflict rejection passed`);
