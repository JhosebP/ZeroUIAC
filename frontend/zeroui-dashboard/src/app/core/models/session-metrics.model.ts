export interface SessionSourceCounts {
  voice: number;
  head: number;
  limb: number;
  gesture: number;
  system: number;
}

export interface SessionMetrics {
  session_active: boolean;

  session_id?: string;
  started_at?: string;

  duration_seconds?: number;

  total_events?: number;
  action_events?: number;
  cursor_events?: number;

  error_events?: number;
  error_rate?: number;

  channel_switches?: number;

  source_counts?: SessionSourceCounts;
}