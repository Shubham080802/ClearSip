import assert from "node:assert/strict";
import { resetCaptureButton } from "../src/camera-ui.js";

const captureButton = { disabled: true, textContent: "Reading label…" };
resetCaptureButton(captureButton);

assert.equal(captureButton.disabled, false);
assert.equal(captureButton.textContent, "Capture and explain →");

console.log("camera UI recovery tests passed");
