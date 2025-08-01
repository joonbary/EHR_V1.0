#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF에서 모든 직무 찾기 - 전체 스캔
"""

import fitz
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def find_all_jobs(pdf_path):
    """PDF에서 모든 직무 관련 페이지 찾기"""
    doc = fitz.open(pdf_path)
    
    # 첫 페이지에서 전체 직무 목록 추출
    first_page = doc[0].get_text()
    print("=== 첫 페이지 직무 목록 ===")
    print(first_page[:1500])
    
    print("\n\n=== 직무 관련 페이지 검색 ===")
    
    job_pages = []
    job_titles = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # 직무: 패턴 찾기
        if '직무:' in text:
            job_match = re.search(r'직무:\s*([^\n]+)', text)
            if job_match:
                job_title = job_match.group(1).strip()
                job_titles.append((page_num + 1, job_title))
                print(f"페이지 {page_num + 1}: 직무: {job_title}")
        
        # Job Profile 페이지 찾기
        if 'Job Profile' in text and ('직군' in text or '직종' in text):
            job_pages.append(page_num + 1)
            # 해당 페이지에서 직종 정보 추출
            lines = text.split('\n')
            for line in lines:
                if '직종' in line and len(line) < 50:
                    print(f"페이지 {page_num + 1}: {line.strip()}")
    
    print(f"\n총 발견된 직무: {len(job_titles)}개")
    print(f"Job Profile 페이지: {len(job_pages)}개")
    
    # PL직군 찾기
    print("\n=== PL직군 검색 ===")
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        if 'PL직군' in text or 'PL' in text:
            print(f"페이지 {page_num + 1}: PL 관련 내용 발견")
            # 해당 페이지 일부 출력
            if 'PL' in text:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'PL' in line:
                        print(f"  -> {line.strip()}")
    
    doc.close()
    
    return job_titles


def extract_job_list_from_first_page(pdf_path):
    """첫 페이지에서 전체 직무 목록 추출"""
    doc = fitz.open(pdf_path)
    first_page_text = doc[0].get_text()
    
    print("\n\n=== 첫 페이지 직무 목록 상세 분석 ===")
    
    # Non-PL 직군 분석
    print("\n[Non-PL 직군]")
    non_pl_jobs = {
        'IT기획': ['시스템기획'],
        'IT개발': ['시스템개발'],
        'IT운영': ['시스템관리', '서비스운영'],
        '경영관리': ['감사', 'HRM', 'HRD', '경영지원', '비서', 'PR', '경영기획', 
                    '디자인', '리스크관리', '마케팅', '스포츠사무관리', '자금', 
                    '재무회계', '정보보안', '준법지원', '총무'],
        '투자금융': ['IB금융'],
        '기업금융': ['기업영업기획', '기업여신심사', '기업여신관리'],
        '기업영업': ['여신영업'],
        '리테일금융': ['데이터/통계', '플랫폼/핀테크', 'NPL영업기획', '리테일심사기획', 
                      'PL기획', '모기지기획', '수신기획', '수신영업']
    }
    
    total_non_pl = 0
    for job_type, jobs in non_pl_jobs.items():
        print(f"{job_type}({len(jobs)}): {', '.join(jobs)}")
        total_non_pl += len(jobs)
    
    print(f"\nNon-PL 총 직무 수: {total_non_pl}개")
    
    # PL 직군 분석
    print("\n[PL 직군]")
    pl_jobs = {
        '고객지원': ['여신고객지원', '사무지원', '수신고객지원', '채권관리지원']
    }
    
    total_pl = 0
    for job_type, jobs in pl_jobs.items():
        print(f"{job_type}({len(jobs)}): {', '.join(jobs)}")
        total_pl += len(jobs)
    
    print(f"\nPL 총 직무 수: {total_pl}개")
    print(f"\n전체 직무 수: {total_non_pl + total_pl}개")
    
    doc.close()
    
    return non_pl_jobs, pl_jobs


if __name__ == '__main__':
    pdf_path = r"C:/Users/apro/OneDrive/Desktop/설명회자료/OK_Job Profile.pdf"
    
    # 전체 직무 찾기
    job_titles = find_all_jobs(pdf_path)
    
    # 첫 페이지 분석
    non_pl_jobs, pl_jobs = extract_job_list_from_first_page(pdf_path)