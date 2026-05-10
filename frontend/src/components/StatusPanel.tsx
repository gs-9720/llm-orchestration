import type { ChatMessage } from "../types/chat";
import ChatMessages from "./ChatMessages";

interface StatusPanelProps {
  submitting: boolean;
  messages: ChatMessage[];
  provider: string;
  model: string;
}

export default function StatusPanel({
  submitting,
  messages,
  provider,
  model
}: StatusPanelProps): JSX.Element {
  return (
    <section className="status-panel" aria-live="polite">
      <div className="status-head">
        <div>
          <strong>Conversation</strong>
          <span> Streaming transcript from your backend </span>
        </div>

        {submitting ? (
          <div className="loading-line">
            <span className="loading-dot"></span>
            Receiving tokens...
          </div>
        ) : (
          <span>{messages.length ? `${messages.length} messages` : "No messages yet"}</span>
        )}
      </div>

      <ChatMessages messages={messages} provider={provider} model={model} />
    </section>
  );
}
