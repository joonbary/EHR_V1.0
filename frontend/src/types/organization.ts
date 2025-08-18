/**
 * Organization TypeScript Type Definitions
 */

export interface Leader {
  title: string;
  rank: string;
  name: string;
  age?: number;
}

export interface MemberCount {
  grade: string;
  count: number;
}

export interface OrgUnit {
  id: string;
  company: string;
  name: string;
  function?: string;
  reportsTo?: string | null;
  headcount: number;
  leader?: Leader;
  members?: MemberCount[];
}

export interface OrgScenario {
  scenario_id: string;
  name: string;
  author?: string;
  author_name?: string;
  payload: OrgUnit[];
  description?: string;
  tags?: string;
  is_active?: boolean;
  created_at: string;
  updated_at?: string;
}

export interface OrgSnapshot {
  snapshot_id: string;
  name: string;
  snapshot_type: 'CURRENT' | 'WHATIF' | 'BACKUP' | 'COMPARISON';
  data: OrgUnit[];
  scenario?: string;
  created_by?: string;
  created_by_name?: string;
  created_at: string;
}

export interface DiffItem {
  type: 'new' | 'deleted' | 'hierarchy' | 'headcount' | 'leader';
  message: string;
  unit: OrgUnit;
}

export interface MatrixCell {
  leader: string;
  headcount: number;
  units: string[];
}

export interface MatrixRow {
  function: string;
  cells: MatrixCell[];
}

export interface MatrixData {
  headers: string[];
  rows: MatrixRow[];
}

export interface OrgChangeLog {
  action: string;
  action_display?: string;
  org_unit_id?: string;
  changes: any;
  user?: string;
  user_name?: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}