import assert from "node:assert/strict";
import { resetCaptureButton, finishCapture } from "../src/camera-ui.js";

const captureButton = { disabled: true, textContent: "Reading label…" };
resetCaptureButton(captureButton);

assert.equal(captureButton.disabled, false);
assert.equal(captureButton.textContent, "Capture and explain →");

let closed = 0;
const status = { textContent: "Reading label…" };
finishCapture(false, () => { closed += 1; }, status);
assert.equal(closed, 0, "camera stays open for another attempt after no match");
assert.match(status.textContent, /try again/i);
finishCapture(true, () => { closed += 1; }, status);
assert.equal(closed, 1, "camera closes after a usable match");

console.log("camera UI recovery tests passed");
