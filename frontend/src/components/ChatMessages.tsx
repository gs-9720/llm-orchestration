import type { ChatMessage } from "../types/chat";

interface ChatMessagesProps {
  messages: ChatMessage[];
  provider: string;
  model: string;
}

export default function ChatMessages({
  messages,
  provider,
  model
}: ChatMessagesProps): JSX.Element {
  if (!messages.length) {
    return (
      <div className="empty-state">
        Your first prompt will appear here. The assistant block grows live while chunks
        stream in from the API.
      </div>
    );
  }

  return (
    <div className="messages">
      {messages.map((message, index) => (
        <article className={`message ${message.role}`} key={`${message.role}-${index}`}>
          <div className="message-meta">
            <span>{message.role === "user" ? "User" : "Assistant"}</span>
            <span>
              {message.provider || provider} · {message.model || model}
            </span>
          </div>
          <pre>{message.content || (message.streaming ? "..." : "")}</pre>
        </article>
      ))}
    </div>
  );
}
