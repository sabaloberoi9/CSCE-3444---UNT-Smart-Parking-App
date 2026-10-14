import React, { useMemo, useRef, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import type { Place, TravelMode } from '../api/types';
import CampusMap, { type CampusMapHandle, type MapMarker, type MapPolygon } from '../components/CampusMap';
import PlacePicker, { placeKey } from '../components/PlacePicker';
import { Button, Card, Chip, Muted } from '../components/ui';
import { useApp } from '../state/AppContext';
import { CAMPUS_REGION, colors, lotKindColor, lotKindLabel } from '../theme';

const START_COLOR = colors.green;
const DEST_COLOR = colors.danger;

/**
 * Campus map + navigation selectors (FR-3, FR-4 outlines).
 *
 * Built: campus map with building pins and lot outlines, start / destination selectors (list or map tap),
 * swap, travel-mode choice.
 * TODO (next milestone): live lot availability (FR-5), permit filtering (FR-16), parking recommendations
 * (FR-6), drive + walking routes (FR-8, FR-9), building search (FR-20), points of interest (FR-22).
 */
export default function MapScreen() {
  const { buildings, lots, user } = useApp();
  const mapRef = useRef<CampusMapHandle>(null);
  const [from, setFrom] = useState<Place | null>(null);
  const [to, setTo] = useState<Place | null>(null);
  const [mode, setMode] = useState<TravelMode>('drive');
  const [picker, setPicker] = useState<'from' | 'to' | null>(null);
  const [tapped, setTapped] = useState<Place | null>(null);

  // Everything the selectors can point at: home (from the profile), buildings, parking lots
  const places = useMemo<Place[]>(() => [
    ...(user?.home ? [{
      type: 'home' as const, id: 'home', name: user.home.label ?? 'Home', subtitle: 'Saved in your profile',
      lat: user.home.lat, lng: user.home.lng,
    }] : []),
    ...buildings.map((b): Place => ({ type: 'building', id: b.id, name: b.name, subtitle: b.code, lat: b.lat, lng: b.lng })),
    ...lots.map((l): Place => ({
      type: 'lot', id: l.id, name: l.name, subtitle: `${lotKindLabel[l.kind] ?? l.kind} lot · ${l.capacity} spaces`,
      lat: l.lat, lng: l.lng,
    })),
  ], [buildings, lots, user?.home]);
  const destinations = useMemo(() => places.filter((p) => p.type !== 'home'), [places]);
  const byKey = useMemo(() => new Map(places.map((p) => [placeKey(p), p])), [places]);

  const focus = (a: Place | null, b: Place | null) => {
    const pts = [a, b].filter((p): p is Place => !!p);
    if (pts.length === 0) return;
    const lats = pts.map((p) => p.lat);
    const lngs = pts.map((p) => p.lng);
    const pad = 0.004;
    mapRef.current?.animateToRegion({
      latitude: (Math.min(...lats) + Math.max(...lats)) / 2,
      longitude: (Math.min(...lngs) + Math.max(...lngs)) / 2,
      latitudeDelta: Math.max(0.006, Math.max(...lats) - Math.min(...lats) + pad),
      longitudeDelta: Math.max(0.006, Math.max(...lngs) - Math.min(...lngs) + pad),
    });
  };

  const choose = (which: 'from' | 'to', p: Place) => {
    if (which === 'from') {
      setFrom(p);
      focus(p, to);
    } else {
      setTo(p);
      focus(from, p);
    }
    setPicker(null);
    setTapped(null);
  };

  const swap = () => {
    if (to?.type === 'home') return;
    setFrom(to);
    setTo(from?.type === 'home' ? null : from);
  };

  const clear = () => {
    setFrom(null);
    setTo(null);
    mapRef.current?.animateToRegion(CAMPUS_REGION);
  };

  const polygons = useMemo<MapPolygon[]>(
    () => lots.map((l) => ({
      id: l.id, coordinates: l.polygon, color: lotKindColor[l.kind] ?? colors.muted,
      fillOpacity: to?.type === 'lot' && to.id === l.id ? 0.6 : 0.3,
    })),
    [lots, to],
  );

  const markers = useMemo<MapMarker[]>(() => {
    const isSelected = (key: string) => key === (from && placeKey(from)) || key === (to && placeKey(to));
    const out: MapMarker[] = [
      ...buildings.filter((b) => !isSelected(`building:${b.id}`)).map((b): MapMarker => ({
        id: `building:${b.id}`, kind: 'pin', lat: b.lat, lng: b.lng, title: b.name, subtitle: b.code, color: colors.green,
      })),
      ...lots.filter((l) => !isSelected(`lot:${l.id}`)).map((l): MapMarker => ({
        id: `lot:${l.id}`, kind: 'bubble', lat: l.lat, lng: l.lng, label: 'P', color: lotKindColor[l.kind] ?? colors.muted,
        zIndex: 100,
      })),
    ];
    if (user?.home && !isSelected('home:home')) {
      out.push({ id: 'home:home', kind: 'emoji', lat: user.home.lat, lng: user.home.lng, label: '🏠', title: user.home.label ?? 'Home' });
    }
    if (from) out.push({ id: placeKey(from), kind: 'bubble', lat: from.lat, lng: from.lng, label: 'A', color: START_COLOR, title: from.name, zIndex: 500 });
    if (to) out.push({ id: placeKey(to), kind: 'bubble', lat: to.lat, lng: to.lng, label: 'B', color: DEST_COLOR, title: to.name, zIndex: 500 });
    return out;
  }, [buildings, lots, user?.home, from, to]);

  const onMapTap = (key: string) => {
    const p = byKey.get(key);
    if (p) setTapped(p);
  };

  return (
    <View style={{ flex: 1 }}>
      <CampusMap
        ref={mapRef}
        style={StyleSheet.absoluteFill}
        initialRegion={CAMPUS_REGION}
        polygons={polygons}
        markers={markers}
        onPressMarker={onMapTap}
        onPressPolygon={(id) => onMapTap(`lot:${id}`)}
      />

      {/* Navigation selectors */}
      <View style={styles.top}>
        <Card style={{ marginBottom: 0, padding: 10 }}>
          <View style={styles.row}>
            <View style={{ flex: 1 }}>
              <Selector letter="A" color={START_COLOR} label="From" place={from} placeholder="Choose a starting point"
                onPress={() => setPicker('from')} />
              <View style={styles.divider} />
              <Selector letter="B" color={DEST_COLOR} label="To" place={to} placeholder="Choose a destination"
                onPress={() => setPicker('to')} />
            </View>
            <Pressable onPress={swap} style={styles.swap} accessibilityLabel="Swap start and destination"
              disabled={!from && !to}>
              <Text style={{ fontSize: 20, color: from || to ? colors.green : colors.border }}>⇅</Text>
            </Pressable>
          </View>
          <View style={[styles.row, { marginTop: 8 }]}>
            <Chip label="🚗 Drive" active={mode === 'drive'} onPress={() => setMode('drive')} />
            <Chip label="🚶 Walk" active={mode === 'walk'} onPress={() => setMode('walk')} />
            <View style={{ flex: 1 }} />
            {(from || to) && <Text style={styles.clear} onPress={clear}>Clear</Text>}
          </View>
          <Button label={mode === 'drive' ? 'Find parking & directions' : 'Get walking directions'} disabled
            onPress={() => undefined} />
          <Muted style={{ textAlign: 'center' }}>Directions and parking recommendations are coming next milestone.</Muted>
        </Card>
      </View>

      {/* Tapped a building or lot on the map: use it in the selectors */}
      {tapped ? (
        <View style={styles.bottom}>
          <Card style={{ marginBottom: 0 }}>
            <View style={styles.between}>
              <Text style={styles.placeName} numberOfLines={1}>{tapped.name}</Text>
              <Pressable onPress={() => setTapped(null)} accessibilityLabel="Close" hitSlop={10}>
                <Text style={{ fontSize: 20 }}>✕</Text>
              </Pressable>
            </View>
            <Muted>{tapped.subtitle}</Muted>
            <View style={[styles.row, { marginTop: 8 }]}>
              <Button small variant="secondary" label="Start here" style={{ flex: 1, marginRight: 6 }}
                onPress={() => choose('from', tapped)} />
              <Button small label="Go here" style={{ flex: 1 }} disabled={tapped.type === 'home'}
                onPress={() => choose('to', tapped)} />
            </View>
          </Card>
        </View>
      ) : (
        <View style={styles.bottom} pointerEvents="box-none">
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.legend}>
            {Object.entries(lotKindLabel).map(([kind, label]) => (
              <View key={kind} style={styles.legendItem}>
                <View style={[styles.swatch, { backgroundColor: lotKindColor[kind] }]} />
                <Text style={styles.legendText}>{label}</Text>
              </View>
            ))}
          </ScrollView>
        </View>
      )}

      <PlacePicker
        visible={picker !== null}
        title={picker === 'from' ? 'Start from' : 'Go to'}
        places={picker === 'from' ? places : destinations}
        selectedKey={picker === 'from' ? from && placeKey(from) : to && placeKey(to)}
        onSelect={(p) => picker && choose(picker, p)}
        onClose={() => setPicker(null)}
      />
    </View>
  );
}

