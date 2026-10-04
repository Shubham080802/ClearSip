import assert from "node:assert/strict";
import { waitForVideoMetadata, seekReadableVideoFrame } from "../src/video-frame.js";

const ready = new EventTarget();
ready.duration = 0;
ready.currentTime = 0;
ready.readyState = 2;
await seekReadableVideoFrame(ready, 20);

const seekable = new EventTarget();
seekable.duration = 4;
seekable.currentTime = 0;
seekable.readyState = 2;
const seeked = seekReadableVideoFrame(seekable, 50);
assert.equal(seekable.currentTime, 2);
seekable.dispatchEvent(new Event("seeked"));
await seeked;

const stalled = new EventTarget();
stalled.duration = 4;
stalled.currentTime = 0;
stalled.readyState = 2;
await assert.rejects(seekReadableVideoFrame(stalled, 10), /timed out/i);

const metadata = new EventTarget();
const loading = waitForVideoMetadata(metadata, "blob:test", 50);
assert.equal(metadata.src, "blob:test");
metadata.dispatchEvent(new Event("loadedmetadata"));
await loading;

console.log("Video frame loading and timeout tests passed");
