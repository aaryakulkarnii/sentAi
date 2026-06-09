import { create } from "zustand";
import type { Alert } from "@/types";

interface AlertStore {
  alerts: Alert[];
  unreadCount: number;
  setAlerts: (alerts: Alert[]) => void;
  prependAlert: (alert: Alert) => void;
  incrementUnread: () => void;
  resetUnread: () => void;
}

export const useAlertStore = create<AlertStore>((set) => ({
  alerts: [],
  unreadCount: 0,
  setAlerts: (alerts) => set({ alerts }),
  prependAlert: (alert) =>
    set((s) => ({ alerts: [alert, ...s.alerts].slice(0, 500) })),
  incrementUnread: () => set((s) => ({ unreadCount: s.unreadCount + 1 })),
  resetUnread: () => set({ unreadCount: 0 }),
}));
