export function useUsersPage() {
  const { t } = useI18n();

  const pageTitle = "User Management";
  const pageDescription = "User management tools will appear here.";

  return {
    pageTitle,
    pageDescription,
    t,
  };
}
