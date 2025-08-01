import React, { useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface BarChartProps {
  data: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor?: string | string[];
      borderColor?: string | string[];
      borderWidth?: number;
    }[];
  };
  options?: any;
  height?: number;
}

const BarChart: React.FC<BarChartProps> = ({ data, options = {}, height = 300 }) => {
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

    // 기본 옵션 설정
    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top' as const,
          labels: {
            color: isDarkMode ? '#E5E7EB' : '#374151',
            font: {
              family: 'Noto Sans KR',
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
        },
      },
      scales: {
        x: {
          ticks: {
            color: isDarkMode ? '#9CA3AF' : '#4B5563',
            font: {
              family: 'Noto Sans KR',
            },
          },
          grid: {
            color: isDarkMode ? '#374151' : '#E5E7EB',
            display: false,
          },
        },
        y: {
          ticks: {
            color: isDarkMode ? '#9CA3AF' : '#4B5563',
            font: {
              family: 'Noto Sans KR',
            },
          },
          grid: {
            color: isDarkMode ? '#374151' : '#E5E7EB',
          },
        },
      },
    };

    // 새 차트 생성
    chartInstance.current = new Chart(ctx, {
      type: 'bar',
      data: {
        ...data,
        datasets: data.datasets.map(dataset => ({
          ...dataset,
          backgroundColor: dataset.backgroundColor || '#1443FF',
          borderColor: dataset.borderColor || '#0E35CC',
          borderWidth: dataset.borderWidth || 0,
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

export default BarChart;