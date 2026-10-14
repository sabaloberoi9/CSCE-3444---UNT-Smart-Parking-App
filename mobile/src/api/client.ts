import Constants from 'expo-constants';
import type { Building, Lot, Meta, PermitType, ProfileChanges, Session, User } from './types';

/**
 * API base URL. Order: EXPO_PUBLIC_API_URL -> the computer running `expo start` (port 8000).
 * A phone can't reach "localhost" on your computer, so the dev-server host is used.
 */
function resolveBaseUrl(): string {
  const fromEnv = process.env.EXPO_PUBLIC_API_URL;
  if (fromEnv) return fromEnv.replace(/\/$/, '');
  const hostUri = Constants.expoConfig?.hostUri; // e.g. "192.168.1.25:8081"
  const host = hostUri ? hostUri.split(':')[0] : 'localhost';
  return `http://${host}:8000`;
}

export const API_BASE = resolveBaseUrl();
const PREFIX = '/api/v1';

let authToken: string | null = null;
export function setToken(token: string | null) {
  authToken = token;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(method: string, path: string, body?: unknown, query?: Record<string, unknown>): Promise<T> {
  const qs = query
    ? '?' + Object.entries(query)
        .filter(([, v]) => v !== undefined && v !== null)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join('&')
    : '';
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    const res = await fetch(`${API_BASE}${PREFIX}${path}${qs}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
    const text = await res.text();
    const data = text ? JSON.parse(text) : null;
    if (!res.ok) {
      const detail = data?.detail;
      const message = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail[0]?.msg : res.statusText;
      throw new ApiError(message || 'Request failed', res.status);
    }
    return data as T;
  } catch (e) {
    if (e instanceof ApiError) throw e;
    throw new ApiError(`Can't reach the server at ${API_BASE}. Is the backend running?`, 0);
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  // Campus data
  meta: () => request<Meta>('GET', '/meta'),
  buildings: () => request<Building[]>('GET', '/buildings'),
  lots: () => request<Lot[]>('GET', '/lots'),

  // Authentication (FR-1)
  login: (email: string, password: string) => request<Session>('POST', '/auth/login', { email, password }),
  register: (name: string, email: string, password: string, permit: PermitType) =>
    request<Session>('POST', '/auth/register', { name, email, password, permit }),
  changePassword: (currentPassword: string, newPassword: string) =>
    request<{ ok: boolean }>('POST', '/auth/change-password', {
      current_password: currentPassword, new_password: newPassword,
    }),

  // Profile (FR-15)
  me: () => request<User>('GET', '/me'),
  updateMe: (changes: ProfileChanges) => request<User>('PATCH', '/me', changes),

  // TODO (next milestone): lot availability + prediction, recommendations, directions, search,
  // schedule, saved parking, favorites, reports, notifications, admin, demo panel
};
