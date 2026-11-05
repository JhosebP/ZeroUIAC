export interface AdaptationWeights {
  voice: number;
  head: number;
  limb: number;
  gesture: number;
}

export interface AdaptationState {
  head_sensitivity_factor: number;
  limb_sensitivity_factor: number;

  weights: AdaptationWeights;

  epsilon: number;
  q_states: number;

  last_reward: number | null;
}