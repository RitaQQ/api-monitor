from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非互動式後端
import io
import base64
from datetime import datetime
from typing import Dict, Any, List
from report_generator import ProjectReport, ReportGenerator

class PDFExporter:
    """PDF匯出器"""
    
    def __init__(self):
        self.setup_fonts()
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_fonts(self):
        """設定中文字體"""
        try:
            # 嘗試註冊中文字體（如果系統有的話）
            # 這裡使用系統預設字體，實際部署時可能需要提供字體檔案
            pass
        except:
            # 如果沒有中文字體，使用英文字體
            pass
    
    def setup_custom_styles(self):
        """設定自定義樣式"""
        # 標題樣式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # 章節標題樣式
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        # 正文樣式
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14
        )
        
        # 小字樣式
        self.small_style = ParagraphStyle(
            'CustomSmall',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey
        )
    
    def export_project_report(self, report: ProjectReport, output_path: str = None) -> bytes:
        """匯出專案報告為PDF"""
        if output_path is None:
            # 如果沒有指定路徑，返回二進制數據
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
        else:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
        
        # 構建PDF內容
        story = []
        
        # 1. 標題頁
        story.extend(self._create_title_page(report))
        story.append(PageBreak())
        
        # 2. 執行摘要
        story.extend(self._create_executive_summary(report))
        story.append(PageBreak())
        
        # 3. 測試統計
        story.extend(self._create_statistics_section(report))
        story.append(PageBreak())
        
        # 4. 產品分析
        story.extend(self._create_product_analysis(report))
        story.append(PageBreak())
        
        # 5. 測試案例詳情
        story.extend(self._create_test_case_details(report))
        story.append(PageBreak())
        
        # 6. 建議與結論
        story.extend(self._create_recommendations(report))
        
        # 生成PDF
        doc.build(story)
        
        if output_path is None:
            buffer.seek(0)
            return buffer.getvalue()
        
        return None
    
    def _create_title_page(self, report: ProjectReport) -> List:
        """建立標題頁"""
        elements = []
        
        # 主標題
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(f"測試報告", self.title_style))
        elements.append(Spacer(1, 0.5*inch))
        
        # 專案名稱
        elements.append(Paragraph(f"專案：{report.project.name}", self.heading_style))
        elements.append(Spacer(1, 1*inch))
        
        # 基本資訊表格
        project_info = [
            ['項目', '內容'],
            ['測試日期', report.project.test_date.strftime('%Y年%m月%d日')],
            ['負責人', report.project.responsible_user],
            ['專案狀態', self._get_status_text(report.project.status)],
            ['報告生成時間', datetime.now().strftime('%Y年%m月%d日 %H:%M')],
            ['測試案例總數', str(report.statistics.total_cases)],
            ['通過率', f"{report.statistics.pass_rate}%"]
        ]
        
        table = Table(project_info, colWidths=[3*cm, 6*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_executive_summary(self, report: ProjectReport) -> List:
        """建立執行摘要"""
        elements = []
        
        elements.append(Paragraph("執行摘要", self.title_style))
        elements.append(Spacer(1, 20))
        
        # 專案概述
        elements.append(Paragraph("專案概述", self.heading_style))
        overview_text = f"""
        本次測試專案「{report.project.name}」於 {report.project.test_date.strftime('%Y年%m月%d日')} 執行，
        共涵蓋 {report.statistics.total_cases} 個測試案例，測試完成率為 {report.summary['completion_rate']}%，
        整體通過率為 {report.statistics.pass_rate}%。
        """
        elements.append(Paragraph(overview_text, self.body_style))
        elements.append(Spacer(1, 12))
        
        # 關鍵指標
        elements.append(Paragraph("關鍵指標", self.heading_style))
        
        metrics_data = [
            ['指標', '數值', '狀態'],
            ['總測試案例', str(report.statistics.total_cases), ''],
            ['通過案例', str(report.statistics.passed_cases), '✓'],
            ['失敗案例', str(report.statistics.failed_cases), '✗' if report.statistics.failed_cases > 0 else ''],
            ['待測案例', str(report.statistics.not_tested_cases), '⏳' if report.statistics.not_tested_cases > 0 else ''],
            ['通過率', f"{report.statistics.pass_rate}%", self._get_rate_status(report.statistics.pass_rate)],
            ['風險等級', report.summary['risk_level'], self._get_risk_color(report.summary['risk_level'])]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[4*cm, 3*cm, 2*cm])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))
        
        # 主要發現
        elements.append(Paragraph("主要發現", self.heading_style))
        
        if report.summary['top_issues']:
            elements.append(Paragraph("主要問題：", self.body_style))
            for issue in report.summary['top_issues']:
                elements.append(Paragraph(f"• {issue['description']}", self.body_style))
        
        if report.summary['perfect_products']:
            elements.append(Paragraph("表現優秀的產品：", self.body_style))
            for product in report.summary['perfect_products']:
                elements.append(Paragraph(f"• {product}", self.body_style))
        
        elements.append(Spacer(1, 12))
        
        # 建議
        elements.append(Paragraph("關鍵建議", self.heading_style))
        elements.append(Paragraph(report.summary['project_status_suggestion'], self.body_style))
        
        return elements
    
    def _create_statistics_section(self, report: ProjectReport) -> List:
        """建立統計章節"""
        elements = []
        
        elements.append(Paragraph("測試統計分析", self.title_style))
        elements.append(Spacer(1, 20))
        
        # 整體統計圖表
        chart_image = self._create_statistics_chart(report.statistics)
        if chart_image:
            elements.append(chart_image)
            elements.append(Spacer(1, 20))
        
        # 詳細統計表
        elements.append(Paragraph("詳細統計", self.heading_style))
        
        stats_data = [
            ['統計項目', '數量', '百分比'],
            ['總測試案例', str(report.statistics.total_cases), '100%'],
            ['已通過', str(report.statistics.passed_cases), f"{report.statistics.pass_rate}%"],
            ['未通過', str(report.statistics.failed_cases), f"{report.statistics.fail_rate}%"],
            ['尚未測試', str(report.statistics.not_tested_cases), 
             f"{round((report.statistics.not_tested_cases / report.statistics.total_cases * 100) if report.statistics.total_cases > 0 else 0, 1)}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[4*cm, 3*cm, 3*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALTERNATEBACKGROUND', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(stats_table)
        
        return elements
    
    def _create_product_analysis(self, report: ProjectReport) -> List:
        """建立產品分析章節"""
        elements = []
        
        elements.append(Paragraph("產品測試分析", self.title_style))
        elements.append(Spacer(1, 20))
        
        if not report.product_stats:
            elements.append(Paragraph("本專案未設定產品標籤分類。", self.body_style))
            return elements
        
        # 產品統計表
        product_data = [['產品名稱', '總案例', '通過', '失敗', '未測', '通過率']]
        
        for ps in report.product_stats:
            product_data.append([
                ps.product_name,
                str(ps.total_cases),
                str(ps.passed_cases),
                str(ps.failed_cases),
                str(ps.not_tested_cases),
                f"{ps.pass_rate}%"
            ])
        
        product_table = Table(product_data, colWidths=[3*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9)
        ]))
        
        # 根據通過率設定行的背景色
        for i, ps in enumerate(report.product_stats, 1):
            if ps.pass_rate >= 95:
                color = colors.lightgreen
            elif ps.pass_rate >= 80:
                color = colors.lightyellow
            elif ps.pass_rate >= 60:
                color = colors.orange
            else:
                color = colors.lightcoral
            
            product_table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), color)
            ]))
        
        elements.append(product_table)
        elements.append(Spacer(1, 20))
        
        # 問題產品詳情
        problematic_products = [ps for ps in report.product_stats if ps.critical_failures]
        
        if problematic_products:
            elements.append(Paragraph("問題產品詳情", self.heading_style))
            
            for ps in problematic_products:
                elements.append(Paragraph(f"{ps.product_name} (通過率: {ps.pass_rate}%)", 
                                        self.body_style))
                
                if ps.critical_failures:
                    elements.append(Paragraph("主要失敗項目：", self.small_style))
                    for failure in ps.critical_failures:
                        elements.append(Paragraph(f"• {failure}", self.small_style))
                
                elements.append(Spacer(1, 10))
        
        return elements
    
    def _create_test_case_details(self, report: ProjectReport) -> List:
        """建立測試案例詳情章節"""
        elements = []
        
        elements.append(Paragraph("測試案例詳情", self.title_style))
        elements.append(Spacer(1, 20))
        
        # 按狀態分組顯示
        failed_cases = [tc for tc in report.test_case_details if tc['status'] == 'fail']
        passed_cases = [tc for tc in report.test_case_details if tc['status'] == 'pass']
        not_tested_cases = [tc for tc in report.test_case_details if tc['status'] == 'not_tested']
        
        # 失敗案例
        if failed_cases:
            elements.append(Paragraph("失敗的測試案例", self.heading_style))
            for tc in failed_cases:
                elements.extend(self._create_test_case_detail(tc, colors.lightcoral))
        
        # 未測試案例
        if not_tested_cases:
            elements.append(Paragraph("尚未測試的案例", self.heading_style))
            for tc in not_tested_cases[:10]:  # 只顯示前10個
                elements.extend(self._create_test_case_detail(tc, colors.lightgrey))
            
            if len(not_tested_cases) > 10:
                elements.append(Paragraph(f"... 還有 {len(not_tested_cases) - 10} 個未測試案例", 
                                        self.small_style))
        
        # 通過案例（簡要顯示）
        if passed_cases and len(passed_cases) <= 20:
            elements.append(Paragraph("通過的測試案例", self.heading_style))
            
            passed_data = [['案例編號', '標題', '產品標籤']]
            for tc in passed_cases:
                passed_data.append([
                    tc['id'][:8] + '...',
                    tc['title'][:30] + ('...' if len(tc['title']) > 30 else ''),
                    ', '.join(tc['product_tags'])
                ])
            
            passed_table = Table(passed_data, colWidths=[3*cm, 6*cm, 4*cm])
            passed_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen)
            ]))
            
            elements.append(passed_table)
        
        return elements
    
    def _create_test_case_detail(self, test_case: Dict[str, Any], bg_color) -> List:
        """建立單個測試案例詳情"""
        elements = []
        
        # 案例標題和狀態
        title_text = f"{test_case['title']} ({test_case['status_text']})"
        elements.append(Paragraph(title_text, self.body_style))
        
        # 詳情表格
        detail_data = [
            ['用戶角色', test_case['user_role']],
            ['功能描述', test_case['feature_description']],
            ['產品標籤', ', '.join(test_case['product_tags']) if test_case['product_tags'] else '無']
        ]
        
        if test_case['acceptance_criteria']:
            detail_data.append(['驗收條件', '\n'.join(f"• {criterion}" for criterion in test_case['acceptance_criteria'])])
        
        if test_case['test_result_notes']:
            detail_data.append(['測試備註', test_case['test_result_notes']])
        
        if test_case['known_issues']:
            detail_data.append(['已知問題', test_case['known_issues']])
        
        detail_table = Table(detail_data, colWidths=[3*cm, 10*cm])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        elements.append(detail_table)
        elements.append(Spacer(1, 10))
        
        return elements
    
    def _create_recommendations(self, report: ProjectReport) -> List:
        """建立建議與結論章節"""
        elements = []
        
        elements.append(Paragraph("建議與結論", self.title_style))
        elements.append(Spacer(1, 20))
        
        # 總結
        elements.append(Paragraph("測試總結", self.heading_style))
        elements.append(Paragraph(report.summary['project_status_suggestion'], self.body_style))
        elements.append(Spacer(1, 12))
        
        # 具體建議
        elements.append(Paragraph("具體建議", self.heading_style))
        for recommendation in report.summary['recommendations']:
            elements.append(Paragraph(f"• {recommendation}", self.body_style))
        
        elements.append(Spacer(1, 20))
        
        # 下一步行動
        elements.append(Paragraph("下一步行動", self.heading_style))
        
        if report.statistics.not_tested_cases > 0:
            elements.append(Paragraph(f"1. 完成剩餘 {report.statistics.not_tested_cases} 個測試案例的執行", self.body_style))
        
        if report.statistics.failed_cases > 0:
            elements.append(Paragraph(f"2. 修復 {report.statistics.failed_cases} 個失敗的測試案例", self.body_style))
        
        elements.append(Paragraph("3. 根據測試結果決定發布時程", self.body_style))
        elements.append(Paragraph("4. 持續監控產品品質指標", self.body_style))
        
        # 報告生成資訊
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("---", self.small_style))
        elements.append(Paragraph(f"報告生成時間：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}", 
                                self.small_style))
        elements.append(Paragraph("本報告由API監控系統自動生成", self.small_style))
        
        return elements
    
    def _create_statistics_chart(self, statistics) -> Image:
        """建立統計圖表"""
        try:
            # 建立圓餅圖
            fig, ax = plt.subplots(figsize=(8, 6))
            
            labels = ['通過', '失敗', '未測試']
            sizes = [statistics.passed_cases, statistics.failed_cases, statistics.not_tested_cases]
            colors_list = ['#2ecc71', '#e74c3c', '#95a5a6']
            
            # 只顯示非零的部分
            non_zero_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors_list) if size > 0]
            
            if non_zero_data:
                labels, sizes, colors_list = zip(*non_zero_data)
                
                wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_list, 
                                                 autopct='%1.1f%%', startangle=90)
                
                ax.set_title('測試結果分布', fontsize=14, fontweight='bold')
                
                # 儲存圖表到記憶體
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
                img_buffer.seek(0)
                
                # 建立ReportLab Image物件
                img = Image(img_buffer, width=4*inch, height=3*inch)
                
                plt.close()
                return img
            
        except Exception as e:
            print(f"圖表生成失敗: {e}")
        
        return None
    
    def _get_status_text(self, status) -> str:
        """取得狀態文字"""
        status_map = {
            'draft': '草稿',
            'in_progress': '進行中',
            'completed': '已完成'
        }
        return status_map.get(status.value if hasattr(status, 'value') else status, '未知')
    
    def _get_rate_status(self, rate: float) -> str:
        """取得通過率狀態"""
        if rate >= 95:
            return '優秀'
        elif rate >= 80:
            return '良好'
        elif rate >= 60:
            return '一般'
        else:
            return '需改善'
    
    def _get_risk_color(self, risk_level: str) -> str:
        """取得風險等級顏色標示"""
        risk_map = {
            '低': '🟢',
            '中': '🟡',
            '高': '🔴'
        }
        return risk_map.get(risk_level, '⚪')