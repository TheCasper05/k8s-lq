import type { AuthenticationInvitationRoleChoices } from "@lq/graphql";

export const InvitationRole = {
  STUDENT: "STUDENT" as AuthenticationInvitationRoleChoices,
  TEACHER: "TEACHER" as AuthenticationInvitationRoleChoices,
  COORDINATOR: "COORDINATOR" as AuthenticationInvitationRoleChoices,
  ADMIN_INSTITUCIONAL: "ADMIN_INSTITUCIONAL" as AuthenticationInvitationRoleChoices,
} as const;
