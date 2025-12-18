export type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

export type BadgeVariant = "success" | "warning" | "error" | "info";

export interface TableColumn {
  field: string;
  header: string;
  sortable?: boolean;
  filterable?: boolean;
}

export interface NavItem {
  label: string;
  to: string;
  icon?: string;
  roles?: string[];
}
