import React from 'react';
import {
  ActivityIndicator, Pressable, StyleProp, StyleSheet, Text, TextInput, TextInputProps, View, ViewStyle,
} from 'react-native';

import { colors } from '../theme';

export function Card({ children, style }: { children: React.ReactNode; style?: StyleProp<ViewStyle> }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function Title({ children }: { children: React.ReactNode }) {
  return <Text style={styles.title}>{children}</Text>;
}

export function SectionLabel({ children }: { children: React.ReactNode }) {
  return <Text style={styles.section}>{children}</Text>;
}

export function Muted({ children, style }: { children: React.ReactNode; style?: object }) {
  return <Text style={[styles.muted, style]}>{children}</Text>;
}

export function Button({
  label, onPress, variant = 'primary', disabled, loading, small, style,
}: {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'danger' | 'demo';
  disabled?: boolean;
  loading?: boolean;
  small?: boolean;
  style?: StyleProp<ViewStyle>;
}) {
  const bg = { primary: colors.green, secondary: colors.card, danger: colors.danger, demo: colors.demo }[variant];
  const fg = variant === 'secondary' ? colors.green : '#fff';
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      onPress={onPress}
      disabled={disabled || loading}
      style={({ pressed }) => [
        styles.button,
        small && styles.buttonSmall,
        { backgroundColor: bg, opacity: disabled ? 0.5 : pressed ? 0.8 : 1 },
        variant === 'secondary' && { borderWidth: 1, borderColor: colors.green },
        style,
      ]}
    >
      {loading ? <ActivityIndicator color={fg} /> : <Text style={[styles.buttonText, small && { fontSize: 13 }, { color: fg }]}>{label}</Text>}
    </Pressable>
  );
}

export function Chip({ label, active, onPress }: { label: string; active?: boolean; onPress: () => void }) {
  return (
    <Pressable onPress={onPress} style={[styles.chip, active && styles.chipActive]} accessibilityState={{ selected: active }}>
      <Text style={[styles.chipText, active && { color: '#fff' }]}>{label}</Text>
    </Pressable>
  );
}

export function Field(props: TextInputProps & { label: string }) {
  const { label, style, ...rest } = props;
  return (
    <View style={{ marginBottom: 10 }}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <TextInput placeholderTextColor={colors.muted} style={[styles.input, style]} {...rest} />
    </View>
  );
}

export function ErrorText({ message }: { message: string | null }) {
  if (!message) return null;
  return <Text style={styles.error}>{message}</Text>;
}

export const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  title: { fontSize: 22, fontWeight: '700', color: colors.text, marginBottom: 12 },
  section: { fontSize: 13, fontWeight: '700', color: colors.muted, textTransform: 'uppercase', marginTop: 8, marginBottom: 8 },
  muted: { color: colors.muted, fontSize: 13 },
  button: { borderRadius: 10, paddingVertical: 12, paddingHorizontal: 16, alignItems: 'center', justifyContent: 'center', marginVertical: 4 },
  buttonSmall: { paddingVertical: 7, paddingHorizontal: 10 },
  buttonText: { fontWeight: '700', fontSize: 15 },
  chip: {
    borderRadius: 999, borderWidth: 1, borderColor: colors.green, paddingHorizontal: 12, paddingVertical: 6,
    marginRight: 8, marginBottom: 8, backgroundColor: colors.card,
  },
  chipActive: { backgroundColor: colors.green },
  chipText: { color: colors.green, fontWeight: '600', fontSize: 13 },
  fieldLabel: { fontSize: 13, color: colors.muted, marginBottom: 4 },
  input: {
    borderWidth: 1, borderColor: colors.border, borderRadius: 10, paddingHorizontal: 12, paddingVertical: 10,
    backgroundColor: '#fff', color: colors.text, fontSize: 15,
  },
  error: { color: colors.danger, marginVertical: 6 },
  row: { flexDirection: 'row', alignItems: 'center' },
  between: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
});
