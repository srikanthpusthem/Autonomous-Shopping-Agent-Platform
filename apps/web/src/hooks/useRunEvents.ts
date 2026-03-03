import { useEffect, useRef, useState } from "react";
import type { AgentEvent } from "../types";
import { buildRunEventsWsUrl } from "../lib/api";

export function useRunEvents(runId: string | null) {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const retryCount = useRef(0);

  useEffect(() => {
    if (!runId) {
      setEvents([]);
      setConnectionError(null);
      return;
    }

    let active = true;
    let socket: WebSocket | null = null;
    let reconnectTimer: number | undefined;

    const connect = () => {
      if (!active) {
        return;
      }
      socket = new WebSocket(buildRunEventsWsUrl(runId));

      socket.onopen = () => {
        retryCount.current = 0;
        setConnectionError(null);
      };

      socket.onmessage = (message) => {
        try {
          const parsed = JSON.parse(message.data) as AgentEvent;
          setEvents((prev) => [...prev, parsed]);
        } catch {
          setConnectionError("Received invalid event payload");
        }
      };

      socket.onerror = () => {
        setConnectionError("WebSocket connection error");
      };

      socket.onclose = () => {
        if (!active) {
          return;
        }
        retryCount.current += 1;
        const delay = Math.min(3000, retryCount.current * 600);
        reconnectTimer = window.setTimeout(connect, delay);
      };
    };

    connect();

    return () => {
      active = false;
      if (reconnectTimer) {
        window.clearTimeout(reconnectTimer);
      }
      socket?.close();
    };
  }, [runId]);

  return { events, connectionError };
}
