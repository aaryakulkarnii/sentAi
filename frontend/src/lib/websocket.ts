const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

type Handler = (data: unknown) => void;

export class SentinelWebSocket {
  private ws: WebSocket | null = null;
  private handlers = new Map<string, Set<Handler>>();
  private reconnectDelay = 2000;

  connect(path: string): void {
    this.ws = new WebSocket(`${WS_URL}${path}`);

    this.ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data) as { type: string; data: unknown };
        this.handlers.get(msg.type)?.forEach((h) => h(msg.data));
      } catch {}
    };

    this.ws.onclose = () => {
      setTimeout(() => this.connect(path), this.reconnectDelay);
    };
  }

  on(type: string, handler: Handler): () => void {
    if (!this.handlers.has(type)) this.handlers.set(type, new Set());
    this.handlers.get(type)!.add(handler);
    return () => this.handlers.get(type)?.delete(handler);
  }

  disconnect(): void {
    this.ws?.close();
  }
}

export const alertSocket = new SentinelWebSocket();
