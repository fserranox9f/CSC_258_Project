//-----------------------------------------------------
// Dashboard runtime config.
//
//   -- Adaptability --
//   Local Docker uses localhost, while GKE replaces this file with a
//   ConfigMap so the browser can call the public storage API address.
//-----------------------------------------------------

window.DASHBOARD_API_BASE_URL = window.DASHBOARD_API_BASE_URL || "http://localhost:5001";
