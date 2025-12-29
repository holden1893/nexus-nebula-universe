export async function GET() {
  return Response.json({ ok: true, service: 'nexus-nebula', ts: new Date().toISOString() });
}
