import React, { useEffect, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Switch, Text, View } from 'react-native';

import { api } from '../api/client';
import type { LatLng, ProfileChanges } from '../api/types';
import { Button, Card, Chip, ErrorText, Field, Muted, SectionLabel, Title } from '../components/ui';
import { PERMITS } from '../permits';
import { useApp } from '../state/AppContext';
import { colors } from '../theme';

/** Simulated home locations for the demo (TR-66). Picking a spot on the map is next milestone. */
const HOME_PRESETS: LatLng[] = [
  { lat: 33.185, lng: -97.115, label: 'Apartment (South Denton)' },
  { lat: 33.2046, lng: -97.1559, label: 'Mean Green Village' },
  { lat: 33.2200, lng: -97.1300, label: 'North Denton' },
  { lat: 33.1700, lng: -97.0900, label: 'Corinth' },
];

/** FR-15 profile: name, parking pass, home, accessibility and alert preferences, password. */
export default function ProfileScreen() {
  const { user, updateProfile, logout } = useApp();
  const [name, setName] = useState(user?.name ?? '');
  const [quietStart, setQuietStart] = useState(user?.notifications.quiet_start ?? '');
  const [quietEnd, setQuietEnd] = useState(user?.notifications.quiet_end ?? '');

  useEffect(() => {
    setName(user?.name ?? '');
    setQuietStart(user?.notifications.quiet_start ?? '');
    setQuietEnd(user?.notifications.quiet_end ?? '');
  }, [user?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!user) return null;

  const save = async (changes: ProfileChanges, done?: string) => {
    try {
      await updateProfile(changes);
      if (done) Alert.alert('Saved', done);
    } catch (e) {
      Alert.alert('Could not save', (e as Error).message);
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }} contentContainerStyle={{ padding: 14 }}
      keyboardShouldPersistTaps="handled">
      <Title>Profile</Title>

      <SectionLabel>Account</SectionLabel>
      <Card>
        <Field label="Name" value={name} onChangeText={setName} autoComplete="name" />
        <Button small variant="secondary" label="Save name" disabled={!name.trim() || name.trim() === user.name}
          onPress={() => save({ name: name.trim() }, 'Name updated.')} />
        <Muted style={{ marginTop: 8 }}>Email: {user.email}</Muted>
        <Muted>Account type: {user.role}</Muted>
      </Card>

      <SectionLabel>Parking pass</SectionLabel>
      <Card>
        <View style={styles.wrap}>
          {PERMITS.map((p) => (
            <Chip key={p.key} label={p.label} active={user.permit === p.key} onPress={() => save({ permit: p.key })} />
          ))}
        </View>
        <Muted>Current: {user.permit_label}. Pass-based lot filtering on the map is coming next milestone.</Muted>
      </Card>

      <SectionLabel>Home</SectionLabel>
      <Card>
        <Text style={{ color: colors.text, fontWeight: '600', marginBottom: 6 }}>{user.home?.label ?? 'Not set'}</Text>
        <View style={styles.wrap}>
          {HOME_PRESETS.map((h) => (
            <Chip key={h.label} label={h.label ?? ''} active={user.home?.label === h.label} onPress={() => save({ home: h })} />
          ))}
        </View>
        <Muted>Your home shows on the map and can be picked as a starting point. (Simulated locations for the demo.)</Muted>
      </Card>

      <SectionLabel>Preferences</SectionLabel>
      <Card>
        <Toggle label="♿ Accessible routes and parking" value={user.accessible_routing}
          onChange={(v) => save({ accessible_routing: v })} />
        <Toggle label="Alert when a favorite lot is nearly full" value={user.notifications.near_full}
          onChange={(v) => save({ notifications: { near_full: v } })} />
        <Toggle label="Alert when a favorite lot is full" value={user.notifications.full}
          onChange={(v) => save({ notifications: { full: v } })} />
        <Toggle label="Leave-by reminders for classes" value={user.notifications.leave_by}
          onChange={(v) => save({ notifications: { leave_by: v } })} />
        <View style={{ flexDirection: 'row', marginTop: 8 }}>
          <View style={{ flex: 1, marginRight: 8 }}>
            <Field label="Quiet hours start" value={quietStart} onChangeText={setQuietStart} placeholder="22:00" />
          </View>
          <View style={{ flex: 1 }}>
            <Field label="Quiet hours end" value={quietEnd} onChangeText={setQuietEnd} placeholder="07:00" />
          </View>
        </View>
        <Button small variant="secondary" label="Save quiet hours"
          onPress={() => save({ notifications: { quiet_start: quietStart || null, quiet_end: quietEnd || null } }, 'Quiet hours updated.')} />
        <Muted style={{ marginTop: 6 }}>Preferences are saved now; alerts and accessible routing arrive in a later build.</Muted>
      </Card>

      <SectionLabel>Password</SectionLabel>
      <PasswordCard />

      <Card>
        <Button label="Log out" variant="secondary" onPress={logout} />
      </Card>
      <View style={{ height: 24 }} />
    </ScrollView>
  );
}

function PasswordCard() {
  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setError(null);
    if (next.length < 8) return setError('New password must be at least 8 characters');
    if (next !== confirm) return setError("New passwords don't match");
    setBusy(true);
    try {
      await api.changePassword(current, next);
      setCurrent('');
      setNext('');
      setConfirm('');
      Alert.alert('Password changed', 'Use your new password next time you log in.');
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <Field label="Current password" value={current} onChangeText={setCurrent} secureTextEntry />
      <Field label="New password (8+ characters)" value={next} onChangeText={setNext} secureTextEntry />
      <Field label="Confirm new password" value={confirm} onChangeText={setConfirm} secureTextEntry />
      <ErrorText message={error} />
      <Button small label="Change password" onPress={submit} loading={busy} disabled={!current || !next} />
    </Card>
  );
}

function Toggle({ label, value, onChange }: { label: string; value: boolean; onChange: (v: boolean) => void }) {
  return (
    <View style={styles.between}>
      <Text style={{ color: colors.text, flex: 1, paddingRight: 8 }}>{label}</Text>
      <Switch value={value} onValueChange={onChange} />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flexDirection: 'row', flexWrap: 'wrap' },
  between: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginVertical: 4 },
});
