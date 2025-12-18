import type { SearchInvitationsQuery, AuthenticationInvitationRoleChoices } from "@lq/graphql";

// Estructura de invitaciones retornada por la query
export type InvitationFromAPI = NonNullable<
  NonNullable<NonNullable<SearchInvitationsQuery["searchInvitations"]>["objects"]>[number]
>;

export interface WorkspaceOption {
  id: string;
  name: string;
}

export interface RoleOption {
  label: string;
  value: AuthenticationInvitationRoleChoices;
}

export interface ClassroomOption {
  label: string;
  value: string;
}

export interface InvitationDto {
  emails: string[];
  workspace: string | null;
  role: AuthenticationInvitationRoleChoices;
  classrooms: string[];
  welcomeMessage: string;
}
