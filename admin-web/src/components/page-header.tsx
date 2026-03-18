import { appConfig } from "@/lib/config";

type PageHeaderProps = {
  title: string;
  description: string;
};

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <header className="topbar">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <div className="badge">
        {appConfig.apiMode === "mock" ? "Mock mode" : "Live API mode"}
      </div>
    </header>
  );
}
