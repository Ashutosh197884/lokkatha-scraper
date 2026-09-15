/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the Lokkatha API server (no trailing slash), e.g. https://api.example.com.
   *  Leave unset in local dev — vite proxies /api to 127.0.0.1:8000. */
  readonly VITE_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
