
// Chart.js Heatmap Plugin Required
// npm install chartjs-chart-matrix

class OptimizedHeatmap {
    constructor(canvasId, data) {
        this.canvasId = canvasId;
        this.data = data;
        this.chart = null;
        this.init();
    }
    
    init() {
        const canvas = document.getElementById(this.canvasId);
        const ctx = canvas.getContext('2d');
        
        // 동적 크기 계산
        const cellSize = this.calculateCellSize();
        const fontSize = this.calculateFontSize();
        
        // 캔버스 크기 설정
        canvas.height = this.data.employees.length * cellSize + 200;
        canvas.width = this.data.skills.length * cellSize + 300;
        
        // 데이터 변환
        const matrixData = this.transformData();
        
        this.chart = new Chart(ctx, {
            type: 'matrix',
            data: {
                datasets: [{
                    label: 'Skill Proficiency',
                    data: matrixData,
                    backgroundColor(context) {
                        const value = context.dataset.data[context.dataIndex].v;
                        const alpha = value / 100;
                        return `rgba(49, 130, 189, ${alpha})`;
                    },
                    borderColor: 'rgba(49, 130, 189, 0.5)',
                    borderWidth: 1,
                    width: cellSize - 2,
                    height: cellSize - 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title() {
                                return '';
                            },
                            label(context) {
                                const v = context.dataset.data[context.dataIndex];
                                return [
                                    `Employee: ${v.employee}`,
                                    `Skill: ${v.skill}`,
                                    `Proficiency: ${v.v}%`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'category',
                        labels: this.data.skills,
                        position: 'top',
                        ticks: {
                            autoSkip: false,
                            maxRotation: 45,
                            minRotation: 45,
                            font: {
                                size: fontSize
                            }
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        type: 'category',
                        labels: this.data.employees,
                        ticks: {
                            autoSkip: false,
                            font: {
                                size: fontSize
                            }
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    calculateCellSize() {
        const maxCells = Math.max(this.data.employees.length, this.data.skills.length);
        if (maxCells > 50) return 15;
        if (maxCells > 30) return 20;
        return 25;
    }
    
    calculateFontSize() {
        const maxLabels = Math.max(this.data.employees.length, this.data.skills.length);
        if (maxLabels > 50) return 8;
        if (maxLabels > 30) return 10;
        return 12;
    }
    
    transformData() {
        const result = [];
        this.data.employees.forEach((employee, y) => {
            this.data.skills.forEach((skill, x) => {
                result.push({
                    x: skill,
                    y: employee,
                    v: this.data.values[y][x],
                    employee: employee,
                    skill: skill
                });
            });
        });
        return result;
    }
    
    updateData(newData) {
        this.data = newData;
        this.chart.destroy();
        this.init();
    }
    
    resize() {
        if (this.chart) {
            this.chart.resize();
        }
    }
}

// 사용 예시
const sampleData = {
    employees: Array.from({length: 30}, (_, i) => `Employee ${i + 1}`),
    skills: Array.from({length: 15}, (_, i) => `Skill ${i + 1}`),
    values: Array.from({length: 30}, () => 
        Array.from({length: 15}, () => Math.floor(Math.random() * 100))
    )
};

const heatmap = new OptimizedHeatmap('heatmapCanvas', sampleData);

// 반응형 대응
window.addEventListener('resize', () => {
    heatmap.resize();
});
