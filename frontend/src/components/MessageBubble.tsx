import { useCallback, useState } from "react";
import type { Message } from "../types";
import Markdown from "react-markdown";
import type { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { Check, Copy } from "lucide-react";

function CopyBtn({ text }: { text: string }) {
  const [ok, setOk] = useState(false);
  const cp = useCallback(() => {
    navigator.clipboard.writeText(text);
    setOk(true); setTimeout(() => setOk(false), 1600);
  }, [text]);
  return (
    <button onClick={cp} className="p-1 rounded-md transition-colors hover:bg-ds-hover" style={{ color: "var(--ds-text-faint)" }}>
      {ok ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
    </button>
  );
}

const mdComponents: Components = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  cite({ children, ...props }: any) {
    const source = (props.source as string) || "";
    const header = (props.header as string) || "";
    const body = (props.node?.children?.[0]?.value as string) || "";
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 mx-0.5 rounded-md align-middle cursor-help" title={`来源: ${source}${header ? ` › ${header}` : ""}`}
        style={{ background: "var(--ds-accent-soft)", color: "var(--ds-accent)", fontSize: 12 }}>
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
        {body}{source ? <span className="opacity-50 font-mono ml-0.5">{source}</span> : null}
      </span>
    );
  },
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  pre({ children }: any) {
    return (
      <div className="relative group my-3">
        <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button className="text-[11px] font-medium px-2 py-0.5 rounded-md" style={{ background: "var(--ds-surface-subtle)", color: "var(--ds-text-muted)" }}
            onClick={(e) => { const code = e.currentTarget.parentElement?.parentElement?.querySelector("code")?.textContent || ""; navigator.clipboard.writeText(code); }}>
            复制
          </button>
        </div>
        <pre className="rounded-2xl p-4 overflow-x-auto text-[13px] leading-relaxed border" style={{ background: "var(--ds-pre-bg)", color: "var(--ds-text)", borderColor: "var(--ds-border-muted)" }}>
          {children}
        </pre>
      </div>
    );
  },
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  code({ children, className, ...rest }: any) {
    if (!className) return <code className="px-1.5 py-0.5 rounded-md text-[13px] font-mono" style={{ background: "var(--ds-inline-code-bg)", color: "var(--ds-accent)" }} {...rest}>{children}</code>;
    return <code className={className} {...rest}>{children}</code>;
  },
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  table({ children }: any) { return <div className="overflow-x-auto my-3 rounded-xl border" style={{ borderColor: "var(--ds-border-muted)" }}><table className="min-w-full text-[13px]">{children}</table></div>; },
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  th({ children }: any) { return <th className="px-4 py-2.5 text-left font-semibold border-b" style={{ background: "var(--ds-table-head-bg)", color: "var(--ds-text-muted)", borderColor: "var(--ds-border-muted)" }}>{children}</th>; },
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  td({ children }: any) { return <td className="px-4 py-2.5 border-b" style={{ color: "var(--ds-text)", borderColor: "var(--ds-border-muted)" }}>{children}</td>; },
  a({ children, href }) { return <a href={href} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2" style={{ color: "var(--ds-accent)" }}>{children}</a>; },
  blockquote({ children }) { return <blockquote className="border-l-3 pl-4 my-3 italic text-[14px]" style={{ borderColor: "var(--ds-accent)", color: "var(--ds-text-muted)" }}>{children}</blockquote>; },
  ul({ children }) { return <ul className="list-disc pl-6 my-2 space-y-1">{children}</ul>; },
  ol({ children }) { return <ol className="list-decimal pl-6 my-2 space-y-1">{children}</ol>; },
  li({ children }) { return <li className="text-[15px] leading-7" style={{ color: "var(--ds-text)" }}>{children}</li>; },
  h1({ children }) { return <h1 className="text-xl font-bold mt-6 mb-2 tracking-tight" style={{ color: "var(--ds-text)" }}>{children}</h1>; },
  h2({ children }) { return <h2 className="text-lg font-semibold mt-5 mb-2 pb-1.5 border-b tracking-tight" style={{ color: "var(--ds-text)", borderColor: "var(--ds-border-muted)" }}>{children}</h2>; },
  h3({ children }) { return <h3 className="text-base font-semibold mt-4 mb-1.5" style={{ color: "var(--ds-text)" }}>{children}</h3>; },
  p({ children }) { return <p className="text-[15px] leading-7 my-2" style={{ color: "var(--ds-text)" }}>{children}</p>; },
  hr() { return <hr className="my-5" style={{ borderColor: "var(--ds-border-muted)" }} />; },
  strong({ children }) { return <strong className="font-semibold" style={{ color: "var(--ds-text)" }}>{children}</strong>; },
  em({ children }) { return <em className="italic" style={{ color: "var(--ds-text-muted)" }}>{children}</em>; },
};

export function UserBubble({ msg }: { msg: Message }) {
  return (
    <div className="ds-user-message group flex justify-end mb-8 pr-1">
      <div className="min-w-0 max-w-[75%]">
        <div className="whitespace-pre-wrap break-words text-[15px] leading-[1.58] font-medium px-5 py-3 rounded-[22px]"
          style={{ background: "var(--ds-bubble-user)", color: "var(--ds-bubble-user-fg)" }}>
          {msg.content}
        </div>
        <div className="mt-1.5 flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <CopyBtn text={msg.content} />
        </div>
      </div>
    </div>
  );
}

export function AssistantBubble({ msg }: { msg: Message }) {
  return (
    <div className="ds-assistant-message group mb-8">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: "var(--ds-accent)" }}>
          <span className="text-[10px] font-bold text-white">K</span>
        </div>
        <span className="text-[13px] font-medium ds-no-select" style={{ color: "var(--ds-text-muted)" }}>CazzKB</span>
        {msg.responseTime != null && (
          <span className="text-[12px] tabular-nums ml-1.5" style={{ color: "var(--ds-text-faint)" }}>
            {msg.responseTime < 1 ? `${Math.round(msg.responseTime * 1000)}ms` : `${msg.responseTime}s`}
          </span>
        )}
      </div>
      <div className="pl-8">
        <div className="text-[15px] leading-7" style={{ color: "var(--ds-text)" }}>
          <Markdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]} components={mdComponents}>
            {msg.content}
          </Markdown>
        </div>
        <div className="mt-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <CopyBtn text={msg.content} />
        </div>
      </div>
    </div>
  );
}
