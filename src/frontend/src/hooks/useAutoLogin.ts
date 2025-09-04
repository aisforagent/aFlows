import { useEffect, useRef } from "react";
import { IS_AUTO_LOGIN } from "@/config/flags";
import api from "@/lib/api";

export function useAutoLogin() {
  const triedRef = useRef(false);

  useEffect(() => {
    // Check if auto_login is disabled globally
    if (localStorage.getItem("AUTO_LOGIN_DISABLED") === "1") {
      return;
    }

    if (!IS_AUTO_LOGIN || triedRef.current) return;
    triedRef.current = true;

    api.get("/v1/auto_login")
      .then(/* handle success */)
      .catch(err => {
        // If backend returns 400/404/405, permanently disable client attempts
        if ([400, 404, 405].includes(err?.response?.status)) {
          // Set global flag so other tabs don't retry
          window.localStorage.setItem("AUTO_LOGIN_DISABLED", "1");
        }
      });
  }, []);
}
