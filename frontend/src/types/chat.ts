export interface RawModelItem {
  provider?: string;
  vendor?: string;
  id?: string;
  model?: string;
  name?: string;
  label?: string;
  [key: string]: unknown;
}

export interface NormalizedModelItem {
  id: string;
  label: string;
  raw: RawModelItem;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  provider?: string;
  model?: string;
  streaming?: boolean;
}
