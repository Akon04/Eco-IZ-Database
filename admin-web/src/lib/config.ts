type ApiMode = "mock" | "live";

function readApiMode(): ApiMode {
  const value = process.env.NEXT_PUBLIC_API_MODE;
  return value === "live" ? "live" : "mock";
}

export const appConfig = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  apiMode: readApiMode(),
};

export function isMockMode() {
  return appConfig.apiMode === "mock";
}
