// 법인별 상세 정보 업데이트 - 엑셀 형식 정확히 반영 (V2)
function updateCorporationDetails(data) {
    const container = document.getElementById('corporationDetails');
    container.innerHTML = '';
    
    if (!data || data.length === 0) {
        container.innerHTML = '<p class="text-center text-gray-500 py-8">데이터가 없습니다.</p>';
        return;
    }
    
    console.log('Corporation data:', data);  // 디버깅용
    
    data.forEach(corp => {
        console.log('Processing corp:', corp);  // 디버깅용
        let corpClass = '';
        if (corp.corporation.includes('OK Bank')) corpClass = 'corp-ok-bank';
        else if (corp.corporation.includes('OK Asset')) corpClass = 'corp-ok-asset';
        else if (corp.corporation.includes('PPCBank')) corpClass = 'corp-ppcbank';
        else if (corp.corporation.includes('천진법인')) corpClass = 'corp-tianjin';
        
        const corpDiv = document.createElement('div');
        corpDiv.className = `border border-gray-200 dark:border-gray-700 rounded-lg mb-6 ${corpClass}`;
        
        // 새로운 데이터 구조 확인
        if (corp.structure && corp.structure.headers) {
            // V2 형식의 데이터
            corpDiv.innerHTML = createTableV2(corp);
        } else if (corp.ranks || corp.positions) {
            // 기존 형식의 데이터 (호환성)
            corpDiv.innerHTML = createTableLegacy(corp);
        } else {
            // 데이터 구조를 알 수 없음
            corpDiv.innerHTML = `<div class="p-4">데이터 형식 오류</div>`;
        }
        
        container.appendChild(corpDiv);
    });
    
    // Lucide 아이콘 초기화
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// V2 형식 테이블 생성 - 정확한 엑셀 구조 반영
function createTableV2(corp) {
    console.log('Creating V2 table for:', corp);  // 디버깅용
    
    const { structure, totals } = corp;
    if (!structure || !structure.headers) {
        console.error('Invalid structure:', structure);
        return '<div class="p-4">데이터 구조 오류</div>';
    }
    
    const { headers } = structure;
    const { positions, categories } = headers;
    
    console.log('Positions:', positions);  // 디버깅용
    console.log('Categories:', categories);  // 디버깅용
    
    let html = `
        <div class="p-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">${corp.corporation}</h3>
            <div class="overflow-x-auto">
                <table class="w-full border-collapse text-sm">
                    <thead>
    `;
    
    // 헤더 행 생성
    html += createHeaderRows(corp.corporation, positions);
    html += `</thead><tbody>`;
    
    // 종합직 섹션
    if (categories['종합직']) {
        html += createCategorySection('종합직', categories['종합직'], positions);
    }
    
    // 계약직 섹션
    if (categories['계약직']) {
        html += createCategorySection('계약직', categories['계약직'], positions);
    }
    
    // 파견(도급)을 포함한 총계 행
    if (totals['총계']) {
        // 천진법인의 경우 특별 처리
        if (corp.corporation === '천진법인 (중국)') {
            html += createTotalRowForChina('총계', totals['총계'], positions, true);
        } else {
            html += createTotalRow('총계', totals['총계'], positions, true);
        }
    }
    
    // 파견(도급) 섹션
    if (categories['파견(도급)']) {
        console.log('파견(도급) found for:', corp.corporation);  // 디버깅용
        html += createCategorySection('파견(도급)', categories['파견(도급)'], positions);
    } else {
        console.log('파견(도급) NOT found for:', corp.corporation);  // 디버깅용
    }
    
    // 파견(도급)을 포함한 최종 총계 행 (모든 법인에 표시)
    if (categories['파견(도급)'] && totals['총계']) {
        // 파견 데이터가 있으면 파견 포함 총계 계산
        const dispatchSubtotal = categories['파견(도급)']['소계'];
        if (dispatchSubtotal) {
            const grandTotal = {};
            let grandTotalSum = 0;
            
            positions.forEach(pos => {
                if (pos !== '계') {  // '계' 컬럼은 별도로 계산
                    const value = (totals['총계'][pos] || 0) + (dispatchSubtotal[pos] || 0);
                    grandTotal[pos] = value;
                    grandTotalSum += value;
                }
            });
            
            // '계' 컬럼이 있으면 총합 추가
            if (positions.includes('계')) {
                // 천진법인의 경우 인원 컬럼만 있으므로 특별 처리
                if (corp.corporation === '천진법인 (중국)' && positions.length === 2) {
                    grandTotal['계'] = grandTotal['인원'] || 0;
                } else {
                    grandTotal['계'] = grandTotalSum;
                }
            }
            
            // 천진법인의 경우 특별 처리
            if (corp.corporation === '천진법인 (중국)') {
                html += createTotalRowForChina('총계 (파견 포함)', grandTotal, positions, true);
            } else {
                html += createTotalRow('총계 (파견 포함)', grandTotal, positions, true);
            }
        }
    }
    
    // 전월비증감 행
    if (totals['전월비증감(파견제외)'] || totals['전월비증감']) {
        const changeData = totals['전월비증감(파견제외)'] || totals['전월비증감'];
        
        // 천진법인의 경우 특별 처리
        if (corp.corporation === '천진법인 (중국)') {
            html += createTotalRowForChina('전월비증감(파견제외)', changeData, positions, false);
        } else {
            html += createTotalRow('전월비증감(파견제외)', changeData, positions, false);
        }
    }
    
    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    return html;
}

// 헤더 행 생성
function createHeaderRows(corporation, positions) {
    let html = '';
    
    // 천진법인은 특별한 헤더 구조
    if (corporation === '천진법인 (중국)') {
        // 첫 번째 헤더 행 - 법인명
        html += `
            <tr>
                <th colspan="2" class="border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 px-4 py-2 text-left font-bold">
                    ${corporation}
                </th>
                <th class="border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 px-4 py-2 text-center">인원</th>
                <th class="border border-gray-300 dark:border-gray-600 bg-orange-100 dark:bg-orange-900 px-4 py-2 text-center font-bold">계</th>
            </tr>
        `;
        
        // 두 번째 헤더 행 - 구분
        html += `
            <tr>
                <th class="border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 px-4 py-2 text-center">구분</th>
                <th class="border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 px-4 py-2 text-center">직급</th>
                <th class="border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700"></th>
                <th class="border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700"></th>
            </tr>
        `;
    } else {
        // 다른 법인들의 헤더
        // 첫 번째 헤더 행 - 법인명
        html += `
            <tr>
                <th colspan="2" class="border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 px-4 py-2 text-left font-bold">
                    ${corporation}
                </th>
        `;
        
        // 직책 헤더
        positions.forEach(pos => {
            html += `<th class="border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 px-4 py-2 text-center">${pos}</th>`;
        });
        
        html += `<th class="border border-gray-300 dark:border-gray-600 bg-orange-100 dark:bg-orange-900 px-4 py-2 text-center font-bold">계</th>`;
        html += `</tr>`;
        
        // 두 번째 헤더 행 - 구분
        html += `
            <tr>
                <th class="border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 px-4 py-2 text-center">구분</th>
                <th class="border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 px-4 py-2 text-center">직급</th>
        `;
        
        // 빈 셀들
        positions.forEach(() => {
            html += `<th class="border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700"></th>`;
        });
        
        html += `<th class="border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700"></th>`;
        html += `</tr>`;
    }
    
    return html;
}

// 카테고리 섹션 생성 (종합직, 계약직, 파견)
function createCategorySection(categoryName, categoryData, positions) {
    let html = '';
    const ranks = categoryData['직급'] || [];
    const data = categoryData['data'] || {};
    
    // 첫 번째 직급에만 카테고리명 표시
    ranks.forEach((rank, index) => {
        html += `<tr>`;
        
        // 카테고리명 (첫 행에만)
        if (index === 0) {
            html += `<td rowspan="${ranks.length}" class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center font-medium bg-gray-50 dark:bg-gray-700">${categoryName}</td>`;
        }
        
        // 직급
        html += `<td class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center">${rank}</td>`;
        
        // 각 직책별 데이터
        const rankData = data[rank] || {};
        positions.forEach(pos => {
            const value = rankData[pos] || 0;
            html += `<td class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center">${value || '-'}</td>`;
        });
        
        // 계 컬럼 - positions에 '계'가 없는 경우에만 추가
        if (!positions.includes('계')) {
            const total = rankData['계'] || 0;
            html += `<td class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center font-medium bg-orange-50 dark:bg-orange-900/20">${total || '-'}</td>`;
        }
        
        html += `</tr>`;
    });
    
    // 소계 행
    if (categoryData['소계']) {
        html += createSubtotalRow(`${categoryName} 계`, categoryData['소계'], positions);
    }
    
    return html;
}

// 소계 행 생성
function createSubtotalRow(label, data, positions) {
    let html = `<tr class="bg-gray-100 dark:bg-gray-800">`;
    html += `<td colspan="2" class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center font-medium">${label}</td>`;
    
    let rowTotal = 0;
    positions.forEach(pos => {
        const value = data[pos] || 0;
        html += `<td class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center font-medium">${value || '-'}</td>`;
        
        // '계' 컬럼이 아닌 경우에만 합계에 추가
        if (pos !== '계') {
            rowTotal += (typeof value === 'number' ? value : 0);
        }
    });
    
    // '계' 컬럼이 positions에 포함되어 있지 않은 경우에만 추가
    if (!positions.includes('계')) {
        const total = data['계'] || rowTotal || 0;
        html += `<td class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center font-bold bg-orange-100 dark:bg-orange-900">${total || '-'}</td>`;
    }
    
    html += `</tr>`;
    
    return html;
}

// 총계 행 생성
function createTotalRow(label, data, positions, isMainTotal) {
    const bgClass = isMainTotal ? 'bg-gray-200 dark:bg-gray-900' : 'bg-blue-50 dark:bg-blue-900/20';
    let html = `<tr class="${bgClass}">`;
    html += `<td colspan="2" class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center font-bold">${label}</td>`;
    
    let rowTotal = 0;
    positions.forEach(pos => {
        const value = data[pos] || 0;
        html += `<td class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center font-bold">${value || '-'}</td>`;
        
        // '계' 컬럼이 아닌 경우에만 합계에 추가
        if (pos !== '계') {
            rowTotal += (typeof value === 'number' ? value : 0);
        }
    });
    
    // '계' 컬럼이 positions에 포함되어 있지 않은 경우에만 추가
    if (!positions.includes('계')) {
        const total = data['계'] || rowTotal || 0;
        html += `<td class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center font-bold bg-orange-200 dark:bg-orange-800">${total || '-'}</td>`;
    }
    
    html += `</tr>`;
    
    return html;
}

// 천진법인 전용 총계 행 생성
function createTotalRowForChina(label, data, positions, isMainTotal) {
    const bgClass = isMainTotal ? 'bg-gray-200 dark:bg-gray-900' : 'bg-blue-50 dark:bg-blue-900/20';
    let html = `<tr class="${bgClass}">`;
    html += `<td colspan="2" class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center font-bold">${label}</td>`;
    
    // 인원 컬럼
    const value = data['인원'] || 0;
    html += `<td class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center font-bold">${value || '-'}</td>`;
    
    // 계 컬럼
    const total = data['계'] || value || 0;
    html += `<td class="border border-gray-300 dark:border-gray-600 px-4 py-2 text-center font-bold bg-orange-200 dark:bg-orange-800">${total || '-'}</td>`;
    
    html += `</tr>`;
    
    return html;
}

// 기존 형식 테이블 생성 (호환성)
function createTableLegacy(corp) {
    // 기존 코드 유지...
    return `<div class="p-4">레거시 형식 데이터</div>`;
}