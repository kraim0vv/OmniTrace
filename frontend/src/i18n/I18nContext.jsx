import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import uk from './locales/uk';
import ru from './locales/ru';
import en from './locales/en';

export const LANGS = ['uk', 'ru', 'en'];
const DICTS = { uk, ru, en };
const STORAGE_KEY = 'omnitrace.lang';
const DEFAULT_LANG = 'uk';

function detectLang() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (LANGS.includes(saved)) return saved;
  } catch {
    // storage unavailable
  }
  const nav = (typeof navigator !== 'undefined' && navigator.language) || '';
  const short = nav.slice(0, 2).toLowerCase();
  return LANGS.includes(short) ? short : DEFAULT_LANG;
}

const I18nContext = createContext(null);

export function I18nProvider({ children }) {
  const [lang, setLangState] = useState(detectLang);

  useEffect(() => {
    document.documentElement.lang = lang;
    document.title = DICTS[lang]['app.title'] || DICTS.en['app.title'];
  }, [lang]);

  const setLang = useCallback((next) => {
    if (!LANGS.includes(next)) return;
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // storage unavailable
    }
    setLangState(next);
  }, []);

  const t = useCallback(
    (key, vars) => {
      const str = DICTS[lang][key] ?? DICTS.en[key] ?? key;
      if (!vars) return str;
      return str.replace(/\{(\w+)\}/g, (m, name) => (name in vars ? String(vars[name]) : m));
    },
    [lang]
  );

  const value = useMemo(() => ({ lang, setLang, t }), [lang, setLang, t]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
}
