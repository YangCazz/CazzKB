import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

interface Props {
  code: string;
}

let _mermaidInitialized = false;

function initMermaid() {
  if (_mermaidInitialized) return;
  mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    themeVariables: {
      primaryColor: "#e8f4ff",
      primaryTextColor: "#1a1a2e",
      primaryBorderColor: "#0088ff",
      lineColor: "#b0b8c4",
      secondaryColor: "#f0f4ff",
      tertiaryColor: "#f7f9fc",
      background: "transparent",
      mainBkg: "#ffffff",
      nodeBorder: "#0088ff",
      clusterBkg: "#f8fafd",
      clusterBorder: "#dce3eb",
      titleColor: "#1a1a2e",
      edgeLabelBackground: "#ffffff",
      nodeTextColor: "#1a1a2e",
      fontSize: "14px",
      fontFamily: "Inter, system-ui, -apple-system, sans-serif",
    },
  });
  _mermaidInitialized = true;
}

export function MermaidBlock({ code }: Props) {
  const idRef = useRef(`mb-${Math.random().toString(36).slice(2, 9)}`);
  const [svg, setSvg] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    initMermaid();
    mermaid
      .render(idRef.current, code)
      .then(({ svg: rendered }) => {
        if (!cancelled) {
          setSvg(rendered);
          setError(false);
        }
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => { cancelled = true; };
  }, [code]);

  if (error) {
    return (
      <pre
        className="rounded-2xl p-4 overflow-x-auto text-[13px] leading-relaxed border my-3"
        style={{
          background: "var(--ds-pre-bg)",
          color: "var(--ds-text)",
          borderColor: "var(--ds-border-muted)",
        }}
      >
        <code>{code}</code>
      </pre>
    );
  }

  return (
    <div
      className="my-4 flex justify-center overflow-x-auto"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}

MermaidBlock.displayName = "MermaidBlock";
