from typing import Dict, List, Tuple, Optional
from enum import Enum
import math
from backend.app.models.posture_result import PostureMetrics
from backend.app.utils.logger import get_logger

logger = get_logger("posture_classifier")

class PostureType(Enum):
    """Posture type classifications"""
    IDEAL = "ideal"
    KYPHOSIS_LORDOSIS = "kyphosis_lordosis"  # S字型
    FLAT_BACK = "flat_back"  # 平背
    SWAY_BACK = "sway_back"  # 反り腰
    FORWARD_HEAD = "forward_head"  # 前傾型
    LATERAL_DEVIATION = "lateral_deviation"  # 側弯型
    SEATED_SLUMPED = "seated_slumped"  # 座位猫背
    SEATED_UPRIGHT = "seated_upright"  # 座位正常

class PostureColorJudgment(Enum):
    """Color judgment levels"""
    EXCELLENT = "excellent"  # 緑
    GOOD = "good"  # 黄緑
    FAIR = "fair"  # 黄
    POOR = "poor"  # オレンジ
    CRITICAL = "critical"  # 赤

class PostureClassifier:
    """Posture classification and color judgment system"""
    
    def __init__(self):
        self.logger = logger
        
        # 正常範囲の定義
        self.normal_ranges = {
            'pelvic_tilt': (5, 15),  # 度
            'thoracic_kyphosis': (25, 45),  # 度
            'cervical_lordosis': (15, 35),  # 度
            'shoulder_height_difference': (0, 1.5),  # cm
            'head_forward_posture': (0, 2.5),  # cm
            'lumbar_lordosis': (30, 50),  # 度
            'scapular_protraction': (0, 2),  # cm
            'trunk_lateral_deviation': (0, 1),  # cm
            'knee_valgus_varus': (0, 10),  # 度
            'heel_inclination': (0, 5),  # 度
        }
        
        # 座位姿勢の正常範囲
        self.seated_normal_ranges = {
            'seated_pelvic_tilt': (0, 15),  # 度
            'head_neck_position': (0, 5),  # cm
            'trunk_forward_lean': (0, 20),  # 度
            'trunk_backward_lean': (0, 10),  # 度
            'lateral_lean': (0, 10),  # 度
            'shoulder_elevation': (0, 1.5),  # cm
        }
    
    def classify_posture_type(self, metrics: PostureMetrics, pose_orientation: str, 
                            additional_metrics: Optional[Dict] = None) -> Dict[str, str]:
        """姿勢タイプを自動分類"""
        
        # 座位姿勢の場合
        if additional_metrics and 'seated_pelvic_tilt' in additional_metrics:
            return self._classify_seated_posture(additional_metrics)
        
        # 立位姿勢の分類
        return self._classify_standing_posture(metrics, pose_orientation)
    
    def _classify_standing_posture(self, metrics: PostureMetrics, pose_orientation: str) -> Dict[str, str]:
        """立位姿勢の分類"""
        
        classifications = []
        primary_type = PostureType.IDEAL
        
        # 前後方向の分析（矢状面）
        if pose_orientation in ['sagittal', 'oblique']:
            
            # 頭部前方偏位が強い場合
            if metrics.head_forward_posture > 5:
                classifications.append("forward_head")
                primary_type = PostureType.FORWARD_HEAD
            
            # 胸椎後弯と腰椎前弯の組み合わせ分析
            thoracic_excessive = metrics.thoracic_kyphosis > 50
            lumbar_excessive = metrics.lumbar_lordosis > 55
            thoracic_reduced = metrics.thoracic_kyphosis < 20
            lumbar_reduced = metrics.lumbar_lordosis < 25
            
            if thoracic_excessive and lumbar_excessive:
                classifications.append("kyphosis_lordosis")
                primary_type = PostureType.KYPHOSIS_LORDOSIS
            elif thoracic_reduced and lumbar_reduced:
                classifications.append("flat_back")
                primary_type = PostureType.FLAT_BACK
            elif lumbar_excessive and not thoracic_excessive:
                classifications.append("sway_back")
                primary_type = PostureType.SWAY_BACK
        
        # 左右方向の分析（前額面）
        if pose_orientation in ['frontal', 'posterior', 'oblique']:
            
            # 左右の偏位が強い場合
            if (metrics.shoulder_height_difference > 2 or 
                metrics.trunk_lateral_deviation > 2):
                classifications.append("lateral_deviation")
                if primary_type == PostureType.IDEAL:
                    primary_type = PostureType.LATERAL_DEVIATION
        
        # 理想的な姿勢かチェック
        if self._is_ideal_posture(metrics):
            primary_type = PostureType.IDEAL
            classifications = ["ideal"]
        
        return {
            'primary_type': primary_type.value,
            'classifications': classifications,
            'description': self._get_posture_description(primary_type, classifications)
        }
    
    def _classify_seated_posture(self, seated_metrics: Dict) -> Dict[str, str]:
        """座位姿勢の分類"""
        
        classifications = []
        primary_type = PostureType.SEATED_UPRIGHT
        
        # 座位猫背の判定
        if (seated_metrics.get('trunk_forward_lean', 0) > 30 or
            seated_metrics.get('head_neck_position', 0) > 8):
            classifications.append("seated_slumped")
            primary_type = PostureType.SEATED_SLUMPED
        
        # 座位での左右偏位
        if seated_metrics.get('lateral_lean', 0) > 15:
            classifications.append("lateral_deviation")
        
        # 理想的な座位姿勢かチェック
        if self._is_ideal_seated_posture(seated_metrics):
            primary_type = PostureType.SEATED_UPRIGHT
            classifications = ["seated_upright"]
        
        return {
            'primary_type': primary_type.value,
            'classifications': classifications,
            'description': self._get_seated_posture_description(primary_type, classifications)
        }
    
    def _is_ideal_posture(self, metrics: PostureMetrics) -> bool:
        """理想的な姿勢かどうか判定"""
        
        checks = [
            5 <= metrics.pelvic_tilt <= 15,
            25 <= metrics.thoracic_kyphosis <= 45,
            15 <= metrics.cervical_lordosis <= 35,
            metrics.shoulder_height_difference <= 1.5,
            metrics.head_forward_posture <= 2.5,
            30 <= metrics.lumbar_lordosis <= 50,
            metrics.scapular_protraction <= 2,
            metrics.trunk_lateral_deviation <= 1
        ]
        
        # 80%以上の指標が正常範囲内にある場合
        return sum(checks) >= len(checks) * 0.8
    
    def _is_ideal_seated_posture(self, seated_metrics: Dict) -> bool:
        """理想的な座位姿勢かどうか判定"""
        
        checks = [
            seated_metrics.get('seated_pelvic_tilt', 0) <= 15,
            seated_metrics.get('head_neck_position', 0) <= 5,
            seated_metrics.get('trunk_forward_lean', 0) <= 20,
            seated_metrics.get('trunk_backward_lean', 0) <= 10,
            seated_metrics.get('lateral_lean', 0) <= 10,
            seated_metrics.get('shoulder_elevation', 0) <= 1.5
        ]
        
        return sum(checks) >= len(checks) * 0.8
    
    def calculate_color_judgment(self, metrics: PostureMetrics, 
                               additional_metrics: Optional[Dict] = None) -> Dict[str, Dict]:
        """各メトリクスのカラー判定"""
        
        color_judgments = {}
        
        # 基本メトリクスの判定
        basic_metrics = {
            'pelvic_tilt': metrics.pelvic_tilt,
            'thoracic_kyphosis': metrics.thoracic_kyphosis,
            'cervical_lordosis': metrics.cervical_lordosis,
            'shoulder_height_difference': metrics.shoulder_height_difference,
            'head_forward_posture': metrics.head_forward_posture,
            'lumbar_lordosis': metrics.lumbar_lordosis,
            'scapular_protraction': metrics.scapular_protraction,
            'trunk_lateral_deviation': metrics.trunk_lateral_deviation
        }
        
        for metric_name, value in basic_metrics.items():
            if metric_name in self.normal_ranges:
                color_judgments[metric_name] = self._judge_metric_color(
                    value, self.normal_ranges[metric_name], metric_name
                )
        
        # 追加メトリクスの判定
        if additional_metrics:
            for metric_name, value in additional_metrics.items():
                if metric_name in self.normal_ranges:
                    color_judgments[metric_name] = self._judge_metric_color(
                        value, self.normal_ranges[metric_name], metric_name
                    )
                elif metric_name in self.seated_normal_ranges:
                    color_judgments[metric_name] = self._judge_metric_color(
                        value, self.seated_normal_ranges[metric_name], metric_name
                    )
        
        return color_judgments
    
    def _judge_metric_color(self, value: float, normal_range: Tuple[float, float], 
                          metric_name: str) -> Dict:
        """個別メトリクスのカラー判定"""
        
        min_normal, max_normal = normal_range
        
        # 正常範囲内
        if min_normal <= value <= max_normal:
            return {
                'color': PostureColorJudgment.EXCELLENT.value,
                'color_code': '#22c55e',  # 緑
                'status': 'normal',
                'message': '正常範囲内です'
            }
        
        # 偏差の計算
        if value < min_normal:
            deviation = min_normal - value
            deviation_percent = (deviation / min_normal) * 100
        else:
            deviation = value - max_normal
            deviation_percent = (deviation / max_normal) * 100
        
        # 偏差に基づく色判定
        if deviation_percent <= 20:
            return {
                'color': PostureColorJudgment.GOOD.value,
                'color_code': '#84cc16',  # 黄緑
                'status': 'slight_deviation',
                'message': '軽度の偏差があります'
            }
        elif deviation_percent <= 40:
            return {
                'color': PostureColorJudgment.FAIR.value,
                'color_code': '#eab308',  # 黄
                'status': 'moderate_deviation',
                'message': '中程度の偏差があります'
            }
        elif deviation_percent <= 60:
            return {
                'color': PostureColorJudgment.POOR.value,
                'color_code': '#f97316',  # オレンジ
                'status': 'significant_deviation',
                'message': '大きな偏差があります'
            }
        else:
            return {
                'color': PostureColorJudgment.CRITICAL.value,
                'color_code': '#ef4444',  # 赤
                'status': 'critical_deviation',
                'message': '要改善の状態です'
            }
    
    def get_overall_color_judgment(self, color_judgments: Dict) -> Dict:
        """全体的なカラー判定"""
        
        if not color_judgments:
            return {
                'color': PostureColorJudgment.FAIR.value,
                'color_code': '#eab308',
                'message': '判定に十分なデータがありません'
            }
        
        # 各判定のスコア化
        color_scores = {
            'excellent': 5,
            'good': 4,
            'fair': 3,
            'poor': 2,
            'critical': 1
        }
        
        scores = []
        for judgment in color_judgments.values():
            scores.append(color_scores.get(judgment['color'], 3))
        
        average_score = sum(scores) / len(scores)
        
        # 平均スコアに基づく全体判定
        if average_score >= 4.5:
            return {
                'color': PostureColorJudgment.EXCELLENT.value,
                'color_code': '#22c55e',
                'message': '全体的に良好な姿勢です'
            }
        elif average_score >= 3.5:
            return {
                'color': PostureColorJudgment.GOOD.value,
                'color_code': '#84cc16',
                'message': '概ね良好な姿勢です'
            }
        elif average_score >= 2.5:
            return {
                'color': PostureColorJudgment.FAIR.value,
                'color_code': '#eab308',
                'message': '改善の余地があります'
            }
        elif average_score >= 1.5:
            return {
                'color': PostureColorJudgment.POOR.value,
                'color_code': '#f97316',
                'message': '改善が必要です'
            }
        else:
            return {
                'color': PostureColorJudgment.CRITICAL.value,
                'color_code': '#ef4444',
                'message': '要改善の状態です'
            }
    
    def _get_posture_description(self, primary_type: PostureType, 
                               classifications: List[str]) -> str:
        """姿勢タイプの説明文を生成"""
        
        descriptions = {
            PostureType.IDEAL: "理想的な姿勢です。現在の姿勢を維持してください。",
            PostureType.KYPHOSIS_LORDOSIS: "S字型の姿勢で、胸椎の後弯と腰椎の前弯が強くなっています。",
            PostureType.FLAT_BACK: "平背型の姿勢で、脊椎の自然なカーブが失われています。",
            PostureType.SWAY_BACK: "反り腰型の姿勢で、腰椎の前弯が強くなっています。",
            PostureType.FORWARD_HEAD: "前傾型の姿勢で、頭部が前方に出ています。",
            PostureType.LATERAL_DEVIATION: "側弯型の姿勢で、左右への偏位が見られます。"
        }
        
        return descriptions.get(primary_type, "姿勢の評価を実施しました。")
    
    def _get_seated_posture_description(self, primary_type: PostureType, 
                                      classifications: List[str]) -> str:
        """座位姿勢タイプの説明文を生成"""
        
        descriptions = {
            PostureType.SEATED_UPRIGHT: "良好な座位姿勢です。現在の姿勢を維持してください。",
            PostureType.SEATED_SLUMPED: "座位での猫背姿勢です。背筋を伸ばして座ることをお勧めします。"
        }
        
        return descriptions.get(primary_type, "座位姿勢の評価を実施しました。")
    
    def generate_improvement_suggestions(self, posture_type: str, 
                                       color_judgments: Dict) -> List[Dict]:
        """姿勢改善の提案を生成"""
        
        suggestions = []
        
        # 姿勢タイプ別の基本提案
        type_suggestions = {
            'forward_head': {
                'title': '頭部前方偏位の改善',
                'description': '顎を引き、頭を後方に位置させる意識を持ちましょう。',
                'exercises': ['チンタック運動', '首のストレッチ', '肩甲骨の引き寄せ']
            },
            'kyphosis_lordosis': {
                'title': 'S字型姿勢の改善',
                'description': '胸椎の伸展と腰椎の安定化を図りましょう。',
                'exercises': ['キャット&カウ', '胸椎伸展運動', '腹筋強化']
            },
            'sway_back': {
                'title': '反り腰の改善',
                'description': '腰椎の前弯を適正化し、腹筋を強化しましょう。',
                'exercises': ['骨盤傾斜運動', '腹筋強化', '股関節屈筋ストレッチ']
            },
            'seated_slumped': {
                'title': '座位猫背の改善',
                'description': '背筋を伸ばし、正しい座位姿勢を意識しましょう。',
                'exercises': ['椅子の調整', '背筋伸展運動', '肩甲骨の引き寄せ']
            }
        }
        
        if posture_type in type_suggestions:
            suggestions.append(type_suggestions[posture_type])
        
        # 色判定が悪い項目への個別提案
        critical_items = [
            name for name, judgment in color_judgments.items() 
            if judgment['color'] in ['poor', 'critical']
        ]
        
        for item in critical_items:
            if item not in [s.get('target_metric') for s in suggestions]:
                item_suggestion = self._get_metric_specific_suggestion(item)
                if item_suggestion:
                    suggestions.append(item_suggestion)
        
        return suggestions
    
    def _get_metric_specific_suggestion(self, metric_name: str) -> Optional[Dict]:
        """メトリクス別の改善提案"""
        
        suggestions = {
            'shoulder_height_difference': {
                'title': '肩の高さ差の改善',
                'description': '左右の肩の高さを揃えるよう意識しましょう。',
                'exercises': ['肩のストレッチ', '肩甲骨の調整', '姿勢鏡での確認'],
                'target_metric': 'shoulder_height_difference'
            },
            'trunk_lateral_deviation': {
                'title': '体幹の左右偏位の改善',
                'description': '体幹の中心線を意識し、左右対称を保ちましょう。',
                'exercises': ['体幹ストレッチ', '側弯改善運動', '姿勢調整'],
                'target_metric': 'trunk_lateral_deviation'
            }
        }
        
        return suggestions.get(metric_name)