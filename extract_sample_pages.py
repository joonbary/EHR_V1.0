#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
특정 페이지의 전체 텍스트를 추출하여 구조 분석
"""

import fitz  # PyMuPDF
import sys
import io

# 한글 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_pages(pdf_path: str, page_numbers: list):
    """특정 페이지 전체 텍스트 추출"""
    doc = fitz.open(pdf_path)
    
    for page_num in page_numbers:
        if page_num <= len(doc):
            page = doc[page_num - 1]  # 0-indexed
            text = page.get_text()
            
            print(f"\n{'='*80}")
            print(f"페이지 {page_num} 전체 텍스트")
            print(f"{'='*80}")
            print(text)
            
            # 텍스트를 파일로 저장
            with open(f'page_{page_num}.txt', 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\n페이지 {page_num} 텍스트가 page_{page_num}.txt로 저장되었습니다.")
    
    doc.close()


if __name__ == '__main__':
    pdf_path = r"C:/Users/apro/OneDrive/Desktop/설명회자료/OK_Job Profile.pdf"
    # 직무 정보가 있는 페이지들 (3-5페이지 샘플)
    extract_pages(pdf_path, [3, 4, 5, 6, 7, 8])