"use client";

import { useEffect, useState } from "react";
import { signIn, signOut, useSession } from "next-auth/react";

export function AuthButton() {
  const { data: session, status } = useSession();
  const [googleEnabled, setGoogleEnabled] = useState<boolean | null>(null);

  useEffect(() => {
    fetch("/api/auth/providers")
      .then((r) => r.json())
      .then((providers) => setGoogleEnabled(Boolean(providers?.google)))
      .catch(() => setGoogleEnabled(false));
  }, []);

  if (status === "loading") {
    return (
      <span className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-ink/45">
        …
      </span>
    );
  }

  if (session?.user) {
    return (
      <div className="flex items-center gap-2">
        {session.user.image ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={session.user.image}
            alt=""
            className="h-8 w-8 rounded-full border border-ink/15"
            referrerPolicy="no-referrer"
          />
        ) : null}
        <span className="hidden max-w-[8rem] truncate text-xs text-ink/70 sm:inline">
          {session.user.name || session.user.email}
        </span>
        <button
          type="button"
          onClick={() => signOut({ callbackUrl: "/" })}
          className="border border-ink/20 px-3 py-2 text-xs font-semibold text-ink transition hover:border-ink"
        >
          Sign out
        </button>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={() => {
        if (!googleEnabled) {
          alert(
            "Google Sign-In is not configured yet. Add AUTH_GOOGLE_ID, AUTH_GOOGLE_SECRET, and AUTH_SECRET on Vercel (see docs/AUTH-SEO.md).",
          );
          return;
        }
        signIn("google", { callbackUrl: "/" });
      }}
      className="bg-deep px-3 py-2 text-xs font-semibold text-paper transition hover:bg-ink"
      title={googleEnabled === false ? "Configure Google OAuth env vars" : undefined}
    >
      Sign in with Google
    </button>
  );
}
