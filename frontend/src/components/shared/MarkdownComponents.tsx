import React, { useRef, useMemo } from "react";
import type { Components } from "react-markdown";
import { CopyButton } from "./CopyButton";
import { MermaidBlock } from "./MermaidBlock";

function hasMermaidChild(children: React.ReactNode): boolean {
  return React.Children.toArray(children).some(
    (c) => React.isValidElement(c) && (c.type as any)?.displayName === "MermaidBlock"
  );
}

function extractCodeText(node: React.ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (!node) return "";
  if (React.isValidElement<{ children?: React.ReactNode }>(node)) {
    const kids = node.props.children;
    if (typeof kids === "string") return kids;
    return extractCodeText(kids);
  }
  if (Array.isArray(node)) return node.map(extractCodeText).join("");
  return "";
}

export interface CitationSource {
  source: string;
  header: string;
  excerpt: string;
}

export function createCiteComponent(
  sourcesRef: React.MutableRefObject<CitationSource[]>
): Components["cite"] {
  return function Cite({ children, ...props }: any) {
    const source = (props.source as string) || "";
    const header = (props.header as string) || "";
    const excerpt =
      typeof children === "string"
        ? children
        : React.isValidElement(children)
          ? extractCodeText(children)
          : "";

    const dedupeKey = `${source}::${excerpt.slice(0, 60)}`;
    const existing = sourcesRef.current.findIndex(
      (s) => `${s.source}::${s.excerpt.slice(0, 60)}` === dedupeKey
    );
    const num = existing >= 0 ? existing + 1 : (sourcesRef.current.push({ source, header, excerpt }), sourcesRef.current.length);

    return (
      <sup className="inline-flex items-center">
        <span
          className="inline-flex items-center justify-center min-w-[16px] h-[16px] px-[3px] rounded-full text-[10px] font-bold cursor-pointer select-none align-top transition-colors hover:opacity-80"
          style={{
            background: "var(--ds-accent)",
            color: "#fff",
          }}
          title={`${source}${header ? ` › ${header}` : ""}\n\n"${excerpt}"`}
          data-citation={num}
        >
          {num}
        </span>
      </sup>
    );
  };
}

export function useCitationComponents() {
  const sourcesRef = useRef<CitationSource[]>([]);
  sourcesRef.current = [];

  const components: Components = useMemo(() => ({
    ..._baseComponents,
    cite: createCiteComponent(sourcesRef),
  }), []);

  return { components, sources: sourcesRef };
}

// --- base components (without cite — cite is injected dynamically) ---

const _baseComponents: Components = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  pre({ children }: any) {
    if (hasMermaidChild(children)) {
      return React.Children.toArray(children).find(
        (c) => React.isValidElement(c) && (c.type as any)?.displayName === "MermaidBlock"
      ) as React.ReactElement;
    }
    const codeText = extractCodeText(children).replace(/\n$/, "");
    return (
      <div className="relative group my-3">
        <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
          <CopyButton text={codeText} />
        </div>
        <pre
          className="rounded-2xl p-4 overflow-x-auto text-[13px] leading-relaxed border"
          style={{
            background: "var(--ds-pre-bg)",
            color: "var(--ds-text)",
            borderColor: "var(--ds-border-muted)",
          }}
        >
          {children}
        </pre>
      </div>
    );
  },

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  code({ children, className, ...rest }: any) {
    const codeText = String(children).replace(/\n$/, "");
    if (className && className.includes("mermaid")) {
      return <MermaidBlock code={codeText} />;
    }
    if (!className) {
      return (
        <code
          className="px-1.5 py-0.5 rounded-md text-[13px] font-mono"
          style={{ background: "var(--ds-inline-code-bg)", color: "var(--ds-accent)" }}
          {...rest}
        >
          {children}
        </code>
      );
    }
    return <code className={className} {...rest}>{children}</code>;
  },

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  table({ children }: any) {
    return (
      <div className="overflow-x-auto my-3 rounded-xl border" style={{ borderColor: "var(--ds-border-muted)" }}>
        <table className="min-w-full text-[13px]">{children}</table>
      </div>
    );
  },

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  th({ children }: any) {
    return (
      <th
        className="px-4 py-2.5 text-left font-semibold border-b"
        style={{
          background: "var(--ds-table-head-bg)",
          color: "var(--ds-text-muted)",
          borderColor: "var(--ds-border-muted)",
        }}
      >
        {children}
      </th>
    );
  },

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  td({ children }: any) {
    return (
      <td
        className="px-4 py-2.5 border-b"
        style={{ color: "var(--ds-text)", borderColor: "var(--ds-border-muted)" }}
      >
        {children}
      </td>
    );
  },

  a({ children, href }) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="underline underline-offset-2"
        style={{ color: "var(--ds-accent)" }}
      >
        {children}
      </a>
    );
  },

  blockquote({ children }) {
    return (
      <blockquote
        className="border-l-3 pl-4 my-3 italic text-[14px]"
        style={{ borderColor: "var(--ds-accent)", color: "var(--ds-text-muted)" }}
      >
        {children}
      </blockquote>
    );
  },

  ul({ children }) {
    return <ul className="list-disc pl-6 my-2 space-y-1">{children}</ul>;
  },

  ol({ children }) {
    return <ol className="list-decimal pl-6 my-2 space-y-1">{children}</ol>;
  },

  li({ children }) {
    return <li className="text-[15px] leading-7" style={{ color: "var(--ds-text)" }}>{children}</li>;
  },

  h1({ children }) {
    return <h1 className="text-xl font-bold mt-6 mb-2 tracking-tight" style={{ color: "var(--ds-text)" }}>{children}</h1>;
  },

  h2({ children }) {
    return (
      <h2 className="text-lg font-semibold mt-5 mb-2 pb-1.5 border-b tracking-tight"
        style={{ color: "var(--ds-text)", borderColor: "var(--ds-border-muted)" }}>
        {children}
      </h2>
    );
  },

  h3({ children }) {
    return <h3 className="text-base font-semibold mt-4 mb-1.5" style={{ color: "var(--ds-text)" }}>{children}</h3>;
  },

  p({ children }) {
    return <p className="text-[15px] leading-7 my-2" style={{ color: "var(--ds-text)" }}>{children}</p>;
  },

  hr() {
    return <hr className="my-5" style={{ borderColor: "var(--ds-border-muted)" }} />;
  },

  strong({ children }) {
    return <strong className="font-semibold" style={{ color: "var(--ds-text)" }}>{children}</strong>;
  },

  em({ children }) {
    return <em className="italic" style={{ color: "var(--ds-text-muted)" }}>{children}</em>;
  },
};
