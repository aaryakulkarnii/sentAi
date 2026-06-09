"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { alertSocket } from "@/lib/websocket";
import { useAlertStore } from "@/stores/alerts";
import type { Alert } from "@/types";

/** Subscribes to real-time alert WebSocket and syncs React Query cache. */
export default function AlertStreamProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const { prependAlert, incrementUnread } = useAlertStore();

  useEffect(() => {
    alertSocket.connect("/ws/alerts");
    const unsub = alertSocket.on("new_alert", (data) => {
      const alert = data as Alert;
      prependAlert(alert);
      incrementUnread();
      queryClient.setQueryData<Alert[]>(["alerts"], (old = []) => {
        if (old.some((a) => a.id === alert.id)) return old;
        return [alert, ...old];
      });
      queryClient.setQueryData<Alert[]>(["alerts", "all"], (old = []) => {
        if (old.some((a) => a.id === alert.id)) return old;
        return [alert, ...old];
      });
    });
    return () => {
      unsub();
      alertSocket.disconnect();
    };
  }, [prependAlert, incrementUnread, queryClient]);

  return <>{children}</>;
}
