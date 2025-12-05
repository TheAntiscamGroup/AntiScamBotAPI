import { WorkerEntrypoint } from "cloudflare:workers";

// Function for getting a request from the cache or going to origin.
async function fetchCacheOrOrigin(request, ctx) {
  // Check if data is in cache
  const cacheUrl = typeof request === 'string' ? new URL(request) : new URL(request.url);
  const cacheKey = new Request(cacheUrl.toString());
  const cache = caches.default;
  let response = await cache.match(cacheKey);
  // Data is not in the cache already
  if (!response) {
    // Fetch the request.
    response = await fetch(request, );
    console.log(`Fetching Origin for Cache ${cacheUrl.toString()}`);
    // Cache it
    response = new Response(response.body, response);
    ctx.waitUntil(cache.put(cacheKey, response.clone()));
  }

  return response;
};

export class APILookup extends WorkerEntrypoint {
  makeRequest(url) {
    return new Request(url, {headers: {
      "Authorization": `Bearer ${this.env.SERVICE_LOOKUP_KEY}`
    }});
  };
  async makeSGRequest(type, account) {
    if (account == "" || account == "0") {
      return {valid: false};
    }
    const request = await fetchCacheOrOrigin(this.makeRequest(`https://api.scamguard.app/${type}/${account}`), this.ctx);
    if (request.ok)
      return await request.json();
    else
      return {valid: false, error: true, status: request.status, code: request.code};
  }
  async checkAccount(account) {
    return await this.makeSGRequest("check", account);
  };
  async getBanDetails(account) {
    return await this.makeSGRequest("ban", account);
  };
  async getBanStats() {
    const request = await fetchCacheOrOrigin(this.makeRequest(`https://api.scamguard.app/bans`), this.ctx);
    if (request.ok)
      return await request.json();
    else
      return {error: true, status: request.status, code: request.code };
  };
};

export default class extends WorkerEntrypoint {
  async fetch(request, env, ctx) {
    // Check if authorization is enabled
    const authRequired = (this.env.REQUIRE_AUTH === "true");
    if (authRequired === false) {
      return fetchCacheOrOrigin(request, this.ctx);
    }

    // Check for Auth Header
    const authHeader = request.headers.get("Authorization");
    if (authHeader !== null) {
      // Extract API Key
      const tokenHolder = authHeader.toString().split(" ");
      // Make sure it's in the right format of Bearer <token>
      if (tokenHolder.length >= 2) {
        // Check if this token exists
        let task = await this.env.TOKEN_LIST.get(tokenHolder[1]);
        
        // Key is valid!
        if (task)
          return await fetchCacheOrOrigin(request, this.ctx);
      }
    }

    // Incorrect key supplied. Reject the request.
    return new Response(JSON.stringify({msg: "you have provided an invalid key", status: false}), {
      status: 403,
      headers: new Headers({"content-type": "application/json"})
    });
  };
};
