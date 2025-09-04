export const IS_AUTO_LOGIN =
  String(import.meta.env.VITE_LANGFLOW_AUTO_LOGIN ?? "false").toLowerCase() === "true";
