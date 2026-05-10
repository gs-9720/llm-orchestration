interface PromptComposerProps {
  prompt: string;
  setPrompt: (value: string) => void;
  loadingModels: boolean;
  submitting: boolean;
  provider: string;
  model: string;
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
  onStop: () => void;
  error: string;
}

export default function PromptComposer({
  prompt,
  setPrompt,
  loadingModels,
  submitting,
  provider,
  model,
  onSubmit,
  onStop,
  error
}: PromptComposerProps): JSX.Element {
  return (
    <form className="prompt-wrap" onSubmit={onSubmit}>
      <textarea
        className="prompt-input"
        placeholder="Ask something, search docs, or send an instruction to the selected model..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        disabled={submitting}
      />

      <div className="composer-footer">
        <div className="hint-row">
          <span className="chip">stream=true</span>
          <span className="chip">/models on load</span>
          <span className="chip">Provider switcher</span>
        </div>

        <div className="action-row">
          {submitting && (
            <button className="stop-btn" type="button" onClick={onStop}>
              Stop
            </button>
          )}

          <button
            className="send-btn"
            type="submit"
            disabled={!prompt.trim() || loadingModels || !provider || !model || submitting}
          >
            {submitting ? (
              <>
                <span className="spinner" aria-hidden="true"></span>
                Searching
              </>
            ) : (
              "Search"
            )}
          </button>
        </div>
      </div>

      {error ? <p className="error">{error}</p> : null}
    </form>
  );
}
