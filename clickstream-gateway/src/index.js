/**
 * Welcome to Cloudflare Workers! This is your first worker.
 *
 * - Run `npm run dev` in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run `npm run deploy` to publish your worker
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */

export default {
  async fetch(request, env, ctx) {
    // 1. Handle CORS requests so your Python script doesn't get blocked
    if (request.method === "OPTIONS") {
      return new Response(null, { 
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
    }

    // 2. Enforce strict POST rules
    if (request.method !== "POST") {
      return new Response("Method Not Allowed.", { status: 405 });
    }

    try {
      // 3. Extract the JSON record streaming in from Python
      const eventData = await request.json();
      
      // 4. Organize data using hive-style date partitioning (year=/month=/day=)
      const now = new Date();
      const year = now.getUTCFullYear();
      const month = String(now.getUTCMonth() + 1).padStart(2, '0');
      const day = String(now.getUTCDate()).padStart(2, '0');
      
      // const fileName = `year=${year}/month=${month}/day=${day}/event-${eventData.event_id}.json`;

      const uniqueId = crypto.randomUUID(); // Built into Cloudflare Workers
      const fileName = `year=${year}/month=${month}/day=${day}/batch-${uniqueId}.json`;

      // 5. Stream the payload directly into your R2 Bucket using our environmental binding
      await env.DATA_BUCKET.put(fileName, JSON.stringify(eventData), {
        headers: { "Content-Type": "application/json" }
      });

      // 6. Return a successful 200 OK response back to your Python script
      return new Response(JSON.stringify({ success: true, saved_as: fileName }), {
        status: 200,
        headers: { 
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*"
        }
      });

    } catch (err) {
      return new Response(`Pipeline Ingestion Error: ${err.message}`, { status: 500 });
    }
  },
};