function Selector({ letter, color, label, place, placeholder, onPress }: {
  letter: string; color: string; label: string; place: Place | null; placeholder: string; onPress: () => void;
}) {
  return (
    <Pressable onPress={onPress} style={styles.selector} accessibilityRole="button"
      accessibilityLabel={`${label}: ${place ? place.name : placeholder}`}>
      <View style={[styles.dot, { backgroundColor: color }]}>
        <Text style={styles.dotText}>{letter}</Text>
      </View>
      <View style={{ flex: 1 }}>
        <Text style={styles.selLabel}>{label}</Text>
        <Text style={[styles.selValue, !place && { color: colors.muted, fontWeight: '400' }]} numberOfLines={1}>
          {place ? place.name : placeholder}
        </Text>
      </View>
      <Text style={{ color: colors.muted }}>▾</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  top: { position: 'absolute', top: 10, left: 10, right: 10 },
  bottom: { position: 'absolute', left: 10, right: 10, bottom: 10 },
  row: { flexDirection: 'row', alignItems: 'center' },
  between: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  selector: { flexDirection: 'row', alignItems: 'center', paddingVertical: 6 },
  dot: { width: 24, height: 24, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginRight: 10 },
  dotText: { color: '#fff', fontWeight: '800', fontSize: 12 },
  selLabel: { fontSize: 11, color: colors.muted },
  selValue: { fontSize: 15, fontWeight: '600', color: colors.text },
  divider: { height: 1, backgroundColor: colors.border, marginLeft: 34 },
  swap: { paddingHorizontal: 10, paddingVertical: 16 },
  clear: { color: colors.danger, fontWeight: '600', paddingHorizontal: 6 },
  placeName: { fontSize: 17, fontWeight: '700', color: colors.text, flex: 1, paddingRight: 8 },
  legend: { backgroundColor: 'rgba(255,255,255,0.92)', borderRadius: 10, paddingHorizontal: 10, paddingVertical: 6 },
  legendItem: { flexDirection: 'row', alignItems: 'center', marginRight: 12 },
  swatch: { width: 12, height: 12, borderRadius: 3, marginRight: 4 },
  legendText: { fontSize: 12, color: colors.text },
});
