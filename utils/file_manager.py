"""
파일 관리 유틸리티 모듈
MCP 파일서버를 활용한 향상된 파일 관리 기능 제공
"""
import os
import hashlib
from datetime import datetime
from pathlib import Path
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import mimetypes


class FileManager:
    """파일 관리를 위한 유틸리티 클래스"""
    
    def __init__(self):
        self.media_root = settings.MEDIA_ROOT
        self.allowed_image_types = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        self.allowed_document_types = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv']
        self.max_image_size = 5 * 1024 * 1024  # 5MB
        self.max_document_size = 10 * 1024 * 1024  # 10MB
        
    def validate_file_type(self, file, allowed_types):
        """파일 타입 검증"""
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_types:
            raise ValueError(f"허용되지 않은 파일 형식입니다. 허용 형식: {', '.join(allowed_types)}")
        
        # MIME 타입 추가 검증
        mime_type, _ = mimetypes.guess_type(file.name)
        if mime_type:
            if 'image' in allowed_types[0] and not mime_type.startswith('image/'):
                raise ValueError("이미지 파일이 아닙니다.")
        
        return True
    
    def validate_file_size(self, file, max_size):
        """파일 크기 검증"""
        if file.size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            raise ValueError(f"파일 크기가 {max_size_mb}MB를 초과합니다.")
        return True
    
    def generate_unique_filename(self, original_filename, prefix=''):
        """중복되지 않는 파일명 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(original_filename)
        
        # 파일명 해시 생성 (중복 방지)
        hash_object = hashlib.md5(f"{name}{timestamp}".encode())
        hash_hex = hash_object.hexdigest()[:8]
        
        if prefix:
            return f"{prefix}_{timestamp}_{hash_hex}{ext}"
        return f"{name}_{timestamp}_{hash_hex}{ext}"
    
    def optimize_image(self, image_file, max_width=1200, max_height=1200, quality=85):
        """이미지 최적화 (리사이징 및 압축)"""
        img = Image.open(image_file)
        
        # EXIF 데이터 기반 회전 처리
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
        
        # 리사이징
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # RGB 변환 (RGBA -> RGB)
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        
        # 메모리에 저장
        from io import BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return ContentFile(output.read())
    
    def save_profile_image(self, image_file, employee_id):
        """프로필 이미지 저장"""
        # 파일 검증
        self.validate_file_type(image_file, self.allowed_image_types)
        self.validate_file_size(image_file, self.max_image_size)
        
        # 파일명 생성
        filename = self.generate_unique_filename(
            image_file.name, 
            prefix=f"profile_{employee_id}"
        )
        
        # 이미지 최적화
        optimized_image = self.optimize_image(image_file)
        
        # 저장 경로
        save_path = f"profile_images/{filename}"
        
        # 파일 저장
        path = default_storage.save(save_path, optimized_image)
        
        return path
    
    def delete_file(self, file_path):
        """파일 삭제"""
        if file_path and default_storage.exists(file_path):
            default_storage.delete(file_path)
            return True
        return False
    
    def get_file_info(self, file_path):
        """파일 정보 조회"""
        if not default_storage.exists(file_path):
            return None
            
        file_stat = default_storage.stat(file_path)
        return {
            'path': file_path,
            'size': default_storage.size(file_path),
            'modified_time': file_stat.st_mtime if hasattr(file_stat, 'st_mtime') else None,
            'url': default_storage.url(file_path)
        }
    
    def create_directory_structure(self):
        """필요한 디렉토리 구조 생성"""
        directories = [
            'profile_images',
            'documents',
            'temp',
            'exports',
            'imports'
        ]
        
        for directory in directories:
            dir_path = os.path.join(self.media_root, directory)
            os.makedirs(dir_path, exist_ok=True)
    
    def cleanup_orphaned_files(self):
        """데이터베이스에 연결되지 않은 파일 정리"""
        from employees.models import Employee
        
        # 프로필 이미지 디렉토리 검사
        profile_dir = os.path.join(self.media_root, 'profile_images')
        if not os.path.exists(profile_dir):
            return []
        
        # DB에 있는 모든 프로필 이미지 경로
        db_images = set(Employee.objects.exclude(
            profile_image__isnull=True
        ).exclude(
            profile_image=''
        ).values_list('profile_image', flat=True))
        
        # 실제 파일 시스템의 파일들
        orphaned_files = []
        for filename in os.listdir(profile_dir):
            file_path = f"profile_images/{filename}"
            if file_path not in db_images:
                orphaned_files.append(file_path)
        
        return orphaned_files


class ExcelFileHandler:
    """Excel 파일 처리를 위한 핸들러"""
    
    def __init__(self):
        self.max_rows = 1000  # 최대 처리 가능 행 수
        
    def validate_excel_file(self, file):
        """Excel 파일 검증"""
        import pandas as pd
        
        # 파일 확장자 검사
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.xlsx', '.xls', '.csv']:
            raise ValueError("Excel 또는 CSV 파일만 업로드 가능합니다.")
        
        # 파일 크기 검사 (10MB 제한)
        if file.size > 10 * 1024 * 1024:
            raise ValueError("파일 크기가 10MB를 초과합니다.")
        
        # 파일 내용 검사
        try:
            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file, nrows=5)  # 처음 5행만 검사
            else:
                df = pd.read_csv(file, nrows=5)
                
            # 필수 컬럼 검사 - 부서 또는 최종소속 중 하나만 있어도 OK
            required_columns = ['이름', '이메일']
            if '부서' not in df.columns and '최종소속' not in df.columns:
                required_columns.append('부서 또는 최종소속')
            
            missing_columns = []
            for col in required_columns:
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                raise ValueError(f"필수 컬럼이 없습니다: {', '.join(missing_columns)}")
                
        except Exception as e:
            raise ValueError(f"파일을 읽을 수 없습니다: {str(e)}")
        
        return True
    
    def process_employee_excel(self, file):
        """직원 정보 Excel 파일 처리"""
        import pandas as pd
        
        # 파일 검증
        self.validate_excel_file(file)
        
        # 파일 읽기
        ext = os.path.splitext(file.name)[1].lower()
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file, dtype=str)
        else:
            df = pd.read_csv(file, dtype=str)
        
        # 행 수 제한 검사
        if len(df) > self.max_rows:
            raise ValueError(f"최대 {self.max_rows}개의 행만 처리 가능합니다.")
        
        # 데이터 정제
        df = df.fillna('')  # NaN을 빈 문자열로 변환
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        # 딕셔너리 리스트로 변환
        records = df.to_dict('records')
        
        return records, len(records)
    
    def generate_error_report(self, errors, original_filename):
        """오류 보고서 Excel 생성"""
        import pandas as pd
        from io import BytesIO
        
        # 오류 데이터프레임 생성
        error_df = pd.DataFrame(errors)
        
        # BytesIO 객체에 Excel 파일 생성
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            error_df.to_excel(writer, index=False, sheet_name='오류내역')
            
            # 워크시트 스타일링
            worksheet = writer.sheets['오류내역']
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
        
        output.seek(0)
        
        # 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"오류보고서_{os.path.splitext(original_filename)[0]}_{timestamp}.xlsx"
        
        return output.read(), filename