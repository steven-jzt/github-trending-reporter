// Cloudflare Worker — DeepSeek API 中转
// 部署后把 WORKER_URL 设为你的 .env 中的 OPENAI_BASE_URL

export default {
  async fetch(request) {
    const DEEPSEEK = "https://api.deepseek.com";
    const url = new URL(request.url);
    const targetUrl = DEEPSEEK + url.pathname + url.search;

    const headers = new Headers(request.headers);
    headers.set("Host", "api.deepseek.com");

    const modified = new Request(targetUrl, {
      method: request.method,
      headers,
      body: request.body,
      redirect: "follow",
    });

    return fetch(modified);
  },
};
