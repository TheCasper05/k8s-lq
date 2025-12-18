import { computed } from "vue";
import { useQuery } from "@vue/apollo-composable";
import { SEARCH_INVITATIONS } from "@lq/graphql";
import type { InvitationFromAPI } from "~/utils/invitations/types";

/**
 * Composable for managing invitation statistics
 * @returns Stats data and formatted stats cards
 */
export function useInvitationStats() {
  const { t } = useI18n();
  const { result: statsResult } = useQuery(SEARCH_INVITATIONS);

  const stats = computed(() => {
    const allInvitations = statsResult.value?.searchInvitations?.objects || [];
    const filteredInvitations = allInvitations.filter(
      (inv: InvitationFromAPI | null): inv is InvitationFromAPI => inv !== null,
    );
    const total = filteredInvitations.length;
    const pending = filteredInvitations.filter((inv: InvitationFromAPI) => inv.status === "PENDING").length;
    const accepted = filteredInvitations.filter((inv: InvitationFromAPI) => inv.status === "ACCEPTED").length;
    const rejected = filteredInvitations.filter((inv: InvitationFromAPI) => inv.status === "DECLINED").length;
    const acceptanceRate = total > 0 ? Math.round((accepted / total) * 100) : 0;

    return {
      total,
      pending,
      accepted,
      rejected,
      acceptanceRate,
    };
  });

  const statsCards = computed(() => [
    {
      key: "total",
      label: t("invitations.stats.total"),
      value: stats.value.total,
      suffix: "",
      color: "text-primary-600",
      bgColor: "bg-primary-50",
      icon: "solar:letter-line-duotone",
    },
    {
      key: "pending",
      label: t("invitations.stats.pending"),
      value: stats.value.pending,
      suffix: "",
      color: "text-warning-600",
      bgColor: "bg-warning-50",
      icon: "solar:clock-circle-line-duotone",
    },
    {
      key: "accepted",
      label: t("invitations.stats.accepted"),
      value: stats.value.accepted,
      suffix: "",
      color: "text-success-600",
      bgColor: "bg-success-50",
      icon: "solar:check-circle-line-duotone",
    },
    {
      key: "rejected",
      label: t("invitations.stats.rejected"),
      value: stats.value.rejected,
      suffix: "",
      color: "text-danger-600",
      bgColor: "bg-danger-50",
      icon: "solar:close-circle-line-duotone",
    },
    {
      key: "acceptanceRate",
      label: t("invitations.stats.acceptanceRate"),
      value: stats.value.acceptanceRate,
      suffix: "%",
      color: "text-primary-600",
      bgColor: "bg-primary-50",
      icon: "solar:magic-stick-line-duotone",
    },
  ]);

  return {
    stats,
    statsCards,
    statsResult,
  };
}
