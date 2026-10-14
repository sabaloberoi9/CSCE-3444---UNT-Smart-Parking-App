import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { ActivityIndicator, StyleSheet, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';

import { StatusBanner, TabBar } from './src/components/Chrome';
import { AppProvider, useApp } from './src/state/AppContext';
import LoginScreen from './src/screens/LoginScreen';
import MapScreen from './src/screens/MapScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import { colors } from './src/theme';

function Root() {
  const { ready, user, tab } = useApp();

  if (!ready) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.green} />
      </View>
    );
  }
  if (!user) return <LoginScreen />;

  return (
    <View style={{ flex: 1 }}>
      <StatusBanner />
      <View style={{ flex: 1 }}>
        {tab === 'map' && <MapScreen />}
        {tab === 'profile' && <ProfileScreen />}
      </View>
      <TabBar />
    </View>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <AppProvider>
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.card }} edges={['top', 'bottom']}>
          <StatusBar style="dark" />
          <Root />
        </SafeAreaView>
      </AppProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.bg },
});
