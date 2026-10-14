import React, { useMemo, useState } from 'react';
import { FlatList, Modal, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import type { Place } from '../api/types';
import { colors } from '../theme';

const TYPE_ICON: Record<Place['type'], string> = { home: '🏠', building: '🏛️', lot: '🅿️' };

interface Props {
  visible: boolean;
  title: string;
  places: Place[];
  selectedKey?: string | null;
  onSelect: (place: Place) => void;
  onClose: () => void;
}

export const placeKey = (p: Place) => `${p.type}:${p.id}`;

/**
 * Navigation selector list: pick a start or destination from your home, campus buildings and parking lots.
 * Filtering is a simple local match on name / code for now. Smart building search with room numbers
 * and typo tolerance (FR-20) is next milestone.
 */
export default function PlacePicker({ visible, title, places, selectedKey, onSelect, onClose }: Props) {
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return places;
    return places.filter((p) => p.name.toLowerCase().includes(q) || p.subtitle.toLowerCase().includes(q));
  }, [places, query]);

  const close = () => {
    setQuery('');
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={close}>
      <View style={styles.backdrop}>
        <View style={styles.sheet}>
          <View style={styles.header}>
            <Text style={styles.title}>{title}</Text>
            <Pressable onPress={close} accessibilityLabel="Close" hitSlop={10}>
              <Text style={{ fontSize: 20, color: colors.text }}>✕</Text>
            </Pressable>
          </View>
          <TextInput
            value={query}
            onChangeText={setQuery}
            placeholder="Filter by name or building code"
            placeholderTextColor={colors.muted}
            style={styles.search}
            autoCorrect={false}
            accessibilityLabel="Filter places"
          />
          <FlatList
            data={filtered}
            keyExtractor={placeKey}
            keyboardShouldPersistTaps="handled"
            ListEmptyComponent={<Text style={styles.empty}>No matches</Text>}
            renderItem={({ item }) => {
              const active = placeKey(item) === selectedKey;
              return (
                <Pressable
                  style={[styles.row, active && { backgroundColor: colors.greenLight }]}
                  onPress={() => {
                    setQuery('');
                    onSelect(item);
                  }}
                  accessibilityState={{ selected: active }}
                >
                  <Text style={styles.icon}>{TYPE_ICON[item.type]}</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.name}>{item.name}</Text>
                    <Text style={styles.sub}>{item.subtitle}</Text>
                  </View>
                  {active && <Text style={{ color: colors.green, fontWeight: '700' }}>✓</Text>}
                </Pressable>
              );
            }}
          />
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.35)', justifyContent: 'flex-end' },
  sheet: {
    backgroundColor: colors.card, borderTopLeftRadius: 16, borderTopRightRadius: 16, paddingTop: 14,
    maxHeight: '80%', minHeight: '55%',
  },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16 },
  title: { fontSize: 18, fontWeight: '700', color: colors.text },
  search: {
    margin: 12, borderWidth: 1, borderColor: colors.border, borderRadius: 10, paddingHorizontal: 12,
    paddingVertical: 10, fontSize: 15, color: colors.text, backgroundColor: '#fff',
  },
  row: {
    flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 11,
    borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  icon: { fontSize: 20, width: 32 },
  name: { fontSize: 15, fontWeight: '600', color: colors.text },
  sub: { fontSize: 12, color: colors.muted, marginTop: 1 },
  empty: { textAlign: 'center', color: colors.muted, padding: 20 },
});
