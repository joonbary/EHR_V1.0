"""
File Upload Utility - Centralized file upload handling to remove duplication
"""
import os
import uuid
from typing import Optional, Tuple, Dict, Any, List
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse
from employees.models import HRFileUpload
from utils.security import validate_file_upload
import logging

logger = logging.getLogger(__name__)


class FileUploadHandler:
    """Centralized file upload handler to eliminate code duplication"""
    
    ALLOWED_EXTENSIONS = {
        'excel': ['.xlsx', '.xls'],
        'csv': ['.csv'],
        'pdf': ['.pdf'],
        'image': ['.jpg', '.jpeg', '.png', '.gif'],
        'document': ['.doc', '.docx', '.pdf', '.txt']
    }
    
    MAX_FILE_SIZE = {
        'default': 10 * 1024 * 1024,  # 10MB
        'large': 50 * 1024 * 1024,    # 50MB
        'image': 5 * 1024 * 1024,     # 5MB
    }
    
    def __init__(self, file_type: str = 'excel', size_category: str = 'default'):
        """
        Initialize file upload handler
        
        Args:
            file_type: Type of file to handle (excel, csv, pdf, image, document)
            size_category: Size category for max file size (default, large, image)
        """
        self.file_type = file_type
        self.allowed_extensions = self.ALLOWED_EXTENSIONS.get(file_type, ['.xlsx', '.xls'])
        self.max_file_size = self.MAX_FILE_SIZE.get(size_category, self.MAX_FILE_SIZE['default'])
    
    def validate_and_save(
        self, 
        file: UploadedFile, 
        upload_path: str = 'uploads',
        record_type: Optional[str] = None,
        user=None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate and save uploaded file
        
        Args:
            file: Uploaded file object
            upload_path: Directory path for saving file
            record_type: Type of upload record to create
            user: User uploading the file
            
        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Validate file
            is_valid, error_message = validate_file_upload(
                file, 
                self.allowed_extensions, 
                self.max_file_size / (1024 * 1024)  # Convert to MB
            )
            
            if not is_valid:
                return False, {'error': error_message}
            
            # Generate unique filename
            file_ext = os.path.splitext(file.name)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = f"{upload_path}/{unique_filename}"
            
            # Save file
            saved_path = default_storage.save(file_path, file)
            full_path = default_storage.path(saved_path)
            
            # Create upload record if requested
            upload_record = None
            if record_type:
                upload_record = HRFileUpload.objects.create(
                    file_name=file.name,
                    file_type=record_type,
                    file_path=saved_path,
                    uploaded_by=user,
                    status='UPLOADED'
                )
            
            result = {
                'success': True,
                'file_path': saved_path,
                'full_path': full_path,
                'original_name': file.name,
                'file_size': file.size,
                'upload_record': upload_record
            }
            
            logger.info(f"File uploaded successfully: {file.name} -> {saved_path}")
            return True, result
            
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}", exc_info=True)
            return False, {'error': f'파일 업로드 실패: {str(e)}'}
    
    def process_with_parser(
        self,
        file: UploadedFile,
        parser_class,
        upload_path: str = 'uploads',
        record_type: Optional[str] = None,
        user=None,
        **parser_kwargs
    ) -> JsonResponse:
        """
        Upload file and process with specified parser
        
        Args:
            file: Uploaded file object
            parser_class: Parser class to process the file
            upload_path: Directory path for saving file
            record_type: Type of upload record to create
            user: User uploading the file
            **parser_kwargs: Additional arguments for parser
            
        Returns:
            JsonResponse with processing results
        """
        # Step 1: Validate and save file
        success, upload_result = self.validate_and_save(
            file, upload_path, record_type, user
        )
        
        if not success:
            return JsonResponse(upload_result, status=400)
        
        try:
            # Step 2: Initialize parser
            parser = parser_class(**parser_kwargs)
            
            # Step 3: Process file
            parse_result = parser.parse(upload_result['full_path'])
            
            # Step 4: Update upload record status
            if upload_result.get('upload_record'):
                upload_result['upload_record'].status = 'PROCESSED'
                upload_result['upload_record'].save()
            
            # Step 5: Return results
            response_data = {
                'success': True,
                'message': '파일이 성공적으로 처리되었습니다.',
                'file_info': {
                    'original_name': upload_result['original_name'],
                    'file_size': upload_result['file_size'],
                    'upload_id': upload_result['upload_record'].id if upload_result.get('upload_record') else None
                },
                'data': parse_result
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"File processing failed: {str(e)}", exc_info=True)
            
            # Update upload record as failed
            if upload_result.get('upload_record'):
                upload_result['upload_record'].status = 'FAILED'
                upload_result['upload_record'].error_message = str(e)
                upload_result['upload_record'].save()
            
            return JsonResponse({
                'success': False,
                'error': f'파일 처리 실패: {str(e)}'
            }, status=500)


class ExcelProcessor:
    """Base class for Excel file processing to reduce duplication"""
    
    def __init__(self):
        self.column_mapping = {}
        self.required_columns = []
    
    def validate_columns(self, df) -> Tuple[bool, Optional[str]]:
        """Validate required columns exist in DataFrame"""
        missing_columns = []
        for col in self.required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            return False, f"필수 컬럼이 없습니다: {', '.join(missing_columns)}"
        return True, None
    
    def map_columns(self, df):
        """Map DataFrame columns to standard names"""
        if self.column_mapping:
            df = df.rename(columns=self.column_mapping)
        return df
    
    def clean_data(self, df):
        """Clean and standardize data"""
        # Remove empty rows
        df = df.dropna(how='all')
        
        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()
        
        return df
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """Main processing method to be overridden by subclasses"""
        import pandas as pd
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Validate columns
        is_valid, error = self.validate_columns(df)
        if not is_valid:
            raise ValueError(error)
        
        # Map columns
        df = self.map_columns(df)
        
        # Clean data
        df = self.clean_data(df)
        
        # Process data (to be implemented by subclasses)
        return self.process_data(df)
    
    def process_data(self, df) -> Dict[str, Any]:
        """Process cleaned DataFrame - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement process_data method")


def create_standard_response(
    success: bool,
    message: str = None,
    data: Any = None,
    error: str = None,
    status_code: int = 200
) -> JsonResponse:
    """
    Create standardized JSON response
    
    Args:
        success: Whether operation was successful
        message: Success message
        data: Response data
        error: Error message
        status_code: HTTP status code
        
    Returns:
        JsonResponse with standardized format
    """
    response_data = {'success': success}
    
    if message:
        response_data['message'] = message
    if data is not None:
        response_data['data'] = data
    if error:
        response_data['error'] = error
    
    return JsonResponse(response_data, status=status_code)