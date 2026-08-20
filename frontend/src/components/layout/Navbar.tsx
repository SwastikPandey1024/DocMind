import { Bell, Search, SunMoon } from 'lucide-react';
import { useTheme } from '@/components/common/ThemeProvider';

export function Navbar() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="border-b border-slate-200 bg-white/80 px-6 py-4 backdrop-blur dark:border-slate-800 dark:bg-slate-900/80">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-blue-600 p-2 text-white">
            <Search className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-semibold">DocuChat workspace</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Knowledge assistant</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="rounded-xl border border-slate-200 p-2 text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800">
            <Bell className="h-4 w-4" />
          </button>
          <button
            onClick={toggleTheme}
            className="rounded-xl border border-slate-200 p-2 text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            <SunMoon className="h-4 w-4" />
            <span className="sr-only">Toggle {theme === 'dark' ? 'light' : 'dark'} mode</span>
          </button>
        </div>
      </div>
    </header>
  );
}
