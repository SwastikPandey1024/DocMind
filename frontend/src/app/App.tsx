import { Suspense } from 'react';
import { Outlet } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { ThemeProvider } from '@/components/common/ThemeProvider';
import { AppRoutes } from '@/routes';
import { LoadingScreen } from '@/components/common/LoadingScreen';

export default function App() {
  return (
    <ThemeProvider>
      <ErrorBoundary>
        <Suspense fallback={<LoadingScreen message="Loading DocMind..." />}>
          <AppShell>
            <Outlet />
            <AppRoutes />
          </AppShell>
        </Suspense>
      </ErrorBoundary>
    </ThemeProvider>
  );
}
