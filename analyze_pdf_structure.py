#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF 구조 분석 스크립트 - OK금융그룹 직무기술서
"""

import fitz  # PyMuPDF
import sys
import io

# 한글 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_pdf_structure(pdf_path: str):
    """PDF 구조 분석"""
    print(f"PDF 분석 시작: {pdf_path}\n")
    
    doc = fitz.open(pdf_path)
    
    # 처음 10페이지 분석
    for page_num in range(min(10, len(doc))):
        page = doc[page_num]
        text = page.get_text()
        
        print(f"\n{'='*60}")
        print(f"페이지 {page_num + 1}")
        print(f"{'='*60}")
        
        # 텍스트 미리보기 (처음 500자)
        preview = text[:500].strip()
        if preview:
            print("텍스트 미리보기:")
            print(preview)
            print("...")
            
            # 직무 관련 키워드 찾기
            keywords = ['직무', '직종', '역할', '자격', '업무', '책임', '요건', '우대']
            found_keywords = [kw for kw in keywords if kw in text]
            if found_keywords:
                print(f"\n발견된 키워드: {', '.join(found_keywords)}")
                
                # 키워드 주변 텍스트 출력
                for kw in found_keywords[:3]:  # 처음 3개만
                    idx = text.find(kw)
                    if idx != -1:
                        start = max(0, idx - 50)
                        end = min(len(text), idx + 100)
                        context = text[start:end].replace('\n', ' ')
                        print(f"\n'{kw}' 주변 텍스트:")
                        print(f"...{context}...")
        else:
            print("텍스트 없음")
    
    # 전체 페이지에서 패턴 찾기
    print(f"\n\n{'='*60}")
    print("전체 PDF 패턴 분석")
    print(f"{'='*60}")
    
    job_pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # 직무 페이지 가능성 체크
        if any(keyword in text for keyword in ['직무명', '담당업무', '자격요건', '주요업무']):
            job_pages.append(page_num + 1)
    
    print(f"\n직무 정보가 있을 가능성이 있는 페이지: {job_pages}")
    
    doc.close()


if __name__ == '__main__':
    pdf_path = r"C:/Users/apro/OneDrive/Desktop/설명회자료/OK_Job Profile.pdf"
    analyze_pdf_structure(pdf_path)