import { Layout } from "./components/Layout";
import { Sidebar } from "./components/Sidebar";
import { ChatView } from "./components/ChatView";

export function App() {
  return (
    <Layout
      sidebar={<Sidebar />}
      main={<ChatView />}
    />
  );
}
