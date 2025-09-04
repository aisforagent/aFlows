// Runtime safety check for auto_login
export function checkAutoLoginDisabled(): boolean {
  return localStorage.getItem("AUTO_LOGIN_DISABLED") === "1";
}

// Initialize auto_login guard on app boot
export function initializeAutoLoginGuard() {
  // If auto_login is disabled, set the flag immediately
  if (checkAutoLoginDisabled()) {
    console.log("Auto-login disabled - skipping initialization");
    return;
  }
  
  // Optional: Check if we're in a development environment
  if (import.meta.env.DEV) {
    console.log("Auto-login guard initialized");
  }
}

// Clear the disabled flag (useful for testing or re-enabling)
export function clearAutoLoginDisabled() {
  localStorage.removeItem("AUTO_LOGIN_DISABLED");
}
