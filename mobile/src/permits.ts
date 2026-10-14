import type { PermitType } from './api/types';

/** Parking pass choices shown on the sign-up and profile screens (FR-15). */
export const PERMITS: { key: PermitType; label: string }[] = [
  { key: 'commuter', label: 'Commuter' },
  { key: 'resident', label: 'Resident' },
  { key: 'faculty_staff', label: 'Faculty/Staff' },
  { key: 'garage', label: 'Garage' },
  { key: 'none', label: 'No pass' },
];
