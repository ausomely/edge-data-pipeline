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
  async fetch(request, env) {
    // 1. Handle CORS/Methods safely
    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    try {
      // Check if the bucket binding actually exists
      if (!env.DATA_BUCKET) {
        return new Response(JSON.stringify({ error: "R2 Bucket binding 'DATA_BUCKET' not found." }), { status: 500 });
      }

      // 2. Extract the incoming payload as an ArrayBuffer
      const buffer = await request.arrayBuffer();
      
      if (!buffer || buffer.byteLength === 0) {
        return new Response(JSON.stringify({ error: "Empty binary payload" }), { status: 400 });
      }

      // 💡 THE FIX: Wrap the raw ArrayBuffer into a typed Uint8Array view 
      // This prevents Cloudflare from misinterpreting raw memory streams.
      const binaryData = new Uint8Array(buffer);

      // 3. Construct precise path names
      const now = new Date();
      const dateStr = now.toISOString().split('T')[0]; // YYYY-MM-DD
      const timestamp = now.toISOString().replace(/[:.]/g, "-");
      const uniqueId = Math.random().toString(36).substring(2, 8);
      
      // Notice the .parquet extension here
      const objectKey = `raw/clickstream/dt=${dateStr}/${timestamp}_${uniqueId}.parquet`;

      // 4. Persist directly to Cloudflare R2
      await env.DATA_BUCKET.put(objectKey, binaryData, {
        httpMetadata: {
          contentType: "application/octet-stream",
        }
      });

      return new Response(JSON.stringify({ 
        success: true, 
        key: objectKey 
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });

    } catch (error) {
      // If it fails, return the EXACT error message to your Python terminal log
      return new Response(JSON.stringify({ 
        error: "Internal Error within Worker",
        details: error.message,
        stack: error.stack
      }), { 
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
  }
};