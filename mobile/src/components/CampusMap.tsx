import React, { forwardRef, useCallback, useEffect, useImperativeHandle, useMemo, useRef } from 'react';
import { StyleSheet, View, type StyleProp, type ViewStyle } from 'react-native';
import { WebView, type WebViewMessageEvent } from 'react-native-webview';

import type { LatLng } from '../api/types';
import { colors } from '../theme';

/**
 * FR-4, FR-29: the campus map shared by the Map, Park and My Car screens.
 *
 * Rendered as a Leaflet map with OpenStreetMap tiles inside a WebView, so it needs no
 * map API key and works in Expo Go on both platforms. (Expo Go on Android stopped shipping a
 * working Google Maps key in SDK 55, which left react-native-maps drawing a gray box there.)
 * Screens describe what to draw with plain props; taps come back through onPressMarker /
 * onPressPolygon. Tiles need an internet connection; lots and routes still draw without one.
 */

export interface MapRegion {
  latitude: number;
  longitude: number;
  latitudeDelta: number;
  longitudeDelta: number;
}

export interface MapMarker {
  id: string;
  lat: number;
  lng: number;
  /** bubble: colored pill with text · pin: colored dot · emoji: large text · me: the user's position */
  kind: 'bubble' | 'pin' | 'emoji' | 'me';
  label?: string;
  color?: string;
  /** Shown in a popup when tapped. */
  title?: string;
  subtitle?: string;
  zIndex?: number;
}

export interface MapPolygon {
  id: string;
  coordinates: [number, number][];
  color: string;
  fillOpacity?: number;
}

export interface MapPolyline {
  id: string;
  coordinates: [number, number][];
  color: string;
  width?: number;
  dashed?: boolean;
}

export interface CampusMapHandle {
  animateToRegion: (region: MapRegion, durationMs?: number) => void;
}

interface Props {
  style?: StyleProp<ViewStyle>;
  /** Region shown on first render. */
  initialRegion?: MapRegion;
  /** Controlled region: the map moves whenever this changes. */
  region?: MapRegion;
  markers?: MapMarker[];
  polygons?: MapPolygon[];
  polylines?: MapPolyline[];
  onPressMarker?: (id: string) => void;
  onPressPolygon?: (id: string) => void;
}

/** TR-19: marker for the user's (real or simulated) position. */
export function meMarker(location: LatLng): MapMarker {
  return { id: 'me', kind: 'me', lat: location.lat, lng: location.lng, title: location.label ?? 'You', zIndex: 1000 };
}

// Kept as a module constant: changing the html string makes the WebView reload the page.
const HTML = `<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body, #map { margin: 0; height: 100%; width: 100%; background: #E8ECE9; }
  .c { transform: translate(-50%, -50%); display: inline-block; white-space: nowrap; }
  .bubble { display: inline-flex; align-items: center; justify-content: center; min-width: 30px; height: 24px;
    padding: 0 6px; border-radius: 12px; border: 2px solid #fff; box-sizing: border-box; color: #fff;
    font: 800 12px -apple-system, Roboto, sans-serif; }
  .pin { width: 16px; height: 16px; border-radius: 8px; border: 2px solid #fff; box-sizing: border-box;
    box-shadow: 0 1px 3px rgba(0,0,0,.45); }
  .me { width: 18px; height: 18px; border-radius: 9px; border: 3px solid #fff; box-sizing: border-box;
    background: ${colors.info}; box-shadow: 0 0 0 4px rgba(21,101,192,.25); }
  .emoji { font-size: 22px; line-height: 1; }
  .leaflet-div-icon { background: transparent; border: 0; }
  .leaflet-popup-content { font: 13px -apple-system, Roboto, sans-serif; margin: 8px 10px; }
  .leaflet-popup-content b { display: block; }
  .msg { padding: 16px; font: 14px -apple-system, Roboto, sans-serif; color: #5F6B63; }
</style></head><body><div id="map"></div><script>
(function () {
  var post = function (m) { if (window.ReactNativeWebView) window.ReactNativeWebView.postMessage(JSON.stringify(m)); };
  if (!window.L) {
    document.body.innerHTML = '<p class="msg">The map needs an internet connection to load.</p>';
    return;
  }
  var map = L.map('map', { zoomControl: false, zoomSnap: 0.5, tap: false });
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);
  var layers = { polygon: {}, polyline: {}, marker: {} };

  function bounds(r) {
    return [[r.latitude - r.latitudeDelta / 2, r.longitude - r.longitudeDelta / 2],
            [r.latitude + r.latitudeDelta / 2, r.longitude + r.longitudeDelta / 2]];
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function iconHtml(m) {
    if (m.kind === 'bubble') return '<div class="c"><div class="bubble" style="background:' + esc(m.color) + '">' + esc(m.label) + '</div></div>';
    if (m.kind === 'emoji') return '<div class="c"><div class="emoji">' + esc(m.label) + '</div></div>';
    if (m.kind === 'me') return '<div class="c"><div class="me"></div></div>';
    return '<div class="c"><div class="pin" style="background:' + esc(m.color || '#00853E') + '"></div></div>';
  }
  function icon(m) { return L.divIcon({ html: iconHtml(m), className: '', iconSize: [0, 0], iconAnchor: [0, 0] }); }
  function popup(m) { return m.title ? '<b>' + esc(m.title) + '</b>' + (m.subtitle ? esc(m.subtitle) : '') : null; }
  function polyStyle(p) { return { color: p.color, weight: 2, fillColor: p.color, fillOpacity: p.fillOpacity == null ? 0.4 : p.fillOpacity }; }
  function lineStyle(p) { return { color: p.color, weight: p.width || 4, dashArray: p.dashed ? '8 6' : null }; }

  // Add/update/remove layers by id so the map doesn't flicker on the 10 s data refresh.
  function sync(kind, items, create, update) {
    var seen = {};
    items.forEach(function (it) {
      seen[it.id] = true;
      var l = layers[kind][it.id];
      if (!l) { l = create(it); l.addTo(map); layers[kind][it.id] = l; } else update(l, it);
    });
    Object.keys(layers[kind]).forEach(function (id) {
      if (!seen[id]) { map.removeLayer(layers[kind][id]); delete layers[kind][id]; }
    });
  }

  window.__update = function (s) {
    sync('polygon', s.polygons || [], function (p) {
      var l = L.polygon(p.coordinates, polyStyle(p));
      l.on('click', function () { post({ type: 'polygon', id: p.id }); });
      return l;
    }, function (l, p) { l.setLatLngs(p.coordinates); l.setStyle(polyStyle(p)); });

    sync('polyline', s.polylines || [], function (p) { return L.polyline(p.coordinates, lineStyle(p)); },
      function (l, p) { l.setLatLngs(p.coordinates); l.setStyle(lineStyle(p)); });

    sync('marker', s.markers || [], function (m) {
      var l = L.marker([m.lat, m.lng], { icon: icon(m), zIndexOffset: m.zIndex || 0 });
      l._sig = JSON.stringify([m.kind, m.label, m.color]);
      var t = popup(m); if (t) l.bindPopup(t);
      l.on('click', function () { post({ type: 'marker', id: m.id }); });
      return l;
    }, function (l, m) {
      l.setLatLng([m.lat, m.lng]);
      var sig = JSON.stringify([m.kind, m.label, m.color]);
      if (sig !== l._sig) { l.setIcon(icon(m)); l._sig = sig; }
      var t = popup(m); if (t) l.bindPopup(t);
    });
  };
  window.__setRegion = function (r, animate) { map.fitBounds(bounds(r), { animate: !!animate, duration: 0.4 }); };
  window.addEventListener('resize', function () { map.invalidateSize(); });
  post({ type: 'ready' });
})();
</script></body></html>`;

