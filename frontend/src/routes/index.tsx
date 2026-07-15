import { Navigate, Route, Routes } from 'react-router-dom';
import { LoginPage } from '@/pages/auth/LoginPage';
import { RegisterPage } from '@/pages/auth/RegisterPage';
import { DashboardPage } from '@/pages/dashboard/DashboardPage';
import { DocumentsPage } from '@/pages/documents/DocumentsPage';
import { ChatPage } from '@/pages/chat/ChatPage';
import { SettingsPage } from '@/pages/settings/SettingsPage';
import { AppLayout } from '@/components/layout/AppLayout';
import { ProtectedRoute } from '@/components/common/ProtectedRoute';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/chat/:documentId" element={<ChatPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}
