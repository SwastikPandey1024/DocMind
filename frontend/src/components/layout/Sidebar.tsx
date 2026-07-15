import { FileText, MessageSquareText, LayoutDashboard, Settings } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/chat/sample-doc', label: 'Chat', icon: MessageSquareText },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="hidden w-72 border-r border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900 lg:flex lg:flex-col">
      <div className="mb-8">
        <p className="text-2xl font-semibold tracking-tight text-slate-900 dark:text-white">DocMind</p>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">AI workspace</p>
      </div>

      <nav className="space-y-2">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
              }`
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
