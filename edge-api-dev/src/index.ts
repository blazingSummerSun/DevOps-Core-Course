/**
 * Welcome to Cloudflare Workers! This is your first worker.
 *
 * - Run `npm run dev` in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run `npm run deploy` to publish your worker
 *
 * Bind resources to your worker in `wrangler.jsonc`. After adding bindings, a type definition for the
 * `Env` object can be regenerated with `npm run cf-typegen`.
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */

export interface Env {
  APP_NAME: string;
  COURSE_NAME: string;
  API_TOKEN: string;
  ADMIN_EMAIL: string;
  SETTINGS: KVNamespace;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    // Вывод в логи (Task 5)
    console.log(`[${request.method}] ${url.pathname} from ${request.cf?.country || 'Unknown'}`);

    // 1. Health endpoint (Task 2)
    if (url.pathname === "/health") {
      return Response.json({ status: "ok", app: env.APP_NAME });
    }

    // 2. Edge metadata endpoint (Task 3)
    if (url.pathname === "/edge") {
      return Response.json({
        message: "Edge execution metadata",
        colo: request.cf?.colo, // Дата-центр (например, FRA, LHR)
        country: request.cf?.country,
        city: request.cf?.city,
        asn: request.cf?.asn,
        httpProtocol: request.cf?.httpProtocol,
        tlsVersion: request.cf?.tlsVersion,
      });
    }

    // 3. KV Persistent counter (Task 4)
    if (url.pathname === "/counter") {
      // Получаем текущее значение или 0
      const raw = await env.SETTINGS.get("visits");
      const visits = Number(raw ?? "0") + 1;

      // Записываем новое значение
      await env.SETTINGS.put("visits", String(visits));

      return Response.json({
        visits,
        note: "This value persists at the Edge!",
        admin: env.ADMIN_EMAIL // Демонстрация использования секрета
      });
    }

    // Default route
    if (url.pathname === "/") {
      return Response.json({
        app: env.APP_NAME,
        course: env.COURSE_NAME,
        message: "Hello Edge World!",
        timestamp: new Date().toISOString(),
      });
    }

    return new Response("Not Found", { status: 404 });
  },
} satisfies ExportedHandler<Env>;
