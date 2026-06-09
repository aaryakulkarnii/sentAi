"use client";

import { useEffect } from "react";
import { alertSocket } from "@/lib/websocket";
import { useAlertStore } from "@/stores/alerts";
import type { Alert } from "@/types";

export function useAlertStream() {
  const { prependAlert, incrementUnread } = useAlertStore();

  useEffect(() => {
    alertSocket.connect("/ws/alerts");
    const unsub = alertSocket.on("new_alert", (data) => {
      prependAlert(data as Alert);
      incrementUnread();
    });
    return () => {
      unsub();
      alertSocket.disconnect();
    };
  }, [prependAlert, incrementUnread]);
}
