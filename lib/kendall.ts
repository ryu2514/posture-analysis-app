import { thresholds, KendallType } from '@/config/posture-thresholds'

export interface KendallInputs {
  cvaDeg: number
  headOffsetPct: number
  trunkTiltDeg: number
  pelvisTranslationPct: number
}

export interface KendallResult {
  type: KendallType
  label: string
  reason: string
}

export function classifyKendall(p: KendallInputs): KendallResult {
  const cvaLow = p.cvaDeg < thresholds.cvaDeg.mildMin
  const cvaNormal = p.cvaDeg >= thresholds.cvaDeg.normalMin && p.cvaDeg <= thresholds.cvaDeg.normalMax

  const headFwd = p.headOffsetPct > thresholds.headOffsetPct.normalMax

  const trunkBack = p.trunkTiltDeg > thresholds.trunkTiltDeg.mildMax && p.headOffsetPct <= thresholds.headOffsetPct.moderateMax
  const trunkNearVertical = p.trunkTiltDeg <= thresholds.trunkTiltDeg.normalMax

  const pelvisFwd = p.pelvisTranslationPct > thresholds.pelvisTranslationPct.mildMax
  const pelvisNeutral = Math.abs(p.pelvisTranslationPct) <= thresholds.pelvisTranslationPct.normalMax

  if (pelvisFwd && trunkBack) {
    return {
      type: 'sway_back',
      label: 'スウェイバック（後弯平坦型）',
      reason: `骨盤が前方へ${p.pelvisTranslationPct.toFixed(1)}%、体幹が後方へ${p.trunkTiltDeg.toFixed(1)}°傾斜` + (cvaLow ? '、CVA低下（前方頭位）' : ''),
    }
  }

  if (headFwd && !trunkBack && !pelvisFwd) {
    return {
      type: 'kypholordosis',
      label: 'カイホロードーシス（後弯前弯型）',
      reason: `前方頭位（オフセット${p.headOffsetPct.toFixed(1)}%）` + (!trunkNearVertical ? `、体幹傾き${p.trunkTiltDeg.toFixed(1)}°` : ''),
    }
  }

  if (trunkNearVertical && !headFwd && pelvisNeutral) {
    return {
      type: 'flat_back',
      label: 'フラットバック（平背型）',
      reason: `体幹垂直に近い（${p.trunkTiltDeg.toFixed(1)}°）、前方頭位小（${p.headOffsetPct.toFixed(1)}%）、骨盤中間位`,
    }
  }

  if (cvaNormal && trunkNearVertical && pelvisNeutral) {
    return {
      type: 'ideal',
      label: '理想的アライメント',
      reason: `CVA正常域（${p.cvaDeg.toFixed(1)}°）、体幹垂直（${p.trunkTiltDeg.toFixed(1)}°）、骨盤中間位`,
    }
  }

  return {
    type: 'ideal',
    label: '理想的アライメント（推定）',
    reason: `指標が中間域のため保守的に理想に分類（CVA ${p.cvaDeg.toFixed(1)}°、体幹${p.trunkTiltDeg.toFixed(1)}°）`,
  }
}

