import { useEffect, useMemo, useRef, useState } from "react";
import Header from "./components/Header";
import ModelSelector from "./components/ModelSelector";
import PromptComposer from "./components/PromptComposer";
import StatusPanel from "./components/StatusPanel";
import type { ChatMessage, RawModelItem } from "./types/chat";
import {
  fetchModels,
  groupByProvider,
  normalizeModelPayload,
  streamChat
} from "./services/api";

export default function App(): JSX.Element {
  const [theme, setTheme] = useState<"light" | "dark">(
    window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
  );
  const [models, setModels] = useState<RawModelItem[]>([]);
  const [provider, setProvider] = useState<string>("");
  const [model, setModel] = useState<string>("");
  const [prompt, setPrompt] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loadingModels, setLoadingModels] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    let ignore = false;

    async function loadModels() {
      try {
        setLoadingModels(true);
        setError("");

        const payload = await fetchModels();
        if (ignore) return;

        const normalized = normalizeModelPayload(payload);
        setModels(normalized);

        const grouped = groupByProvider(normalized);
        const firstProvider = Object.keys(grouped)[0] || "";
        const firstModel = grouped[firstProvider]?.[0]?.id || "";

        setProvider(firstProvider);
        setModel(firstModel);
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : "Could not load models");
        }
      } finally {
        if (!ignore) {
          setLoadingModels(false);
        }
      }
    }

    loadModels();

    return () => {
      ignore = true;
    };
  }, []);

  const grouped = useMemo(() => groupByProvider(models), [models]);
  const providerOptions = Object.keys(grouped);
  const modelOptions = grouped[provider] || [];

  useEffect(() => {
    if (!provider && providerOptions.length) {
      setProvider(providerOptions[0]);
      return;
    }

    if (
      provider &&
      modelOptions.length &&
      !modelOptions.some((item) => item.id === model)
    ) {
      setModel(modelOptions[0].id);
    }
  }, [provider, providerOptions, modelOptions, model]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!prompt.trim() || !provider || !model || submitting) {
      return;
    }

    setError("");
    setSubmitting(true);

    const userPrompt = prompt.trim();

    const nextMessages: ChatMessage[] = [
      ...messages,
      { role: "user", content: userPrompt, provider, model },
      { role: "assistant", content: "", provider, model, streaming: true }
    ];

    setMessages(nextMessages);
    setPrompt("");

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      await streamChat({
        prompt: userPrompt,
        provider,
        model,
        signal: controller.signal,
        onChunk: (chunk: string) => {
          setMessages((current) => {
            const updated = [...current];
            const last = updated[updated.length - 1];

            if (last?.role === "assistant") {
              updated[updated.length - 1] = {
                ...last,
                content: (last.content || "") + chunk,
                streaming: true
              };
            }

            return updated;
          });
        }
      });

      setMessages((current) => {
        const updated = [...current];
        const last = updated[updated.length - 1];

        if (last?.role === "assistant") {
          updated[updated.length - 1] = {
            ...last,
            streaming: false
          };
        }

        return updated;
      });
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        setMessages((current) => {
          const updated = [...current];
          const last = updated[updated.length - 1];

          if (last?.role === "assistant") {
            updated[updated.length - 1] = {
              ...last,
              content: last.content || "Stopped by user.",
              streaming: false
            };
          }

          return updated;
        });
      } else {
        setError(err instanceof Error ? err.message : "Something went wrong");

        setMessages((current) => {
          const updated = [...current];
          const last = updated[updated.length - 1];

          if (last?.role === "assistant") {
            updated[updated.length - 1] = {
              ...last,
              content: last.content || "Unable to fetch response.",
              streaming: false
            };
          }

          return updated;
        });
      }
    } finally {
      abortRef.current = null;
      setSubmitting(false);
    }
  }

  function handleStop() {
    abortRef.current?.abort();
  }

  function handleNewChat() {
    setMessages([]);
    setError("");
  }

  function toggleTheme() {
    setTheme((current) => (current === "dark" ? "light" : "dark"));
  }

  return (
    <div className="app-shell">
      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        onNewChat={handleNewChat}
      />

      <main className="workspace">
        <section className="center-stage">
          <div className="hero">
            <h1>Choose a provider, pick a model, then stream the answer.</h1>
            <p>
              The composer stays centered like a chat-first landing screen, then
              the live response panel expands beneath it as tokens arrive from your API.
            </p>
          </div>

          <div className="composer-card">
            <ModelSelector
              provider={provider}
              setProvider={setProvider}
              model={model}
              setModel={setModel}
              providerOptions={providerOptions}
              modelOptions={modelOptions}
              loadingModels={loadingModels}
              submitting={submitting}
            />

            <PromptComposer
              prompt={prompt}
              setPrompt={setPrompt}
              loadingModels={loadingModels}
              submitting={submitting}
              provider={provider}
              model={model}
              onSubmit={handleSubmit}
              onStop={handleStop}
              error={error}
            />
          </div>

          <StatusPanel
            submitting={submitting}
            messages={messages}
            provider={provider}
            model={model}
          />
        </section>
      </main>
    </div>
  );
}
