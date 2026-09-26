export const MAX_IMAGE_BYTES = 12 * 1024 * 1024;
export const MAX_VIDEO_BYTES = 80 * 1024 * 1024;

const fileLimits = {
  image: { maxBytes: MAX_IMAGE_BYTES, mediaType: "image", label: "image" },
  video: { maxBytes: MAX_VIDEO_BYTES, mediaType: "video", label: "video" },
};

function megabytes(bytes) {
  return Math.round(bytes / 1024 / 1024);
}

export function validateScanFile(file, kind) {
  const limit = fileLimits[kind];
  if (!limit) throw new Error(`Unsupported scan type: ${kind}`);
  if (!file) return `Choose a ${limit.label} first.`;
  if (!file.type?.startsWith(`${limit.mediaType}/`)) return `Choose a supported ${limit.label} file.`;
  if (!file.size) return `That ${limit.label} file is empty.`;
  if (file.size > limit.maxBytes) return `Choose a ${limit.label} smaller than ${megabytes(limit.maxBytes)} MB.`;
  return null;
}
