import { Navigate, Outlet } from 'react-router-dom';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = false;

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children ? <>{children}</> : <Outlet />;
}
