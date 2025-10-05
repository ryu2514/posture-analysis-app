// Central thresholds for posture metrics (v1, provisional)
// Values are intended to be replaced/confirmed via literature review (PubMed).

export const thresholds = {
  cvaDeg: {
    normalMin: 50, // CVA normal range lower bound
    normalMax: 60, // upper bound
    mildMin: 45, // < normalMin and >= mildMin considered mild FHP
    moderateMin: 40, // < mildMin and >= moderateMin
  },
  headOffsetPct: {
    normalMax: 8,
    mildMax: 12,
    moderateMax: 16,
  },
  trunkTiltDeg: {
    normalMax: 5,
    mildMax: 10,
    moderateMax: 15,
  },
  pelvisTranslationPct: {
    normalMax: 5,
    mildMax: 10,
    moderateMax: 15,
  },
  shoulderTiltDeg: {
    normalMax: 2,
    mildMax: 4,
    moderateMax: 6,
  },
  shoulderHeightPct: {
    normalMax: 2,
    mildMax: 4,
    moderateMax: 6,
  },
} as const

export type KendallType = 'ideal' | 'kypholordosis' | 'flat_back' | 'sway_back'

