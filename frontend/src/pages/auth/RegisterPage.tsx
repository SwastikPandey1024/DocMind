import { Button } from '@/components/ui/button';

export function RegisterPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-6 py-12 dark:bg-slate-950">
      <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-8">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-cyan-600">DocuChat</p>
          <h1 className="mt-3 text-3xl font-semibold text-slate-900 dark:text-white">Create your account</h1>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Start building a private knowledge base from your documents.</p>
        </div>

        <Button className="w-full">Create account</Button>
      </div>
    </div>
  );
}
