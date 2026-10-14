import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, Text, View } from 'react-native';

import { API_BASE } from '../api/client';
import type { PermitType } from '../api/types';
import { Button, Card, Chip, ErrorText, Field, Muted, SectionLabel } from '../components/ui';
import { PERMITS } from '../permits';
import { useApp } from '../state/AppContext';
import { colors } from '../theme';

const DEMO_ACCOUNTS = [
  { email: 'alex.commuter@demo.local', label: 'Alex · Commuter' },
  { email: 'riley.resident@demo.local', label: 'Riley · Resident' },
  { email: 'morgan.faculty@demo.local', label: 'Dr. Morgan · Faculty/Staff' },
  { email: 'sam.garage@demo.local', label: 'Sam · Garage permit' },
  { email: 'casey.visitor@demo.local', label: 'Casey · Visitor (no pass)' },
];

/** FR-1 user authentication: log in or create a local account. UNT single sign-on is future work. */
export default function LoginScreen() {
  const { login, register } = useApp();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [permit, setPermit] = useState<PermitType>('commuter');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const run = async (fn: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try {
      await fn();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const submitLogin = (e = email, p = password) => run(() => login(e.trim(), p));

  const submitRegister = () => {
    if (password.length < 8) return setError('Password must be at least 8 characters');
    if (password !== confirm) return setError("Passwords don't match");
    run(() => register(name.trim(), email.trim(), password, permit));
  };

  const switchMode = (m: 'login' | 'register') => {
    setMode(m);
    setError(null);
    setPassword('');
    setConfirm('');
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: colors.bg }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={{ padding: 20, paddingTop: 48 }} keyboardShouldPersistTaps="handled">
        <View style={{ alignItems: 'center', marginBottom: 24 }}>
          <Text style={{ fontSize: 44 }}>🦅</Text>
          <Text style={{ fontSize: 26, fontWeight: '800', color: colors.green }}>UNT Parking</Text>
          <Muted>Find parking and get to class</Muted>
        </View>

        <View style={{ flexDirection: 'row', marginBottom: 12 }}>
          <Segment label="Log in" active={mode === 'login'} onPress={() => switchMode('login')} />
          <Segment label="Create account" active={mode === 'register'} onPress={() => switchMode('register')} />
        </View>

        {mode === 'login' ? (
          <Card>
            <Field label="Email" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address"
              autoComplete="email" placeholder="you@demo.local" />
            <Field label="Password" value={password} onChangeText={setPassword} secureTextEntry placeholder="Password" />
            <ErrorText message={error} />
            <Button label="Log in" onPress={() => submitLogin()} loading={busy} disabled={!email || !password} />
          </Card>
        ) : (
          <Card>
            <Field label="Full name" value={name} onChangeText={setName} placeholder="Jamie Lee" autoComplete="name" />
            <Field label="Email" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address"
              autoComplete="email" placeholder="you@my.unt.edu" />
            <Field label="Password (8+ characters)" value={password} onChangeText={setPassword} secureTextEntry />
            <Field label="Confirm password" value={confirm} onChangeText={setConfirm} secureTextEntry />
            <Text style={{ fontSize: 13, color: colors.muted, marginBottom: 6 }}>Parking pass</Text>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
              {PERMITS.map((p) => <Chip key={p.key} label={p.label} active={permit === p.key} onPress={() => setPermit(p.key)} />)}
            </View>
            <ErrorText message={error} />
            <Button label="Create account" onPress={submitRegister} loading={busy} disabled={!name || !email || !password} />
          </Card>
        )}

        {mode === 'login' && (
          <>
            <SectionLabel>Demo accounts (password demo1234)</SectionLabel>
            <Card>
              {DEMO_ACCOUNTS.map((a) => (
                <Button key={a.email} label={a.label} variant="secondary" small onPress={() => submitLogin(a.email, 'demo1234')} />
              ))}
            </Card>
          </>
        )}
        <Muted style={{ textAlign: 'center' }}>Server: {API_BASE}</Muted>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

function Segment({ label, active, onPress }: { label: string; active: boolean; onPress: () => void }) {
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="tab"
      accessibilityState={{ selected: active }}
      style={{
        flex: 1, paddingVertical: 10, alignItems: 'center', borderBottomWidth: 2,
        borderBottomColor: active ? colors.green : colors.border,
      }}
    >
      <Text style={{ fontWeight: active ? '700' : '500', color: active ? colors.green : colors.muted }}>{label}</Text>
    </Pressable>
  );
}
