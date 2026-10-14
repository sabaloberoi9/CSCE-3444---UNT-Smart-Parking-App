export type PermitType = 'commuter' | 'resident' | 'faculty_staff' | 'garage' | 'none';

export interface LatLng {
  lat: number;
  lng: number;
  label?: string | null;
}

export interface NotificationPrefs {
  near_full: boolean;
  full: boolean;
  leave_by: boolean;
  quiet_start: string | null;
  quiet_end: string | null;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'visitor' | 'admin';
  permit: PermitType;
  permit_label: string;
  home: LatLng | null;
  accessible_routing: boolean;
  notifications: NotificationPrefs;
}

export interface Session {
  token: string;
  user: User;
}

export interface ProfileChanges {
  name?: string;
  permit?: PermitType;
  home?: LatLng;
  accessible_routing?: boolean;
  notifications?: Partial<NotificationPrefs>;
}

export interface Meta {
  app: string;
  version: string;
  milestone: string;
  demo_mode: boolean;
  data_source: string;
  server_time: string;
}

export interface Entrance {
  name: string;
  lat: number;
  lng: number;
  accessible: boolean;
}

export interface Building {
  id: string;
  name: string;
  code: string;
  aliases: string[];
  lat: number;
  lng: number;
  entrances: Entrance[];
}

/** Static lot info. Live availability (FR-5) and permit checks (FR-16) are next milestone. */
export interface Lot {
  id: string;
  name: string;
  kind: string;
  lat: number;
  lng: number;
  polygon: [number, number][];
  capacity: number;
  accessible_spaces: number;
  ev_chargers: number;
  pay_by_hour: boolean;
  hourly_rate: number | null;
}

/** Something the navigation selectors can point at. */
export interface Place {
  type: 'home' | 'building' | 'lot';
  id: string;
  name: string;
  subtitle: string;
  lat: number;
  lng: number;
}

export type TravelMode = 'drive' | 'walk';
