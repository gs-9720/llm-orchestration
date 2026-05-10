import BrandMark from "./BrandMark";

interface HeaderProps {
  theme: "light" | "dark";
  onToggleTheme: () => void;
  onNewChat: () => void;
}

export default function Header({
  theme,
  onToggleTheme,
  onNewChat
}: HeaderProps): JSX.Element {
  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-mark">
          <BrandMark />
        </div>
        <div className="brand-copy">
          <strong>LLM Chat Workbench</strong>
          <span>Provider-aware streaming console</span>
        </div>
      </div>

      <div className="topbar-actions">
        <button className="ghost-btn" type="button" onClick={onNewChat}>
          New chat
        </button>

        <button
          className="theme-btn"
          type="button"
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          onClick={onToggleTheme}
        >
          {theme === "dark" ? "☼" : "◐"}
        </button>
      </div>
    </header>
  );
}
