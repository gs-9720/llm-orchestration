import type { NormalizedModelItem } from "../types/chat";

interface ModelSelectorProps {
  provider: string;
  setProvider: (value: string) => void;
  model: string;
  setModel: (value: string) => void;
  providerOptions: string[];
  modelOptions: NormalizedModelItem[];
  loadingModels: boolean;
  submitting: boolean;
}

export default function ModelSelector({
  provider,
  setProvider,
  model,
  setModel,
  providerOptions,
  modelOptions,
  loadingModels,
  submitting
}: ModelSelectorProps): JSX.Element {
  return (
    <div className="model-row">
      <div className="field">
        <label htmlFor="provider">Provider</label>
        <select
          id="provider"
          className="select"
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          disabled={loadingModels || submitting}
        >
          {providerOptions.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor="model">Model</label>
        <select
          id="model"
          className="select"
          value={model}
          onChange={(e) => setModel(e.target.value)}
          disabled={loadingModels || submitting}
        >
          {modelOptions.map((item) => (
            <option key={item.id} value={item.id}>
              {item.label}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label>Status</label>
        <div className="select select-static">
          {loadingModels ? "Loading models..." : `${providerOptions.length || 0} providers`}
        </div>
      </div>
    </div>
  );
}
