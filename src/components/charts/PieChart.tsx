import React, { useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface PieChartProps {
  data: {
    labels: string[];
    datasets: {
      label?: string;
      data: number[];
      backgroundColor?: string[];
      borderColor?: string | string[];
      borderWidth?: number;
    }[];
  };
  options?: any;
  height?: number;
}

const PieChart: React.FC<PieChartProps> = ({ data, options = {}, height = 300 }) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // 이전 차트 인스턴스 제거
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    // 다크모드 감지
    const isDarkMode = document.documentElement.classList.contains('dark');

    // 기본 색상 팔레트
    const defaultColors = [
      '#1443FF', // Primary
      '#FFD700', // Accent
      '#10B981', // Green
      '#F59E0B', // Yellow
      '#EF4444', // Red
      '#8B5CF6', // Purple
      '#EC4899', // Pink
      '#6366F1', // Indigo
    ];

    // 기본 옵션 설정
    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right' as const,
          labels: {
            color: isDarkMode ? '#E5E7EB' : '#374151',
            font: {
              family: 'Noto Sans KR',
              size: 12,
            },
            padding: 15,
            generateLabels: (chart: any) => {
              const data = chart.data;
              if (data.labels.length && data.datasets.length) {
                const dataset = data.datasets[0];
                const total = dataset.data.reduce((a: number, b: number) => a + b, 0);
                
                return data.labels.map((label: string, i: number) => {
                  const value = dataset.data[i];
                  const percentage = ((value / total) * 100).toFixed(1);
                  
                  return {
                    text: `${label} (${percentage}%)`,
                    fillStyle: dataset.backgroundColor[i],
                    hidden: false,
                    index: i,
                  };
                });
              }
              return [];
            },
          },
        },
        tooltip: {
          backgroundColor: isDarkMode ? '#1F2937' : '#FFFFFF',
          titleColor: isDarkMode ? '#F3F4F6' : '#111827',
          bodyColor: isDarkMode ? '#D1D5DB' : '#4B5563',
          borderColor: isDarkMode ? '#374151' : '#E5E7EB',
          borderWidth: 1,
          titleFont: {
            family: 'Noto Sans KR',
            weight: 'bold',
          },
          bodyFont: {
            family: 'Noto Sans KR',
          },
          callbacks: {
            label: (context: any) => {
              const label = context.label || '';
              const value = context.parsed;
              const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              return `${label}: ${value.toLocaleString()} (${percentage}%)`;
            },
          },
        },
      },
    };

    // 새 차트 생성
    chartInstance.current = new Chart(ctx, {
      type: 'pie',
      data: {
        ...data,
        datasets: data.datasets.map(dataset => ({
          ...dataset,
          backgroundColor: dataset.backgroundColor || defaultColors,
          borderColor: dataset.borderColor || (isDarkMode ? '#1F2937' : '#FFFFFF'),
          borderWidth: dataset.borderWidth || 2,
        })),
      },
      options: {
        ...defaultOptions,
        ...options,
      },
    });

    // Cleanup
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data, options]);

  return (
    <div style={{ height: `${height}px` }}>
      <canvas ref={chartRef}></canvas>
    </div>
  );
};

export default PieChart;