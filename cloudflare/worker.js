import { WorkerEntrypoint } from "cloudflare:workers";

// Function for getting a request from the cache or going to origin.
async function fetchCacheOrOrigin(request, ctx) {
  // Check if data is in cache
  const cacheUrl = typeof request == 'string' ? new URL(request) : new URL(request.url);
  const cacheKey = new Request(cacheUrl.toString());
  const cache = caches.default;
  let response = await cache.match(cacheKey);
  // Data is not in the cache already
  if (!response) {
    // Fetch the request.
    response = await fetch(request);
    console.log(`Fetching Origin for Cache ${cacheUrl.toString()}`);
    // Cache it
    response = new Response(response.body, response);
    ctx.waitUntil(cache.put(cacheKey, response.clone()));
  }
  else
    console.log(`Data was in cache already for ${cacheUrl.toString()}`);

  return response;
};

export class APILookup extends WorkerEntrypoint {
  async checkAccount(account) {
    if (account == 0) {
      return {};
    }
    return await fetchCacheOrOrigin(`https://api.scamguard.app/check/${account}`);
  };
  async getBanDetails(account) {
    if (account == 0) {
      return {};
    }
    return await fetchCacheOrOrigin(`https://api.scamguard.app/ban/${account}`);
  };
  async getBanStats() {
    return await fetchCacheOrOrigin(`https://api.scamguard.app/bans`);
  }
};

export default {
  async fetch(request, env, ctx) {
    // Check if authorization is enabled
    const authRequired = (env.REQUIRE_AUTH === "true");
    if (authRequired === false) {
      return fetchCacheOrOrigin(request, ctx);
    }
    
    // Check for Auth Header
    const authHeader = request.headers.get("Authorization");
    if (authHeader !== null) {
      // Extract API Key
      const tokenHolder = authHeader.toString().split(" ");
      // Make sure it's in the right format of Bearer <token>
      if (tokenHolder.length >= 2) {
        // Check if this token exists
        let task = await env.TOKEN_LIST.get(tokenHolder[1]);
        
        // Key is valid!
        if (task)
          return await fetchCacheOrOrigin(request, ctx);
      }
    }

    // Incorrect key supplied. Reject the request.
    return new Response(JSON.stringify({msg: "you have provided an invalid key", status: false}), {
      status: 403,
      headers: new Headers({"content-type": "application/json"})
    });
  },
};
