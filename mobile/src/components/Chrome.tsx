import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useApp, type Tab } from '../state/AppContext';
import { colors } from '../theme';

/** TR-69: visible while demo mode is on. Also marks this as an in-progress build. */
export function StatusBanner() {
  const { meta, campusError } = useApp();
  if (campusError) {
    return (
      <View style={[styles.banner, { backgroundColor: colors.warning }]}>
        <Text style={styles.bannerText}>Can't load campus data · check that the backend is running</Text>
      </View>
    );
  }
  if (!meta?.demo_mode) return null;
  return (
    <View style={[styles.banner, { backgroundColor: colors.demo }]}>
      <Text style={styles.bannerText}>Simulated data · dev build v{meta.version} ({meta.milestone})</Text>
    </View>
  );
}

// TODO (next milestone): Park, Classes, My Car and Alerts tabs
const TABS: { key: Tab; label: string; icon: string }[] = [
  { key: 'map', label: 'Map', icon: '🗺️' },
  { key: 'profile', label: 'Profile', icon: '👤' },
];

export function TabBar() {
  const { tab, setTab } = useApp();
  return (
    <View style={styles.tabBar}>
      {TABS.map((t) => {
        const active = t.key === tab;
        return (
          <Pressable
            key={t.key}
            onPress={() => setTab(t.key)}
            style={styles.tab}
            accessibilityRole="tab"
            accessibilityState={{ selected: active }}
            accessibilityLabel={t.label}
          >
            <Text style={styles.icon}>{t.icon}</Text>
            <Text style={[styles.tabLabel, active && { color: colors.green, fontWeight: '700' }]}>{t.label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  banner: { paddingVertical: 5, alignItems: 'center' },
  bannerText: { color: '#fff', fontSize: 12, fontWeight: '700' },
  tabBar: {
    flexDirection: 'row', borderTopWidth: 1, borderTopColor: colors.border, backgroundColor: colors.card,
    paddingBottom: 4,
  },
  tab: { flex: 1, alignItems: 'center', paddingVertical: 6 },
  icon: { fontSize: 18 },
  tabLabel: { fontSize: 11, color: colors.muted, marginTop: 2 },
});
