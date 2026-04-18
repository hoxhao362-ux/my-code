import os
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any

import fitz  # PyMuPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

from utils.log import global_logger

class PDFService:
    """PDF 处理服务"""
    
    def __init__(self):
        # 尝试注册中文字体（这里假设系统中有常用中文字体，如果找不到可以做兼容处理）
        # 为了学术正式，通常使用宋体或黑体
        # 注意：在 Linux Docker 环境中，可能需要安装字体包如 fonts-wqy-microhei
        self._register_fonts()

    def _register_fonts(self):
        """注册中文字体以支持 PDF 生成"""
        try:
            # 寻找可能的字体路径
            possible_fonts = [
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/truetype/arphic/uming.ttc",
                "C:/Windows/Fonts/simsun.ttc",  # Windows 宋体
                "C:/Windows/Fonts/msyh.ttc",    # Windows 微软雅黑
            ]
            font_path = None
            for p in possible_fonts:
                if os.path.exists(p):
                    font_path = p
                    break
            
            if font_path:
                pdfmetrics.registerFont(TTFont('SimSun', font_path))
                self.font_name = 'SimSun'
                global_logger.info("PDFService", f"成功加载中文字体: {font_path}")
            else:
                self.font_name = 'Helvetica'
                global_logger.warning("PDFService", "未找到中文字体，使用默认 Helvetica 字体，可能导致中文乱码")
        except Exception as e:
            self.font_name = 'Helvetica'
            global_logger.warning("PDFService", f"字体加载失败: {e}")

    async def generate_cover_pdf(self, data: Dict[str, Any], output_path: str):
        """
        生成学术风格的封面 PDF（异步版本）

        Args:
            data: 包含文章信息的字典
            output_path: 输出的 PDF 文件路径
        """
        # 使用 asyncio.to_thread 包装同步的 reportlab 调用
        await asyncio.to_thread(self._generate_cover_pdf_sync, data, output_path)

    def _generate_cover_pdf_sync(self, data: Dict[str, Any], output_path: str):
        """
        同步方法：生成学术风格的封面 PDF
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )

        styles = getSampleStyleSheet()

        # 自定义样式
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName=self.font_name,
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=20
        )

        heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Heading3'],
            fontName=self.font_name,
            fontSize=12,
            spaceAfter=6,
            textColor="black"
        )

        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontName=self.font_name,
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )

        elements = []

        # 1. 标题
        title = data.get("title", "Untitled Manuscript")
        elements.append(Paragraph(f"<b>{title}</b>", title_style))
        elements.append(Spacer(1, 0.5 * inch))

        # 2. 文章类型与栏目
        article_type = data.get("article_type", "Research Article")
        section = data.get("section_category", "")
        type_str = f"<b>Article Type:</b> {article_type}"
        if section:
            type_str += f" | <b>Section/Category:</b> {section}"
        elements.append(Paragraph(type_str, normal_style))

        # 3. 作者信息
        elements.append(Paragraph("<b>Author Information:</b>", heading_style))
        first_author = data.get("first_author", "")
        corresponding_author = data.get("corresponding_author", "")
        authors = data.get("authors", "")
        order_of_authors = data.get("order_of_authors", "")

        if first_author:
            elements.append(Paragraph(f"<b>First Author:</b> {first_author}", normal_style))
        if corresponding_author:
            elements.append(Paragraph(f"<b>Corresponding Author:</b> {corresponding_author}", normal_style))
        if authors:
            elements.append(Paragraph(f"<b>All Authors:</b> {authors}", normal_style))

        elements.append(Spacer(1, 0.2 * inch))

        # 4. 关键字
        keywords = data.get("keywords", "")
        if keywords:
            elements.append(Paragraph("<b>Keywords:</b>", heading_style))
            elements.append(Paragraph(keywords, normal_style))
            elements.append(Spacer(1, 0.2 * inch))

        # 5. 摘要
        abstract = data.get("abstract", "")
        if abstract:
            elements.append(Paragraph("<b>Abstract:</b>", heading_style))
            elements.append(Paragraph(abstract, normal_style))

        # 生成 PDF
        doc.build(elements)
        global_logger.debug("PDFService", f"封面 PDF 已生成: {output_path}")

    async def convert_to_pdf(self, input_path: str, output_dir: str) -> str:
        """
        将文档（如 .docx, .doc）转换为 PDF（异步版本）

        在 Linux 环境下，通过 LibreOffice 的 headless 模式转换。
        如果在不支持的环境中，则直接抛出异常。

        Args:
            input_path: 源文件路径
            output_dir: 输出目录

        Returns:
            生成的 PDF 文件路径
        """
        input_ext = Path(input_path).suffix.lower()
        if input_ext == ".pdf":
            return input_path

        # 针对 Word 等文档，尝试调用 libreoffice
        # 注意：需要在 Dockerfile 中安装 libreoffice-core
        global_logger.info("PDFService", f"开始转换文档为 PDF: {input_path}")

        # 确定命令名称（不同系统可能不同，如 libreoffice, soffice）
        cmd = "libreoffice" if os.name == "posix" else "soffice"

        try:
            # 使用 asyncio.create_subprocess_exec 替代 subprocess.run
            process = await asyncio.create_subprocess_exec(
                cmd, "--headless", "--convert-to", "pdf", input_path, "--outdir", output_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)

            if process.returncode != 0:
                error_msg = stderr.decode("utf-8", errors="ignore")
                global_logger.error("PDFService", f"文档转换失败: {error_msg}")
                raise RuntimeError(f"无法转换文档为 PDF: 可能是系统未安装 LibreOffice 或发生错误。")

            # 转换后的文件路径
            output_filename = Path(input_path).stem + ".pdf"
            output_path = os.path.join(output_dir, output_filename)

            if not os.path.exists(output_path):
                raise FileNotFoundError("转换完成但未找到输出的 PDF 文件")

            global_logger.info("PDFService", f"文档转换成功: {output_path}")
            return output_path

        except FileNotFoundError:
            global_logger.error("PDFService", "系统中未找到 LibreOffice 命令行工具，无法进行格式转换。")
            raise RuntimeError("系统不支持将此类型的文件转换为 PDF（缺少 LibreOffice）。")
        except asyncio.TimeoutError:
            global_logger.error("PDFService", "文档转换超时")
            raise RuntimeError("文档转换超时。")

    async def merge_pdfs(self, pdf_list: list[str], output_path: str):
        """
        合并多个 PDF 文件（异步版本）

        Args:
            pdf_list: 要合并的 PDF 文件路径列表
            output_path: 合并后的输出路径
        """
        # 使用 asyncio.to_thread 包装同步的 PyMuPDF 调用
        await asyncio.to_thread(self._merge_pdfs_sync, pdf_list, output_path)

    def _merge_pdfs_sync(self, pdf_list: list[str], output_path: str):
        """
        同步方法：合并多个 PDF 文件
        """
        result_pdf = fitz.open()

        for pdf_path in pdf_list:
            try:
                with fitz.open(pdf_path) as pdf:
                    result_pdf.insert_pdf(pdf)
            except Exception as e:
                global_logger.error("PDFService", f"合并 PDF 时读取 {pdf_path} 失败: {e}")
                raise RuntimeError(f"合并 PDF 失败，文件损坏或格式不正确。")

        result_pdf.save(output_path)
        result_pdf.close()
        global_logger.info("PDFService", f"PDF 合并成功: {output_path}")

pdf_service = PDFService()
