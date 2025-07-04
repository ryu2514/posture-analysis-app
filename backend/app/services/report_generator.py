import matplotlib.pyplot as plt
import matplotlib.patches as patches
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import base64
import uuid
import os
from datetime import datetime
from typing import Dict, List, Any
import numpy as np

from backend.app.models.posture_result import PostureAnalysisResult, PostureReport, PostureRecommendation
from backend.app.core.config import settings

class ReportGenerator:
    """Generate PDF and visual reports for posture analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E7D32')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#1976D2')
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#424242')
        ))
    
    async def generate_pdf_report(self, analysis_result: PostureAnalysisResult) -> Dict[str, str]:
        """Generate comprehensive PDF report"""
        
        # Generate unique report ID
        report_id = str(uuid.uuid4())
        filename = f"posture_report_{report_id}.pdf"
        filepath = os.path.join(settings.REPORTS_DIR, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=50, leftMargin=50,
                              topMargin=50, bottomMargin=50)
        
        # Build report content
        story = []
        
        # Title
        story.append(Paragraph("姿勢分析レポート", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Analysis date
        analysis_date = analysis_result.analysis_timestamp.strftime("%Y年%m月%d日 %H:%M")
        story.append(Paragraph(f"分析日時: {analysis_date}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Overall score section
        score_color = self._get_score_color(analysis_result.overall_score)
        score_text = f'<font color="{score_color}">総合スコア: {analysis_result.overall_score:.1f}点</font>'
        story.append(Paragraph(score_text, self.styles['SectionHeader']))
        story.append(Spacer(1, 10))
        
        # Score interpretation
        interpretation = self._get_score_interpretation(analysis_result.overall_score)
        story.append(Paragraph(interpretation, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Metrics table
        story.append(Paragraph("詳細測定値", self.styles['SectionHeader']))
        metrics_table = self._create_metrics_table(analysis_result.metrics)
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Visual chart
        chart_image = await self._create_radar_chart(analysis_result.metrics)
        if chart_image:
            story.append(Paragraph("姿勢評価チャート", self.styles['SectionHeader']))
            story.append(chart_image)
            story.append(Spacer(1, 20))
        
        # Recommendations
        recommendations = self._generate_recommendations(analysis_result.metrics)
        if recommendations:
            story.append(Paragraph("改善提案", self.styles['SectionHeader']))
            for rec in recommendations:
                story.append(Paragraph(f"• {rec.title}", self.styles['Normal']))
                story.append(Paragraph(f"  {rec.description}", self.styles['MetricLabel']))
                story.append(Spacer(1, 8))
        
        # Build PDF
        doc.build(story)
        
        return {
            "id": report_id,
            "filename": filename,
            "url": f"/reports/{filename}",
            "path": filepath
        }
    
    def _create_metrics_table(self, metrics) -> Table:
        """Create metrics comparison table"""
        
        data = [
            ['測定項目', '測定値', '正常範囲', '評価'],
        ]
        
        ref_values = settings.REFERENCE_VALUES
        
        # Pelvic tilt
        pelvic_status = self._evaluate_metric(metrics.pelvic_tilt, ref_values['pelvic_tilt']['normal'])
        data.append([
            '骨盤傾斜角',
            f'{metrics.pelvic_tilt:.1f}°',
            f'{ref_values["pelvic_tilt"]["normal"][0]}-{ref_values["pelvic_tilt"]["normal"][1]}°',
            pelvic_status
        ])
        
        # Thoracic kyphosis
        thoracic_status = self._evaluate_metric(metrics.thoracic_kyphosis, ref_values['thoracic_kyphosis']['normal'])
        data.append([
            '胸椎後弯角',
            f'{metrics.thoracic_kyphosis:.1f}°',
            f'{ref_values["thoracic_kyphosis"]["normal"][0]}-{ref_values["thoracic_kyphosis"]["normal"][1]}°',
            thoracic_status
        ])
        
        # Cervical lordosis
        cervical_status = self._evaluate_metric(metrics.cervical_lordosis, ref_values['cervical_lordosis']['normal'])
        data.append([
            '頸椎前弯角',
            f'{metrics.cervical_lordosis:.1f}°',
            f'{ref_values["cervical_lordosis"]["normal"][0]}-{ref_values["cervical_lordosis"]["normal"][1]}°',
            cervical_status
        ])
        
        # Shoulder height difference
        shoulder_status = self._evaluate_metric(metrics.shoulder_height_difference, ref_values['shoulder_height_diff']['normal'])
        data.append([
            '肩の高さの差',
            f'{metrics.shoulder_height_difference:.1f}cm',
            f'{ref_values["shoulder_height_diff"]["normal"][0]}-{ref_values["shoulder_height_diff"]["normal"][1]}cm',
            shoulder_status
        ])
        
        # Head forward posture
        head_status = self._evaluate_metric(metrics.head_forward_posture, ref_values['head_forward_posture']['normal'])
        data.append([
            '頭部前方偏位',
            f'{metrics.head_forward_posture:.1f}cm',
            f'{ref_values["head_forward_posture"]["normal"][0]}-{ref_values["head_forward_posture"]["normal"][1]}cm',
            head_status
        ])
        
        table = Table(data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDBDBD'))
        ]))
        
        return table
    
    async def _create_radar_chart(self, metrics) -> Image:
        """Create radar chart for posture metrics"""
        
        try:
            # Setup the radar chart
            categories = ['骨盤傾斜', '胸椎後弯', '頸椎前弯', '肩の高さ', '頭部前方', '腰椎前弯']
            
            # Normalize metrics to 0-100 scale for visualization
            values = [
                self._normalize_for_chart(metrics.pelvic_tilt, [5, 15]),
                self._normalize_for_chart(metrics.thoracic_kyphosis, [25, 45]),
                self._normalize_for_chart(metrics.cervical_lordosis, [15, 35]),
                self._normalize_for_chart(metrics.shoulder_height_difference, [0, 1.5]),
                self._normalize_for_chart(metrics.head_forward_posture, [0, 2.5]),
                self._normalize_for_chart(metrics.lumbar_lordosis, [30, 50])
            ]
            
            # Create the radar chart
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            # Calculate angles for each category
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            values += values[:1]  # Complete the circle
            angles += angles[:1]
            
            # Plot the radar chart
            ax.plot(angles, values, 'o-', linewidth=2, color='#2E7D32')
            ax.fill(angles, values, alpha=0.25, color='#4CAF50')
            
            # Add category labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=12)
            
            # Set y-axis limits and labels
            ax.set_ylim(0, 100)
            ax.set_yticks([20, 40, 60, 80, 100])
            ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10)
            
            # Add grid
            ax.grid(True)
            
            # Title
            plt.title('姿勢評価レーダーチャート', size=16, y=1.08)
            
            # Save to bytes
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            plt.close()
            
            # Create ReportLab Image
            return Image(img_buffer, width=4*inch, height=4*inch)
            
        except Exception as e:
            print(f"Error creating radar chart: {e}")
            return None
    
    def _normalize_for_chart(self, value: float, normal_range: List[float]) -> float:
        """Normalize value for radar chart (0-100 scale)"""
        min_normal, max_normal = normal_range
        
        if min_normal <= value <= max_normal:
            return 100  # Perfect score
        
        # Calculate deviation penalty
        if value < min_normal:
            deviation = (min_normal - value) / min_normal
        else:
            deviation = (value - max_normal) / max_normal
        
        # Convert to 0-100 scale
        score = max(0, 100 - (deviation * 50))  # 50% penalty for 100% deviation
        return min(100, score)
    
    def _evaluate_metric(self, value: float, normal_range: List[float]) -> str:
        """Evaluate if metric is within normal range"""
        min_normal, max_normal = normal_range
        
        if min_normal <= value <= max_normal:
            return "正常"
        elif value < min_normal:
            return "低値"
        else:
            return "高値"
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score"""
        if score >= 80:
            return "#4CAF50"  # Green
        elif score >= 60:
            return "#FF9800"  # Orange
        else:
            return "#F44336"  # Red
    
    def _get_score_interpretation(self, score: float) -> str:
        """Get score interpretation text"""
        if score >= 90:
            return "優秀: 姿勢は非常に良好です。現在の良い姿勢を維持してください。"
        elif score >= 80:
            return "良好: 姿勢は概ね良好ですが、軽微な改善の余地があります。"
        elif score >= 70:
            return "普通: 姿勢にいくつかの問題が見られます。改善エクササイズを推奨します。"
        elif score >= 50:
            return "要改善: 姿勢に複数の問題があります。積極的な改善が必要です。"
        else:
            return "要注意: 姿勢に重大な問題があります。専門家への相談を推奨します。"
    
    def _generate_recommendations(self, metrics) -> List[PostureRecommendation]:
        """Generate personalized recommendations based on metrics"""
        recommendations = []
        
        # Pelvic tilt recommendations
        if metrics.pelvic_tilt > 15:
            recommendations.append(PostureRecommendation(
                category="骨盤矯正",
                title="骨盤後傾エクササイズ",
                description="仰向けで膝を立て、骨盤を床に押し付けるようにして腹筋を収縮させます。",
                difficulty="初級",
                duration="10回 × 3セット",
                frequency="毎日"
            ))
        
        # Head forward posture recommendations  
        if metrics.head_forward_posture > 2.5:
            recommendations.append(PostureRecommendation(
                category="首・肩矯正",
                title="頭部後退エクササイズ",
                description="顎を軽く引き、頭を後ろに押すように首の深部筋を鍛えます。",
                difficulty="初級", 
                duration="10秒保持 × 10回",
                frequency="1日3回"
            ))
        
        # Shoulder height recommendations
        if metrics.shoulder_height_difference > 1.5:
            recommendations.append(PostureRecommendation(
                category="肩バランス矯正",
                title="肩甲骨安定化エクササイズ",
                description="肩甲骨を寄せる動作で背中の筋肉を強化し、肩の位置を整えます。",
                difficulty="中級",
                duration="15回 × 3セット", 
                frequency="週3回"
            ))
        
        return recommendations