const CampusMap = forwardRef<CampusMapHandle, Props>(function CampusMap(
  { style, initialRegion, region, markers, polygons, polylines, onPressMarker, onPressPolygon }, ref,
) {
  const web = useRef<WebView>(null);
  const ready = useRef(false);
  const lastSent = useRef('');
  const state = useMemo(
    () => JSON.stringify({ markers: markers ?? [], polygons: polygons ?? [], polylines: polylines ?? [] }),
    [markers, polygons, polylines],
  );
  const regionJson = region ? JSON.stringify(region) : null;

  const run = useCallback((js: string) => { web.current?.injectJavaScript(`${js}; true;`); }, []);

  const push = useCallback(() => {
    if (!ready.current || state === lastSent.current) return;
    lastSent.current = state;
    run(`window.__update(${state})`);
  }, [run, state]);

  useEffect(push, [push]);

  useEffect(() => {
    if (ready.current && regionJson) run(`window.__setRegion(${regionJson}, true)`);
  }, [regionJson, run]);

  useImperativeHandle(ref, () => ({
    animateToRegion: (r, durationMs = 400) => run(`window.__setRegion(${JSON.stringify(r)}, ${durationMs > 0})`),
  }), [run]);

  const onMessage = (e: WebViewMessageEvent) => {
    let msg: { type: string; id?: string };
    try {
      msg = JSON.parse(e.nativeEvent.data);
    } catch {
      return;
    }
    if (msg.type === 'ready') {
      ready.current = true;
      const first = region ?? initialRegion;
      if (first) run(`window.__setRegion(${JSON.stringify(first)}, false)`);
      lastSent.current = '';
      push();
    } else if (msg.type === 'marker' && msg.id) {
      onPressMarker?.(msg.id);
    } else if (msg.type === 'polygon' && msg.id) {
      onPressPolygon?.(msg.id);
    }
  };

  return (
    <View style={[styles.wrap, style]}>
      <WebView
        ref={web}
        source={{ html: HTML }}
        originWhitelist={['*']}
        onMessage={onMessage}
        style={styles.web}
        javaScriptEnabled
        domStorageEnabled
        scrollEnabled={false}
        bounces={false}
        overScrollMode="never"
        nestedScrollEnabled
        setBuiltInZoomControls={false}
        allowsInlineMediaPlayback
        // the page is reloaded (and 'ready' re-sent) if the WebView process is killed in the background
        onContentProcessDidTerminate={() => { ready.current = false; web.current?.reload(); }}
        onRenderProcessGone={() => { ready.current = false; web.current?.reload(); }}
      />
    </View>
  );
});

export default CampusMap;

const styles = StyleSheet.create({
  wrap: { overflow: 'hidden', backgroundColor: '#E8ECE9' },
  web: { flex: 1, backgroundColor: 'transparent' },
});
