import { Button } from '@/components/ui/button';

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-blue-600">Overview</p>
        <h2 className="mt-3 text-2xl font-semibold text-slate-900 dark:text-white">Your document workspace</h2>
        <p className="mt-2 max-w-2xl text-sm text-slate-500 dark:text-slate-400">
          Upload documents, explore them, and ask questions with a polished AI-powered interface.
        </p>
        <div className="mt-6 flex gap-3">
          <Button>Upload document</Button>
          <Button variant="secondary">View documents</Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Recent documents</h3>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">The latest uploaded files will appear here.</p>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Activity</h3>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Conversation history and processing updates will appear here.</p>
        </div>
      </div>
    </div>
  );
}
