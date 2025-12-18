/**
 * Feature Flags
 *
 * Controls feature availability across the application.
 * Set flags to true when features are ready for production.
 */

export const FEATURE_FLAGS = {
  /**
   * Multi-role support for users with multiple roles
   * Set to true when backend implements multi-role functionality
   */
  MULTI_ROLE_SUPPORT: false,
} as const;

export type FeatureFlag = keyof typeof FEATURE_FLAGS;
