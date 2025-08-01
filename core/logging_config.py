"""
로깅 설정
"""
import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path


def setup_logging(log_dir: str = None):
    """로깅 설정"""
    if not log_dir:
        log_dir = Path(__file__).parent.parent / 'logs'
    
    # 로그 디렉토리 생성
    Path(log_dir).mkdir(exist_ok=True)
    
    # 로그 포맷 설정
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    detailed_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # 일반 로그 파일 핸들러 (일별 로테이션)
    info_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'ehr_system.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(log_format)
    root_logger.addHandler(info_handler)
    
    # 에러 로그 파일 핸들러
    error_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'ehr_error.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_format)
    root_logger.addHandler(error_handler)
    
    # 디버그 로그 파일 핸들러 (개발 환경에서만)
    if os.environ.get('DEBUG', 'False').lower() == 'true':
        debug_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, 'ehr_debug.log'),
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=5,
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(detailed_format)
        root_logger.addHandler(debug_handler)
        root_logger.setLevel(logging.DEBUG)
    
    # 특정 모듈별 로거 설정
    setup_module_loggers(log_dir)


def setup_module_loggers(log_dir: str):
    """모듈별 로거 설정"""
    
    # 비즈니스 로직 로거
    business_logger = logging.getLogger('services')
    business_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'business.log'),
        maxBytes=20 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8'
    )
    business_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    business_logger.addHandler(business_handler)
    business_logger.setLevel(logging.INFO)
    
    # MCP 통합 로거
    mcp_logger = logging.getLogger('core.mcp')
    mcp_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'mcp.log'),
        maxBytes=20 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8'
    )
    mcp_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    mcp_logger.addHandler(mcp_handler)
    mcp_logger.setLevel(logging.INFO)
    
    # 보안 로거
    security_logger = logging.getLogger('security')
    security_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'security.log'),
        maxBytes=50 * 1024 * 1024,
        backupCount=20,
        encoding='utf-8'
    )
    security_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(remote_addr)s - %(user)s - %(message)s'
    ))
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    
    # 성능 로거
    performance_logger = logging.getLogger('performance')
    performance_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'performance.log'),
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    performance_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(message)s'
    ))
    performance_logger.addHandler(performance_handler)
    performance_logger.setLevel(logging.INFO)


class SecurityLogger:
    """보안 관련 로깅"""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
    
    def log_login_attempt(self, username: str, remote_addr: str, success: bool):
        """로그인 시도 로깅"""
        extra = {
            'remote_addr': remote_addr,
            'user': username
        }
        
        if success:
            self.logger.info('Successful login', extra=extra)
        else:
            self.logger.warning('Failed login attempt', extra=extra)
    
    def log_access_denied(self, user: str, resource: str, remote_addr: str):
        """접근 거부 로깅"""
        extra = {
            'remote_addr': remote_addr,
            'user': user
        }
        self.logger.warning(f'Access denied to {resource}', extra=extra)
    
    def log_data_access(self, user: str, model: str, action: str, remote_addr: str):
        """데이터 접근 로깅"""
        extra = {
            'remote_addr': remote_addr,
            'user': user
        }
        self.logger.info(f'{action} on {model}', extra=extra)


class PerformanceLogger:
    """성능 관련 로깅"""
    
    def __init__(self):
        self.logger = logging.getLogger('performance')
    
    def log_slow_query(self, query: str, duration: float):
        """느린 쿼리 로깅"""
        self.logger.warning(f'Slow query ({duration:.2f}s): {query}')
    
    def log_api_response_time(self, endpoint: str, method: str, duration: float):
        """API 응답 시간 로깅"""
        self.logger.info(f'{method} {endpoint}: {duration:.3f}s')
    
    def log_task_execution(self, task_type: str, duration: float, success: bool):
        """작업 실행 시간 로깅"""
        status = 'success' if success else 'failed'
        self.logger.info(f'Task {task_type} {status}: {duration:.2f}s')


# 싱글톤 인스턴스
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()