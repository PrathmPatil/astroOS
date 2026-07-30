"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { Lang, LANG_OPTIONS, translate } from "@/lib/i18n";

type LanguageContextValue = {
  language: Lang;
  setLanguage: (lang: Lang) => void;
  t: (key: string) => string;
  options: typeof LANG_OPTIONS;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

const STORAGE_KEY = "astroos_language";

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Lang>("mr");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY) as Lang | null;
      if (saved && LANG_OPTIONS.some((o) => o.code === saved)) {
        setLanguageState(saved);
      }
    } catch {
      /* ignore */
    }
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    document.documentElement.lang = language;
    try {
      localStorage.setItem(STORAGE_KEY, language);
    } catch {
      /* ignore */
    }
  }, [language, ready]);

  const setLanguage = useCallback((lang: Lang) => {
    setLanguageState(lang);
  }, []);

  const t = useCallback((key: string) => translate(language, key), [language]);

  const value = useMemo(
    () => ({ language, setLanguage, t, options: LANG_OPTIONS }),
    [language, setLanguage, t],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
}
