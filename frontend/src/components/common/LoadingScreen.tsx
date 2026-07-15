export function LoadingScreen({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
      <div className="flex flex-col items-center gap-3">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-cyan-500" />
        <p className="text-sm text-slate-400">{message}</p>
      </div>
    </div>
  );
}
