import * as SecureStore from 'expo-secure-store';
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { Platform } from 'react-native';

import { api, setToken } from '../api/client';
import type { Building, Lot, Meta, PermitType, ProfileChanges, Session, User } from '../api/types';

const TOKEN_KEY = 'unt_parking_token';

export type Tab = 'map' | 'profile';

interface AppState {
  ready: boolean;
  user: User | null;
  meta: Meta | null;
  buildings: Building[];
  lots: Lot[];
  campusError: string | null;
  tab: Tab;
  setTab: (tab: Tab) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, permit: PermitType) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  updateProfile: (changes: ProfileChanges) => Promise<void>;
  loadCampus: () => Promise<void>;
}

const Ctx = createContext<AppState | null>(null);

/** The login token is kept in the phone's secure storage so the user stays logged in. */
async function saveToken(token: string | null) {
  try {
    if (Platform.OS === 'web') return;
    if (token) await SecureStore.setItemAsync(TOKEN_KEY, token);
    else await SecureStore.deleteItemAsync(TOKEN_KEY);
  } catch {
    // secure storage unavailable - user will just log in again
  }
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [lots, setLots] = useState<Lot[]>([]);
  const [campusError, setCampusError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>('map');

  // Campus data for the map and the navigation selectors (static for now - no polling yet)
  const loadCampus = useCallback(async () => {
    try {
      const [m, b, l] = await Promise.all([api.meta(), api.buildings(), api.lots()]);
      setMeta(m);
      setBuildings(b);
      setLots(l);
      setCampusError(null);
    } catch (e) {
      setCampusError((e as Error).message);
    }
  }, []);

  const startSession = useCallback(async (s: Session) => {
    setToken(s.token);
    await saveToken(s.token);
    setUser(s.user);
    loadCampus();
  }, [loadCampus]);

  // Restore a saved login on app start
  useEffect(() => {
    (async () => {
      try {
        const token = Platform.OS === 'web' ? null : await SecureStore.getItemAsync(TOKEN_KEY);
        if (token) {
          setToken(token);
          setUser(await api.me());
          loadCampus();
        }
      } catch {
        setToken(null);
        await saveToken(null);
      } finally {
        setReady(true);
      }
    })();
  }, [loadCampus]);

  const login = useCallback(async (email: string, password: string) => {
    await startSession(await api.login(email, password));
  }, [startSession]);

  const register = useCallback(async (name: string, email: string, password: string, permit: PermitType) => {
    await startSession(await api.register(name, email, password, permit));
  }, [startSession]);

  const logout = useCallback(async () => {
    setToken(null);
    await saveToken(null);
    setUser(null);
    setTab('map');
  }, []);

  const refreshUser = useCallback(async () => {
    setUser(await api.me());
  }, []);

  const updateProfile = useCallback(async (changes: ProfileChanges) => {
    setUser(await api.updateMe(changes));
  }, []);

  const value = useMemo<AppState>(() => ({
    ready, user, meta, buildings, lots, campusError, tab, setTab, login, register, logout, refreshUser,
    updateProfile, loadCampus,
  }), [ready, user, meta, buildings, lots, campusError, tab, login, register, logout, refreshUser, updateProfile,
    loadCampus]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useApp(): AppState {
  const v = useContext(Ctx);
  if (!v) throw new Error('useApp must be used inside AppProvider');
  return v;
}
