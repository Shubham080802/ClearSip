export const CAPTURE_BUTTON_LABEL = "Capture and explain →";

export function resetCaptureButton(button) {
  button.disabled = false;
  button.textContent = CAPTURE_BUTTON_LABEL;
}

export function setCaptureProcessing(button) {
  button.disabled = true;
  button.textContent = "Reading label…";
}

export function finishCapture(matched, stopCamera, status) {
  if (matched) {
    stopCamera();
  } else {
    status.textContent = "No reliable match yet. Reposition the drink and try again, or search by name.";
  }
}
