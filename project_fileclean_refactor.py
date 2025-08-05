"""
프로젝트 파일 자동 정리 및 폴더 구조 리팩토링 도구
Project File Cleaner and Folder Structure Refactoring Tool

목적: 불필요한 파일 정리, 데드코드 제거, 폴더 구조 최적화
작성자: Python/React Fullstack Maintainer + File Structure Expert
작성일: 2024-12-31
"""

import os
import sys
import shutil
import hashlib
import ast
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
import difflib
import subprocess

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('project_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== 1. 파일 패턴 정의 =====

class FilePatterns:
    """정리 대상 파일 패턴 정의"""
    
    # 삭제할 파일 확장자
    JUNK_EXTENSIONS = {
        '.pyc', '.pyo', '.pyd',  # Python 캐시
        '.log', '.bak', '.swp', '.swo',  # 로그/백업
        '.tmp', '.temp', '.cache',  # 임시 파일
        '.DS_Store', '.Thumbs.db',  # OS 파일
        '.orig', '.rej',  # Git 충돌 파일
        '.~', '~',  # 편집기 임시 파일
    }
    
    # 삭제할 디렉토리
    JUNK_DIRECTORIES = {
        '__pycache__', '.pytest_cache', '.mypy_cache',
        'node_modules', '.next', 'dist', 'build',
        '.idea', '.vscode', '.vs',
        'tmp', 'temp', 'cache',
        '.git/hooks', '.git/logs',
    }
    
    # 백업 제외 패턴
    BACKUP_EXCLUDE = {
        '.git', '.env', 'venv', 'env',
        'node_modules', '__pycache__',
    }
    
    # 소스 코드 확장자
    SOURCE_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx',
        '.java', '.cpp', '.c', '.h',
        '.html', '.css', '.scss', '.sass',
    }
    
    # 문서 파일
    DOC_EXTENSIONS = {
        '.md', '.rst', '.txt', '.pdf',
        '.doc', '.docx', '.odt',
    }
    
    # 설정 파일
    CONFIG_FILES = {
        'package.json', 'requirements.txt', 'setup.py',
        'Dockerfile', 'docker-compose.yml',
        '.gitignore', '.env.example',
        'webpack.config.js', 'tsconfig.json',
    }

# ===== 2. 파일 분석기 =====

