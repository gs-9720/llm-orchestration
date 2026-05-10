import type { NormalizedModelItem, RawModelItem } from "../types/chat";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

type ModelPayload =
  | RawModelItem[]
  | { models?: RawModelItem[]; data?: RawModelItem[] }
  | unknown;

interface StreamChatParams {
  prompt: string;
  provider: string;
  model: string;
  signal: AbortSignal;
  onChunk: (chunk: string) => void;
}

export async function fetchModels(): Promise<ModelPayload> {
  const response = await fetch(`${API_BASE}/models`);

  if (!response.ok) {
    throw new Error("Failed to load models");
  }

  return response.json();
}

export function normalizeModelPayload(payload: ModelPayload): RawModelItem[] {
  if (Array.isArray(payload)) return payload;

  if (
    payload &&
    typeof payload === "object" &&
    Array.isArray((payload as { models?: RawModelItem[] }).models)
  ) {
    return (payload as { models: RawModelItem[] }).models;
  }

  if (payload && typeof payload === "object" && Array.isArray((payload as { data?: RawModelItem[] }).data)) {
    return (payload as {  data: RawModelItem[] }).data;
    //return [];
  }

  return [];
}

export function groupByProvider(
  models: RawModelItem[]
): Record<string, NormalizedModelItem[]> {
  const grouped: Record<string, NormalizedModelItem[]> = {};

  models.forEach((item) => {
    const provider = item.provider || item.vendor || "default";
    const id = item.id || item.model || item.name || "unknown-model";
    const label = item.label || item.name || item.model || item.id || "Unknown Model";

    if (!grouped[provider]) {
      grouped[provider] = [];
    }

    grouped[provider].push({
      id,
      label,
      raw: item
    });
  });

  return grouped;
}

export async function streamChat({
  prompt,
  provider,
  model,
  signal,
  onChunk
}: StreamChatParams): Promise<void> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    signal,
    body: JSON.stringify({
      message: prompt,
      provider,
      model,
      stream: true
    })
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }

  if (!response.body) {
    const fallback = await response.text();
    onChunk(fallback);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n");
    buffer = parts.pop() || "";

    parts.forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed) return;

      if (trimmed.startsWith("")) {
        const raw = trimmed.replace(/^\s*/, "");
        if (raw === "[DONE]") return;

        try {
          const parsed = JSON.parse(raw) as Record<string, unknown>;
          const token =
            (parsed.delta as string) ||
            (parsed.token as string) ||
            (parsed.content as string) ||
            (parsed.message as string) ||
            "";

          if (token) {
            onChunk(token);
          }
        } catch {
          onChunk(raw);
        }
      } else {
        onChunk(trimmed);
      }
    });
  }

  if (buffer.trim()) {
    onChunk(buffer.trim());
  }
}
