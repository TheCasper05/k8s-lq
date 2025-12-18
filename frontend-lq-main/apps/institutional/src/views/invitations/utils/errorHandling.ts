import type { ApolloError } from "@apollo/client";
import type { CreateInvitationInput } from "@lq/graphql";

/**
 * Type for error report items from GraphQL mutations
 */
type ErrorReportItem = {
  objectPosition?: string | null;
  errors?: Array<{
    field?: string | null;
    messages: string[];
  } | null> | null;
} | null;

/**
 * Extracts error messages from errorsReport for create/update operations
 * @param errorsReport - Array of error report items
 * @param payload - Optional payload to get email from position
 * @param t - Translation function
 * @returns Formatted error messages string
 */
export function extractErrorsFromReport(
  errorsReport: ErrorReportItem[] | null | undefined,
  payload?: Array<CreateInvitationInput>,
  t?: (key: string) => string,
): string {
  if (!errorsReport || errorsReport.length === 0) return "";

  const defaultError = t ? t("common.error") : "Error";

  return errorsReport
    .map((error) => {
      if (!error) return "";

      let prefix = "";
      if (payload && error.objectPosition) {
        const position = Number.parseInt(error.objectPosition, 10);
        if (position >= 0 && payload[position]) {
          prefix = `${payload[position].email}: `;
        }
      }

      const messages =
        error.errors
          ?.filter((e): e is NonNullable<typeof e> => e !== null)
          .map((e) => e.messages.join(", "))
          .join("; ") || defaultError;

      return `${prefix}${messages}`;
    })
    .filter((msg) => msg !== "")
    .join("\n");
}

/**
 * Extracts error messages from errorsReport for bulk upload operations
 * @param errorsReport - Array of error report items
 * @param t - Translation function
 * @returns Formatted error messages string
 */
export function extractBulkUploadErrors(
  errorsReport: ErrorReportItem[] | null | undefined,
  t?: (key: string) => string,
): string {
  if (!errorsReport || errorsReport.length === 0) return "";

  const defaultError = t ? t("common.error") : "Error";
  const unknownRow = "Fila desconocida";

  return errorsReport
    .map((error) => {
      if (!error) return "";

      const position = error.objectPosition ? `Fila ${Number.parseInt(error.objectPosition, 10) + 1}` : unknownRow;

      const messages =
        error.errors
          ?.filter((e): e is NonNullable<typeof e> => e !== null)
          .map((e) => `${e.field || ""}: ${e.messages.join(", ")}`)
          .join("; ") || defaultError;

      return `${position}: ${messages}`;
    })
    .filter((msg) => msg !== "")
    .join("\n");
}

/**
 * Extracts error messages from errorsReport for update operations (simpler format)
 * @param errorsReport - Array of error report items
 * @param t - Translation function
 * @returns Formatted error messages string
 */
export function extractUpdateErrors(
  errorsReport: ErrorReportItem[] | null | undefined,
  t?: (key: string) => string,
): string {
  if (!errorsReport || errorsReport.length === 0) return "";

  const defaultError = t ? t("common.error") : "Error";

  return errorsReport
    .map((error) => {
      if (!error) return "";
      return (
        error.errors
          ?.filter((e): e is NonNullable<typeof e> => e !== null)
          .map((e) => e.messages.join(", "))
          .join("; ") || defaultError
      );
    })
    .filter((msg) => msg !== "")
    .join("\n");
}

/**
 * Extracts error message from Apollo/GraphQL errors
 * @param error - The error object (can be ApolloError, Error, or unknown)
 * @param t - Translation function
 * @param defaultMessageKey - Default message key for translation
 * @returns Extracted error message
 */
export function extractApolloError(
  error: unknown,
  t?: (key: string) => string,
  defaultMessageKey: string = "invitations.messages.genericError",
): string {
  const defaultMessage = t ? t(defaultMessageKey) : "An error occurred";

  if (error && typeof error === "object" && "graphQLErrors" in error) {
    const apolloError = error as ApolloError;
    if (apolloError.graphQLErrors && apolloError.graphQLErrors.length > 0) {
      return apolloError.graphQLErrors.map((e) => e.message).join(", ");
    }
    if (apolloError.networkError) {
      return t ? t("invitations.messages.networkError") : "Network error";
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return defaultMessage;
}

/**
 * Formats bulk validation error from GraphQL error message
 * @param rawMessage - Raw error message from GraphQL
 * @returns Object with formatted message and hasCorrectRows flag
 */
export function formatBulkValidationError(rawMessage: string): {
  formattedMessage: string;
  hasCorrectRows: boolean;
} {
  let hasCorrectRows = false;

  if (!rawMessage.includes("Bulk invitation validation failed:")) {
    return { formattedMessage: rawMessage, hasCorrectRows: false };
  }

  const lines = rawMessage.split("\n").filter((line) => line.trim());
  const formattedLines: string[] = [];

  lines.forEach((line) => {
    if (line.includes("Row") && line.includes("CORRECT")) {
      hasCorrectRows = true;
    } else if (line.includes("Row") && line.includes("ERROR")) {
      formattedLines.push(line.replace("ERROR", "❌ ERROR"));
    } else if (line.trim().startsWith("-")) {
      formattedLines.push(`  ${line.trim()}`);
    }
  });

  return {
    formattedMessage: formattedLines.length > 0 ? formattedLines.join("\n") : rawMessage,
    hasCorrectRows,
  };
}

/**
 * Handles bulk upload GraphQL errors with special formatting
 * @param error - The error object
 * @param t - Translation function
 * @returns Object with error message and hasCorrectRows flag
 */
export function handleBulkUploadGraphQLError(
  error: unknown,
  t?: (key: string) => string,
): {
  errorMessage: string;
  hasCorrectRows: boolean;
} {
  const defaultMessage = t ? t("invitations.messages.bulkUploadGenericError") : "Bulk upload error";

  if (error && typeof error === "object" && "graphQLErrors" in error) {
    const apolloError = error as ApolloError;
    if (apolloError.graphQLErrors && apolloError.graphQLErrors.length > 0) {
      const rawMessage = apolloError.graphQLErrors[0].message;
      const formatted = formatBulkValidationError(rawMessage);
      return {
        errorMessage: formatted.formattedMessage,
        hasCorrectRows: formatted.hasCorrectRows,
      };
    }
    if (apolloError.networkError) {
      return {
        errorMessage: t ? t("invitations.messages.networkError") : "Network error",
        hasCorrectRows: false,
      };
    }
  }

  if (error instanceof Error) {
    return {
      errorMessage: error.message,
      hasCorrectRows: false,
    };
  }

  return {
    errorMessage: defaultMessage,
    hasCorrectRows: false,
  };
}
