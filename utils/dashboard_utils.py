"""
Dashboard Utilities - Common dashboard data aggregation and formatting
"""
from typing import Dict, Any, List, Optional
from django.db.models import Count, Avg, Sum, Max, Min, QuerySet
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DashboardAggregator:
    """Common dashboard data aggregation utilities"""
    
    @staticmethod
    def get_employee_statistics(employee_queryset: QuerySet) -> Dict[str, Any]:
        """
        Get common employee statistics
        
        Args:
            employee_queryset: QuerySet of Employee model
            
        Returns:
            Dictionary with employee statistics
        """
        try:
            total = employee_queryset.count()
            active = employee_queryset.filter(employment_status='재직').count()
            
            # Department distribution
            dept_distribution = employee_queryset.values('department').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Recent hires (last 30 days)
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            new_hires = employee_queryset.filter(
                hire_date__gte=thirty_days_ago
            ).count()
            
            # Recent resignations (resignation_date 필드가 없는 경우 0)
            resignations = 0  # Employee 모델에 resignation_date가 없음
            
            return {
                'total_employees': total,
                'active_employees': active,
                'new_hires_month': new_hires,
                'resignations_month': resignations,
                'department_distribution': list(dept_distribution)
            }
            
        except Exception as e:
            logger.error(f"Error calculating employee statistics: {e}")
            return {
                'total_employees': 0,
                'active_employees': 0,
                'new_hires_month': 0,
                'resignations_month': 0,
                'department_distribution': []
            }
    
    @staticmethod
    def get_compensation_statistics(compensation_queryset: QuerySet) -> Dict[str, Any]:
        """
        Get compensation statistics
        
        Args:
            compensation_queryset: QuerySet of Compensation model
            
        Returns:
            Dictionary with compensation statistics
        """
        try:
            stats = compensation_queryset.aggregate(
                total=Sum('total_compensation'),
                average=Avg('total_compensation'),
                maximum=Max('total_compensation'),
                minimum=Min('total_compensation')
            )
            
            return {
                'total_payroll': float(stats.get('total') or 0),
                'avg_salary': float(stats.get('average') or 0),
                'max_salary': float(stats.get('maximum') or 0),
                'min_salary': float(stats.get('minimum') or 0)
            }
            
        except Exception as e:
            logger.error(f"Error calculating compensation statistics: {e}")
            return {
                'total_payroll': 0,
                'avg_salary': 0,
                'max_salary': 0,
                'min_salary': 0
            }
    
    @staticmethod
    def get_department_summary(
        employee_queryset: QuerySet,
        include_compensation: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get department-wise summary
        
        Args:
            employee_queryset: QuerySet of Employee model
            include_compensation: Whether to include compensation data
            
        Returns:
            List of department summaries
        """
        try:
            query = employee_queryset.values('department').annotate(
                employee_count=Count('id')
            )
            
            if include_compensation:
                query = query.annotate(
                    avg_salary=Avg('compensations__total_compensation')
                )
            
            departments = []
            for dept in query.order_by('-employee_count'):
                dept_data = {
                    'department_name': dept.get('department') or 'Unknown',
                    'employee_count': dept.get('employee_count', 0)
                }
                
                if include_compensation:
                    dept_data['avg_salary'] = float(dept.get('avg_salary') or 0)
                
                departments.append(dept_data)
            
            return departments
            
        except Exception as e:
            logger.error(f"Error calculating department summary: {e}")
            return []
    
    @staticmethod
    def format_kpi_card(
        title: str,
        value: Any,
        icon: str = 'fas fa-chart-line',
        trend_direction: Optional[str] = None,
        trend_value: Optional[float] = None,
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format data for KPI card display
        
        Args:
            title: KPI title
            value: KPI value
            icon: Icon class for display
            trend_direction: 'up', 'down', or None
            trend_value: Percentage change
            period: Time period for trend
            
        Returns:
            Formatted KPI card data
        """
        kpi_data = {
            'title': title,
            'value': value,
            'icon': icon
        }
        
        if trend_direction:
            kpi_data['trend_direction'] = trend_direction
            
        if trend_value is not None:
            kpi_data['trend_value'] = trend_value
            
        if period:
            kpi_data['period'] = period
            
        return kpi_data
    
    @staticmethod
    def get_monthly_trend(
        queryset: QuerySet,
        date_field: str,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get monthly trend data
        
        Args:
            queryset: QuerySet to analyze
            date_field: Name of date field to group by
            months: Number of months to include
            
        Returns:
            List of monthly data points
        """
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=months * 30)
            
            # Filter by date range
            filter_kwargs = {
                f"{date_field}__range": [start_date, end_date]
            }
            filtered_qs = queryset.filter(**filter_kwargs)
            
            # Group by month (simplified version)
            monthly_data = []
            for i in range(months):
                month_start = end_date - timedelta(days=(i+1) * 30)
                month_end = end_date - timedelta(days=i * 30)
                
                month_filter = {
                    f"{date_field}__range": [month_start, month_end]
                }
                count = queryset.filter(**month_filter).count()
                
                monthly_data.append({
                    'month': month_start.strftime('%Y-%m'),
                    'count': count
                })
            
            return list(reversed(monthly_data))
            
        except Exception as e:
            logger.error(f"Error calculating monthly trend: {e}")
            return []


class ChartDataFormatter:
    """Format data for various chart types"""
    
    @staticmethod
    def format_bar_chart(
        labels: List[str],
        data: List[float],
        label: str = 'Data',
        colors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Format data for bar chart
        
        Args:
            labels: X-axis labels
            data: Y-axis data points
            label: Dataset label
            colors: Optional color array
            
        Returns:
            Formatted chart data
        """
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': label,
                'data': data
            }]
        }
        
        if colors:
            chart_data['datasets'][0]['backgroundColor'] = colors
        else:
            # Default colors
            chart_data['datasets'][0]['backgroundColor'] = [
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 99, 132, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(75, 192, 192, 0.5)',
                'rgba(153, 102, 255, 0.5)'
            ][:len(data)]
        
        return chart_data
    
    @staticmethod
    def format_pie_chart(
        labels: List[str],
        data: List[float],
        colors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Format data for pie chart
        
        Args:
            labels: Segment labels
            data: Segment values
            colors: Optional color array
            
        Returns:
            Formatted chart data
        """
        chart_data = {
            'labels': labels,
            'datasets': [{
                'data': data
            }]
        }
        
        if colors:
            chart_data['datasets'][0]['backgroundColor'] = colors
        else:
            # Default colors for pie chart
            chart_data['datasets'][0]['backgroundColor'] = [
                '#FF6384',
                '#36A2EB',
                '#FFCE56',
                '#4BC0C0',
                '#9966FF',
                '#FF9F40'
            ][:len(data)]
        
        return chart_data
    
    @staticmethod
    def format_line_chart(
        labels: List[str],
        datasets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Format data for line chart
        
        Args:
            labels: X-axis labels
            datasets: List of dataset dictionaries
            
        Returns:
            Formatted chart data
        """
        return {
            'labels': labels,
            'datasets': datasets
        }


def calculate_growth_rate(
    current_value: float,
    previous_value: float,
    decimal_places: int = 1
) -> Dict[str, Any]:
    """
    Calculate growth rate between two values
    
    Args:
        current_value: Current period value
        previous_value: Previous period value
        decimal_places: Number of decimal places for percentage
        
    Returns:
        Dictionary with growth rate and direction
    """
    if previous_value == 0:
        return {
            'rate': 0,
            'direction': 'stable',
            'percentage': '0%'
        }
    
    rate = ((current_value - previous_value) / previous_value) * 100
    direction = 'up' if rate > 0 else 'down' if rate < 0 else 'stable'
    
    return {
        'rate': round(rate, decimal_places),
        'direction': direction,
        'percentage': f"{abs(round(rate, decimal_places))}%"
    }


def format_currency(
    value: float,
    currency: str = '₩',
    decimal_places: int = 0
) -> str:
    """
    Format value as currency string
    
    Args:
        value: Numeric value
        currency: Currency symbol
        decimal_places: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    if decimal_places > 0:
        formatted_value = f"{value:,.{decimal_places}f}"
    else:
        formatted_value = f"{int(value):,}"
    
    return f"{currency}{formatted_value}"


def format_percentage(
    value: float,
    decimal_places: int = 1,
    include_sign: bool = True
) -> str:
    """
    Format value as percentage string
    
    Args:
        value: Numeric value (already in percentage)
        decimal_places: Number of decimal places
        include_sign: Whether to include + sign for positive values
        
    Returns:
        Formatted percentage string
    """
    formatted = f"{value:.{decimal_places}f}%"
    
    if include_sign and value > 0:
        formatted = f"+{formatted}"
    
    return formatted