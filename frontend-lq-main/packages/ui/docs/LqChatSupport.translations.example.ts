import type { ChatTranslations } from "./LqChatSupport.vue";

/**
 * Example translations for LqChatSupport component
 *
 * Usage:
 * ```vue
 * <LqChatSupport
 *   :translations="chatTranslations[locale]"
 *   :logo-src="logoSrc"
 *   :bot-avatar-src="botAvatarSrc"
 * />
 * ```
 */

export const chatTranslationsEN: ChatTranslations = {
  title: "Support",
  subtitle: "online",
  welcomeMessage: "Hi there! 👋 How can I help you today?",
  placeholder: "Type your question...",
  disclaimer: "AI can make mistakes. Check important info.",
  botResponseSimulated: "Thanks for your message! This is a simulated response for the mockup.",
  tooltips: {
    refresh: "Refresh chat",
    minimize: "Minimize chat",
    close: "Close chat",
  },
};

export const chatTranslationsES: ChatTranslations = {
  title: "Soporte",
  subtitle: "en línea",
  welcomeMessage: "¡Hola! 👋 ¿Cómo puedo ayudarte hoy?",
  placeholder: "Escribe tu pregunta...",
  disclaimer: "La IA puede cometer errores. Verifica la información importante.",
  botResponseSimulated: "¡Gracias por tu mensaje! Esta es una respuesta simulada para la maqueta.",
  tooltips: {
    refresh: "Actualizar chat",
    minimize: "Minimizar chat",
    close: "Cerrar chat",
  },
};

export const chatTranslations = {
  en: chatTranslationsEN,
  es: chatTranslationsES,
};
