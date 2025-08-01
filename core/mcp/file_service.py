"""
MCP 파일서버 통합 서비스
파일 관리를 위한 통합 인터페이스 제공
"""
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pandas as pd
import logging

from core.exceptions import FileProcessingError, ValidationError
from core.validators import FileValidators


logger = logging.getLogger(__name__)


class MCPFileService:
    """MCP 파일서버 서비스"""
    
    def __init__(self):
        self.media_root = Path(settings.MEDIA_ROOT)
        self.file_validators = FileValidators()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """필요한 디렉토리 생성"""
        directories = [
            'profile_images',
            'documents',
            'exports',
            'imports',
            'temp'
        ]
        for directory in directories:
            (self.media_root / directory).mkdir(parents=True, exist_ok=True)
    
    # 이미지 처리
    def process_profile_image(
        self,
        image_file,
        employee_id: str,
        max_size: Tuple[int, int] = (800, 800),
        quality: int = 85
    ) -> str:
        """프로필 이미지 처리 및 저장"""
        try:
            # 검증
            self.file_validators.validate_image_file(image_file)
            
            # 이미지 열기
            img = Image.open(image_file)
            
            # EXIF 데이터 처리 (회전 보정)
            img = self._fix_image_orientation(img)
            
            # 리사이징
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # RGB 변환
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # 파일명 생성
            filename = self._generate_unique_filename(
                f"profile_{employee_id}",
                '.jpg'
            )
            
            # 저장
            from io import BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            path = f"profile_images/{filename}"
            saved_path = default_storage.save(path, ContentFile(output.read()))
            
            logger.info(f"Profile image saved: {saved_path}")
            return saved_path
            
        except Exception as e:
            logger.error(f"Profile image processing error: {str(e)}")
            raise FileProcessingError(f"프로필 이미지 처리 실패: {str(e)}")
    
    def _fix_image_orientation(self, img: Image.Image) -> Image.Image:
        """EXIF 데이터 기반 이미지 회전 보정"""
        try:
            from PIL import ExifTags
            
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            
            exif = img._getexif()
            if exif and orientation in exif:
                if exif[orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    img = img.rotate(90, expand=True)
        except:
            pass
        
        return img
    
    # Excel 처리
    def process_excel_import(
        self,
        file,
        required_columns: List[str],
        max_rows: int = 10000
    ) -> Tuple[pd.DataFrame, Dict]:
        """Excel 파일 임포트 처리"""
        try:
            # 파일 타입 확인
            ext = os.path.splitext(file.name)[1].lower()
            
            # 데이터 읽기
            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file, dtype=str)
            elif ext == '.csv':
                df = pd.read_csv(file, dtype=str)
            else:
                raise ValidationError("지원하지 않는 파일 형식입니다.")
            
            # 크기 검증
            if len(df) > max_rows:
                raise ValidationError(f"최대 {max_rows}개 행까지만 처리 가능합니다.")
            
            # 필수 컬럼 검증
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                raise ValidationError(
                    f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}"
                )
            
            # 데이터 정제
            df = df.fillna('')
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            
            # 통계 정보
            stats = {
                'total_rows': len(df),
                'columns': list(df.columns),
                'missing_values': df.isnull().sum().to_dict()
            }
            
            logger.info(f"Excel import processed: {stats['total_rows']} rows")
            return df, stats
            
        except Exception as e:
            logger.error(f"Excel import error: {str(e)}")
            raise FileProcessingError(f"Excel 파일 처리 실패: {str(e)}")
    
    def generate_excel_export(
        self,
        data: Union[List[Dict], pd.DataFrame],
        filename: str,
        sheet_name: str = 'Sheet1',
        include_timestamp: bool = True
    ) -> str:
        """Excel 파일 생성 및 저장"""
        try:
            # DataFrame 변환
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            # 파일명 생성
            if include_timestamp:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_name = os.path.splitext(filename)[0]
                filename = f"{base_name}_{timestamp}.xlsx"
            
            # 파일 경로
            file_path = self.media_root / 'exports' / filename
            
            # Excel 파일 생성
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 열 너비 자동 조정
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"Excel export generated: {filename}")
            return f"exports/{filename}"
            
        except Exception as e:
            logger.error(f"Excel export error: {str(e)}")
            raise FileProcessingError(f"Excel 파일 생성 실패: {str(e)}")
    
    # 파일 관리
    def delete_file(self, file_path: str) -> bool:
        """파일 삭제"""
        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"File deletion error: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """파일 정보 조회"""
        try:
            if not default_storage.exists(file_path):
                return None
            
            file_stat = default_storage.stat(file_path)
            return {
                'path': file_path,
                'size': default_storage.size(file_path),
                'modified_time': file_stat.st_mtime if hasattr(file_stat, 'st_mtime') else None,
                'url': default_storage.url(file_path),
                'exists': True
            }
        except Exception as e:
            logger.error(f"File info error: {str(e)}")
            return None
    
    def _generate_unique_filename(self, prefix: str, extension: str) -> str:
        """유니크한 파일명 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_hash = hashlib.md5(f"{prefix}{timestamp}".encode()).hexdigest()[:8]
        return f"{prefix}_{timestamp}_{random_hash}{extension}"
    
    def cleanup_temp_files(self, older_than_hours: int = 24):
        """임시 파일 정리"""
        try:
            temp_dir = self.media_root / 'temp'
            cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
            
            cleaned_count = 0
            for file_path in temp_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
            
            logger.info(f"Cleaned {cleaned_count} temp files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Temp file cleanup error: {str(e)}")
            return 0
    
    def get_storage_stats(self) -> Dict:
        """저장소 통계 정보"""
        stats = {
            'profile_images': 0,
            'documents': 0,
            'exports': 0,
            'total_size': 0
        }
        
        try:
            for directory in ['profile_images', 'documents', 'exports']:
                dir_path = self.media_root / directory
                if dir_path.exists():
                    files = list(dir_path.iterdir())
                    stats[directory] = len(files)
                    stats['total_size'] += sum(f.stat().st_size for f in files if f.is_file())
            
            # 크기를 MB로 변환
            stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
            
        except Exception as e:
            logger.error(f"Storage stats error: {str(e)}")
        
        return stats