export const colors = {
  green: '#00853E', // UNT green
  greenDark: '#006A31',
  greenLight: '#E6F4EC',
  bg: '#F6F7F6',
  card: '#FFFFFF',
  text: '#1B1F1C',
  muted: '#5F6B63',
  border: '#DDE3DF',
  danger: '#C62828',
  warning: '#E08A00',
  info: '#1565C0',
  demo: '#6A1B9A',
};

/**
 * Lots are colored by type for now. Live availability colors (open / busy / full)
 * replace this once FR-5 is built.
 */
export const lotKindColor: Record<string, string> = {
  commuter: '#2E7D32',
  resident: '#6A1B9A',
  faculty: '#1565C0',
  garage: '#37474F',
  visitor: '#E08A00',
  remote: '#8D6E63',
};

export const lotKindLabel: Record<string, string> = {
  commuter: 'Commuter',
  resident: 'Resident',
  faculty: 'Faculty/Staff',
  garage: 'Garage',
  visitor: 'Visitor',
  remote: 'Remote',
};

export const CAMPUS_REGION = {
  latitude: 33.2105,
  longitude: -97.1505,
  latitudeDelta: 0.014,
  longitudeDelta: 0.014,
};
