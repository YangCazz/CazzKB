import { useState, useCallback } from "react";
import { Check, Copy } from "lucide-react";

export function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  }, [text]);
  return (
    <button
      onClick={handleCopy}
      className="p-1 rounded-md transition-colors hover:bg-ds-hover"
      style={{ color: copied ? "var(--ds-success)" : "var(--ds-text-faint)" }}
      title="复制"
    >
      {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
    </button>
  );
}
