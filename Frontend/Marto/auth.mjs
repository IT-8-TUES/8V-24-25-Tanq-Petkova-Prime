export async function loginAndSave(username, password) {
    const r = await fetch("http://127.0.0.1:8000/api/account/token/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const d = await r.json();
  
    if (!r.ok) throw new Error(d.detail || "login failed");
  
    localStorage.setItem("access_token", d.access);
    localStorage.setItem("refresh_token", d.refresh);
    localStorage.setItem('username', username);
    console.log("✅ login OK, tokens saved");
  }
  
  async function refreshAccess() {
    const refresh = localStorage.getItem("refresh_token");
    if (!refresh) {
      console.warn("no refresh token in storage");
      return false;
    }
  
    console.log("↻ refreshing access token…");
    const r = await fetch("http://127.0.0.1:8000/api/account/token/refresh/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    const d = await r.json();
  
    if (!r.ok) {
      console.warn("refresh failed:", d);
      return false;
    }
  
    // save the new access; also save new refresh if backend rotates 
    localStorage.setItem("access_token", d.access);
    if (d.refresh) localStorage.setItem("refresh_token", d.refresh);
  
    console.log("token refreshed");
    return true;
  }
  
  export async function fetchWithAuth(url, opts = {}, retry = true) {
    const access = localStorage.getItem("access_token");
    const r1 = await fetch(url, {
      ...opts,
      headers: { ...(opts.headers || {}), Authorization: `Bearer ${access}` },
    });
  
    if (r1.status !== 401) return r1;          // success or other error
  
    console.warn(`🔒 401 on ${url}`);
  
    if (!retry || !(await refreshAccess())) {
      return r1;
    }
    // retry with fresh access
    return fetchWithAuth(url, opts, false);
  }
  