class FileAnalyzer:
    """파일 및 코드 분석"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.file_stats = defaultdict(int)
        self.duplicate_files = defaultdict(list)
        self.dead_code = defaultdict(list)
        self.unused_imports = defaultdict(set)
        
    def analyze_project(self) -> Dict[str, Any]:
        """프로젝트 전체 분석"""
        logger.info("프로젝트 분석 시작...")
        
        analysis = {
            'total_files': 0,
            'total_size': 0,
            'file_types': defaultdict(int),
            'junk_files': [],
            'duplicate_files': {},
            'dead_code': {},
            'unused_imports': {},
            'empty_files': [],
            'large_files': [],
        }
        
        for root, dirs, files in os.walk(self.project_root):
            # 제외할 디렉토리 건너뛰기
            dirs[:] = [d for d in dirs if d not in FilePatterns.BACKUP_EXCLUDE]
            
            for file in files:
                file_path = Path(root) / file
                analysis['total_files'] += 1
                
                # 파일 크기
                try:
                    file_size = file_path.stat().st_size
                    analysis['total_size'] += file_size
                    
                    # 빈 파일
                    if file_size == 0:
                        analysis['empty_files'].append(str(file_path))
                    
                    # 큰 파일 (10MB 이상)
                    if file_size > 10 * 1024 * 1024:
                        analysis['large_files'].append({
                            'path': str(file_path),
                            'size': file_size
                        })
                except:
                    continue
                
                # 파일 타입 분석
                ext = file_path.suffix.lower()
                analysis['file_types'][ext] += 1
                
                # 정크 파일 검사
                if self._is_junk_file(file_path):
                    analysis['junk_files'].append(str(file_path))
                
                # 중복 파일 검사
                if ext in FilePatterns.SOURCE_EXTENSIONS:
                    file_hash = self._get_file_hash(file_path)
                    if file_hash:
                        self.duplicate_files[file_hash].append(str(file_path))
                
                # Python 파일 분석
                if ext == '.py':
                    self._analyze_python_file(file_path)
        
        # 중복 파일 정리
        analysis['duplicate_files'] = {
            h: files for h, files in self.duplicate_files.items()
            if len(files) > 1
        }
        
        # 데드코드 및 미사용 임포트
        analysis['dead_code'] = dict(self.dead_code)
        analysis['unused_imports'] = {
            str(k): list(v) for k, v in self.unused_imports.items()
        }
        
        return analysis
    
    def _is_junk_file(self, file_path: Path) -> bool:
        """정크 파일 여부 확인"""
        # 확장자 검사
        if file_path.suffix.lower() in FilePatterns.JUNK_EXTENSIONS:
            return True
        
        # 파일명 패턴 검사
        name = file_path.name.lower()
        junk_patterns = ['old', 'backup', 'copy', 'test_', '_test', 'tmp', 'temp']
        
        for pattern in junk_patterns:
            if pattern in name:
                return True
        
        # 날짜 패턴 (백업 파일)
        date_pattern = r'\d{4}[-_]\d{2}[-_]\d{2}'
        if re.search(date_pattern, name):
            return True
        
        return False
    
    def _get_file_hash(self, file_path: Path) -> Optional[str]:
        """파일 해시 계산"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def _analyze_python_file(self, file_path: Path):
        """Python 파일 분석"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 임포트 분석
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
            
            # 사용된 이름 찾기
            used_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
            
            # 미사용 임포트 찾기
            unused = imports - used_names
            if unused:
                self.unused_imports[file_path] = unused
            
            # 미사용 함수/클래스 찾기 (간단한 버전)
            defined_funcs = set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not node.name.startswith('_'):  # private 제외
                        defined_funcs.add(node.name)
            
            # 실제 사용 확인 (더 정교한 분석 필요)
            potentially_unused = defined_funcs - used_names
            if potentially_unused:
                self.dead_code[str(file_path)] = list(potentially_unused)
                
        except Exception as e:
            logger.error(f"Python 파일 분석 실패 {file_path}: {e}")

# ===== 3. 백업 관리자 =====

class BackupManager:
    """스마트 백업 관리"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / '.cleanup_backup' / datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def create_backup(self, files_to_backup: List[str]) -> str:
        """파일 백업 생성"""
        logger.info(f"백업 생성 중: {self.backup_dir}")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 백업 메타데이터
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'files': [],
            'total_size': 0
        }
        
        for file_path in files_to_backup:
            try:
                src = Path(file_path)
                if not src.exists():
                    continue
                
                # 상대 경로 유지
                rel_path = src.relative_to(self.project_root)
                dst = self.backup_dir / rel_path
                
                # 디렉토리 생성
                dst.parent.mkdir(parents=True, exist_ok=True)
                
                # 파일 복사
                shutil.copy2(src, dst)
                
                # 메타데이터 추가
                file_size = src.stat().st_size
                metadata['files'].append({
                    'original': str(src),
                    'backup': str(dst),
                    'size': file_size
                })
                metadata['total_size'] += file_size
                
            except Exception as e:
                logger.error(f"백업 실패 {file_path}: {e}")
        
        # 메타데이터 저장
        with open(self.backup_dir / 'backup_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"백업 완료: {len(metadata['files'])}개 파일, {metadata['total_size'] / 1024 / 1024:.2f}MB")
        
        return str(self.backup_dir)
    
    def restore_backup(self, backup_dir: str) -> bool:
        """백업 복원"""
        backup_path = Path(backup_dir)
        metadata_file = backup_path / 'backup_metadata.json'
        
        if not metadata_file.exists():
            logger.error("백업 메타데이터를 찾을 수 없습니다.")
            return False
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        restored = 0
        for file_info in metadata['files']:
            try:
                src = Path(file_info['backup'])
                dst = Path(file_info['original'])
                
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    restored += 1
                    
            except Exception as e:
                logger.error(f"복원 실패 {file_info['original']}: {e}")
        
        logger.info(f"복원 완료: {restored}/{len(metadata['files'])}개 파일")
        return restored > 0

# ===== 4. 폴더 구조 리팩토링 =====

class FolderRefactoring:
    """폴더 구조 개선"""
    
    # 권장 프로젝트 구조
    RECOMMENDED_STRUCTURE = {
        'src': {
            'description': '소스 코드',
            'subdirs': ['components', 'utils', 'services', 'models']
        },
        'api': {
            'description': 'API 엔드포인트',
            'subdirs': ['routes', 'controllers', 'middlewares']
        },
        'frontend': {
            'description': '프론트엔드 코드',
            'subdirs': ['components', 'pages', 'styles', 'assets']
        },
        'backend': {
            'description': '백엔드 코드',
            'subdirs': ['models', 'views', 'serializers', 'services']
        },
        'tests': {
            'description': '테스트 코드',
            'subdirs': ['unit', 'integration', 'e2e']
        },
        'docs': {
            'description': '문서',
            'subdirs': ['api', 'guides', 'references']
        },
        'scripts': {
            'description': '유틸리티 스크립트',
            'subdirs': ['build', 'deploy', 'maintenance']
        },
        'config': {
            'description': '설정 파일',
            'subdirs': ['environments', 'webpack', 'docker']
        }
    }
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        
    def analyze_current_structure(self) -> Dict[str, Any]:
        """현재 폴더 구조 분석"""
        structure = {
            'directories': {},
            'file_distribution': defaultdict(list),
            'recommendations': []
        }
        
        # 최상위 디렉토리 분석
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                dir_info = self._analyze_directory(item)
                structure['directories'][item.name] = dir_info
        
        # 파일 분포 분석
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                
                if ext in FilePatterns.SOURCE_EXTENSIONS:
                    rel_path = file_path.relative_to(self.project_root)
                    structure['file_distribution'][ext].append(str(rel_path))
        
        # 개선 권장사항 생성
        structure['recommendations'] = self._generate_recommendations(structure)
        
        return structure
    
    def _analyze_directory(self, dir_path: Path) -> Dict[str, Any]:
        """디렉토리 분석"""
        info = {
            'path': str(dir_path),
            'file_count': 0,
            'total_size': 0,
            'file_types': defaultdict(int),
            'subdirs': []
        }
        
        for root, dirs, files in os.walk(dir_path):
            # 하위 디렉토리
            if root == str(dir_path):
                info['subdirs'] = [d for d in dirs if not d.startswith('.')]
            
            # 파일 분석
            for file in files:
                info['file_count'] += 1
                file_path = Path(root) / file
                
                try:
                    info['total_size'] += file_path.stat().st_size
                    info['file_types'][file_path.suffix.lower()] += 1
                except:
                    pass
        
        return info
    
    def _generate_recommendations(self, structure: Dict[str, Any]) -> List[Dict[str, str]]:
        """폴더 구조 개선 권장사항"""
        recommendations = []
        
        # 1. 누락된 표준 디렉토리 확인
        existing_dirs = set(structure['directories'].keys())
        for dir_name, dir_info in self.RECOMMENDED_STRUCTURE.items():
            if dir_name not in existing_dirs:
                recommendations.append({
                    'type': 'missing_directory',
                    'directory': dir_name,
                    'description': dir_info['description'],
                    'action': f"{dir_name}/ 디렉토리 생성 권장"
                })
        
        # 2. 파일 재구성 제안
        for ext, files in structure['file_distribution'].items():
            if ext == '.py':
                # Python 파일이 루트에 있는 경우
                root_files = [f for f in files if '/' not in f]
                if len(root_files) > 5:
                    recommendations.append({
                        'type': 'reorganize_files',
                        'files': root_files[:5],
                        'action': 'Python 파일들을 src/ 또는 적절한 디렉토리로 이동'
                    })
            
            elif ext in ['.js', '.jsx', '.tsx']:
                # Frontend 파일 정리
                scattered_files = [f for f in files if not f.startswith(('frontend/', 'src/'))]
                if scattered_files:
                    recommendations.append({
                        'type': 'reorganize_files',
                        'files': scattered_files[:5],
                        'action': 'Frontend 파일들을 frontend/ 디렉토리로 통합'
                    })
        
        # 3. 테스트 파일 정리
        test_files = []
        for files in structure['file_distribution'].values():
            test_files.extend([f for f in files if 'test' in f.lower()])
        
        if test_files and 'tests' not in existing_dirs:
            recommendations.append({
                'type': 'organize_tests',
                'files': test_files[:5],
                'action': '테스트 파일들을 tests/ 디렉토리로 통합'
            })
        
        return recommendations
    
    def create_improved_structure(self, dry_run: bool = True) -> Dict[str, Any]:
        """개선된 폴더 구조 생성"""
        operations = []
        
        # 권장 디렉토리 생성
        for dir_name, dir_info in self.RECOMMENDED_STRUCTURE.items():
            dir_path = self.project_root / dir_name
            
            if not dir_path.exists():
                operations.append({
                    'type': 'create_directory',
                    'path': str(dir_path),
                    'subdirs': dir_info['subdirs']
                })
                
                if not dry_run:
                    dir_path.mkdir(exist_ok=True)
                    for subdir in dir_info['subdirs']:
                        (dir_path / subdir).mkdir(exist_ok=True)
        
        # 파일 이동 제안
        moves = self._suggest_file_moves()
        operations.extend(moves)
        
        if not dry_run:
            for move in moves:
                if move['type'] == 'move_file':
                    self._move_file(move['source'], move['destination'])
        
        return {
            'operations': operations,
            'dry_run': dry_run
        }
    
    def _suggest_file_moves(self) -> List[Dict[str, str]]:
        """파일 이동 제안"""
        moves = []
        
        # Python 파일 정리
        for py_file in self.project_root.glob('*.py'):
            if py_file.name not in ['setup.py', 'manage.py']:
                suggested_path = self.project_root / 'src' / py_file.name
                moves.append({
                    'type': 'move_file',
                    'source': str(py_file),
                    'destination': str(suggested_path),
                    'reason': '루트 디렉토리의 Python 파일을 src/로 이동'
                })
        
        # 테스트 파일 정리
        for test_file in self.project_root.glob('**/test_*.py'):
            if 'tests' not in str(test_file):
                suggested_path = self.project_root / 'tests' / 'unit' / test_file.name
                moves.append({
                    'type': 'move_file',
                    'source': str(test_file),
                    'destination': str(suggested_path),
                    'reason': '테스트 파일을 tests/ 디렉토리로 통합'
                })
        
        return moves[:20]  # 최대 20개 제안
    
    def _move_file(self, source: str, destination: str):
        """파일 이동"""
        try:
            src = Path(source)
            dst = Path(destination)
            
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                logger.info(f"파일 이동: {source} -> {destination}")
        except Exception as e:
            logger.error(f"파일 이동 실패: {e}")

# ===== 5. 정리 실행기 =====

class ProjectCleaner:
    """프로젝트 정리 메인 클래스"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analyzer = FileAnalyzer(project_root)
        self.backup_manager = BackupManager(project_root)
        self.folder_refactoring = FolderRefactoring(project_root)
        self.report = {
            'start_time': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'actions': []
        }
        
    def run_cleanup(self, dry_run: bool = False, create_backup: bool = True) -> Dict[str, Any]:
        """전체 정리 프로세스 실행"""
        logger.info("="*60)
        logger.info(f"프로젝트 정리 시작: {self.project_root}")
        logger.info(f"모드: {'시뮬레이션' if dry_run else '실행'}")
        logger.info("="*60)
        
        # 1. 프로젝트 분석
        logger.info("\n[1/5] 프로젝트 분석 중...")
        analysis = self.analyzer.analyze_project()
        self.report['analysis'] = analysis
        
        # 통계 출력
        logger.info(f"총 파일 수: {analysis['total_files']:,}")
        logger.info(f"총 크기: {analysis['total_size'] / 1024 / 1024:.2f} MB")
        logger.info(f"정크 파일: {len(analysis['junk_files'])}개")
        logger.info(f"중복 파일: {sum(len(f)-1 for f in analysis['duplicate_files'].values())}개")
        logger.info(f"빈 파일: {len(analysis['empty_files'])}개")
        
        # 2. 삭제할 파일 목록 생성
        logger.info("\n[2/5] 삭제 대상 파일 선정...")
        files_to_delete = self._select_files_to_delete(analysis)
        logger.info(f"삭제 예정: {len(files_to_delete)}개 파일")
        
        # 3. 백업 생성
        if create_backup and files_to_delete and not dry_run:
            logger.info("\n[3/5] 백업 생성 중...")
            backup_path = self.backup_manager.create_backup(files_to_delete)
            self.report['backup_path'] = backup_path
        else:
            logger.info("\n[3/5] 백업 건너뜀")
        
        # 4. 파일 삭제
        if not dry_run:
            logger.info("\n[4/5] 파일 삭제 중...")
            deleted_count = self._delete_files(files_to_delete)
            self.report['deleted_files'] = deleted_count
        else:
            logger.info("\n[4/5] 파일 삭제 시뮬레이션")
            self.report['files_to_delete'] = files_to_delete[:100]  # 샘플만 저장
        
        # 5. 폴더 구조 개선
        logger.info("\n[5/5] 폴더 구조 분석 및 개선 제안...")
        structure_analysis = self.folder_refactoring.analyze_current_structure()
        structure_improvements = self.folder_refactoring.create_improved_structure(dry_run=dry_run)
        
        self.report['structure_analysis'] = structure_analysis
        self.report['structure_improvements'] = structure_improvements
        
        # 최종 보고서 생성
        self.report['end_time'] = datetime.now().isoformat()
        self.report['dry_run'] = dry_run
        
        # 보고서 저장
        self._save_report()
        
        logger.info("\n" + "="*60)
        logger.info("프로젝트 정리 완료!")
        logger.info("="*60)
        
        return self.report
    
    def _select_files_to_delete(self, analysis: Dict[str, Any]) -> List[str]:
        """삭제할 파일 선정"""
        files_to_delete = []
        
        # 정크 파일
        files_to_delete.extend(analysis['junk_files'])
        
        # 빈 파일
        files_to_delete.extend(analysis['empty_files'])
        
        # 중복 파일 (원본 하나만 남김)
        for file_hash, duplicate_files in analysis['duplicate_files'].items():
            # 가장 짧은 경로의 파일을 원본으로 선택
            original = min(duplicate_files, key=len)
            for dup in duplicate_files:
                if dup != original:
                    files_to_delete.append(dup)
                    logger.debug(f"중복 파일: {dup} (원본: {original})")
        
        # __pycache__ 디렉토리의 모든 파일
        for pycache_dir in self.project_root.glob('**/__pycache__'):
            for file in pycache_dir.glob('**/*'):
                if file.is_file():
                    files_to_delete.append(str(file))
        
        # 중복 제거
        return list(set(files_to_delete))
    
    def _delete_files(self, files: List[str]) -> int:
        """파일 삭제 실행"""
        deleted = 0
        
        for file_path in files:
            try:
                path = Path(file_path)
                if path.exists():
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path)
                    deleted += 1
                    logger.debug(f"삭제됨: {file_path}")
            except Exception as e:
                logger.error(f"삭제 실패 {file_path}: {e}")
        
        # 빈 디렉토리 정리
        self._remove_empty_directories()
        
        return deleted
    
    def _remove_empty_directories(self):
        """빈 디렉토리 제거"""
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        logger.debug(f"빈 디렉토리 제거: {dir_path}")
                except:
                    pass
    
    def _save_report(self):
        """정리 보고서 저장"""
        report_path = self.project_root / f'cleanup_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        # 보고서 요약 생성
        summary = {
            'project': str(self.project_root),
            'timestamp': self.report['start_time'],
            'mode': 'dry_run' if self.report.get('dry_run') else 'executed',
            'statistics': {
                'total_files': self.report['analysis']['total_files'],
                'junk_files': len(self.report['analysis']['junk_files']),
                'duplicate_files': sum(len(f)-1 for f in self.report['analysis']['duplicate_files'].values()),
                'empty_files': len(self.report['analysis']['empty_files']),
                'deleted_files': self.report.get('deleted_files', 0)
            },
            'recommendations': self.report['structure_analysis']['recommendations']
        }
        
        # 전체 보고서 저장
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        # 요약 보고서 출력
        logger.info(f"\n보고서 저장됨: {report_path}")
        logger.info("\n=== 정리 요약 ===")
        logger.info(f"총 파일: {summary['statistics']['total_files']:,}개")
        logger.info(f"정크 파일: {summary['statistics']['junk_files']}개")
        logger.info(f"중복 파일: {summary['statistics']['duplicate_files']}개")
        logger.info(f"빈 파일: {summary['statistics']['empty_files']}개")
        
        if not self.report.get('dry_run'):
            logger.info(f"삭제된 파일: {summary['statistics']['deleted_files']}개")
            if 'backup_path' in self.report:
                logger.info(f"백업 위치: {self.report['backup_path']}")
        
        # 폴더 구조 권장사항
        if summary['recommendations']:
            logger.info("\n=== 폴더 구조 개선 권장사항 ===")
            for i, rec in enumerate(summary['recommendations'][:5], 1):
                logger.info(f"{i}. {rec['action']}")

# ===== 6. 데드코드 제거기 =====

class DeadCodeRemover:
    """미사용 코드 제거"""
    
    @staticmethod
    def remove_unused_imports(file_path: str, unused_imports: Set[str]) -> bool:
        """미사용 임포트 제거"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            modified = False
            new_lines = []
            
            for line in lines:
                # 임포트 라인 검사
                if line.strip().startswith(('import ', 'from ')):
                    # 미사용 임포트 확인
                    skip = False
                    for unused in unused_imports:
                        if unused in line:
                            skip = True
                            modified = True
                            logger.debug(f"제거: {line.strip()} from {file_path}")
                            break
                    
                    if not skip:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
            
            return modified
            
        except Exception as e:
            logger.error(f"임포트 제거 실패 {file_path}: {e}")
            return False

# ===== 7. 메인 실행 =====

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='프로젝트 파일 정리 및 구조 개선')
    parser.add_argument('project_path', nargs='?', default='.', 
                       help='프로젝트 경로 (기본: 현재 디렉토리)')
    parser.add_argument('--dry-run', action='store_true',
                       help='시뮬레이션 모드 (실제 삭제하지 않음)')
    parser.add_argument('--no-backup', action='store_true',
                       help='백업 생성 안함')
    parser.add_argument('--remove-imports', action='store_true',
                       help='미사용 임포트 제거')
    parser.add_argument('--verbose', action='store_true',
                       help='상세 로그 출력')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 프로젝트 경로 확인
    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        logger.error(f"프로젝트 경로를 찾을 수 없습니다: {project_path}")
        return 1
    
    # 정리 실행
    cleaner = ProjectCleaner(str(project_path))
    report = cleaner.run_cleanup(
        dry_run=args.dry_run,
        create_backup=not args.no_backup
    )
    
    # 미사용 임포트 제거
    if args.remove_imports and not args.dry_run:
        logger.info("\n미사용 임포트 제거 중...")
        remover = DeadCodeRemover()
        
        for file_path, unused_imports in report['analysis']['unused_imports'].items():
            if unused_imports:
                if remover.remove_unused_imports(file_path, set(unused_imports)):
                    logger.info(f"임포트 정리됨: {file_path}")
    
    return 0

# ===== 사용 예시 =====

if __name__ == "__main__":
    # CLI 실행
    sys.exit(main())

# 프로그램 방식 사용 예시:
"""
# 기본 정리
cleaner = ProjectCleaner('/path/to/project')
report = cleaner.run_cleanup(dry_run=True)  # 시뮬레이션

# 실제 정리 실행
cleaner = ProjectCleaner('/path/to/project')
report = cleaner.run_cleanup(dry_run=False, create_backup=True)

# 백업 복원
backup_manager = BackupManager('/path/to/project')
backup_manager.restore_backup(report['backup_path'])

# 폴더 구조 개선만
refactoring = FolderRefactoring('/path/to/project')
analysis = refactoring.analyze_current_structure()
improvements = refactoring.create_improved_structure(dry_run=False)
"""