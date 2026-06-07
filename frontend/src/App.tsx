import { useState } from "react";
import Layout from "./components/Layout";
import Sidebar from "./components/Sidebar";
import ChatArea from "./components/ChatArea";

export default function App() {
  const [selectedKb, setSelectedKb] = useState<{ id: number; name: string } | null>(null);

  return (
    <Layout
      sidebar={
        <Sidebar
          selectedId={selectedKb?.id ?? null}
          onSelect={(id) => setSelectedKb({ id, name: "" })}
        />
      }
      main={
        <ChatArea
          kbId={selectedKb?.id ?? null}
          kbName={selectedKb?.name ?? ""}
        />
      }
    />
  );
}
