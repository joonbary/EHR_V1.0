// Debug script to test the view toggle functionality
console.log('=== Starting View Toggle Debug ===');

// Check if elements exist
const viewToggle = document.getElementById('viewToggle');
const employeeGrid = document.getElementById('employeeGrid');
const employeeTable = document.getElementById('employeeTable');

console.log('viewToggle element:', viewToggle);
console.log('employeeGrid element:', employeeGrid);
console.log('employeeTable element:', employeeTable);

if (viewToggle) {
    const icon = viewToggle.querySelector('i');
    console.log('Icon element:', icon);
    if (icon) {
        console.log('Icon data-lucide attribute:', icon.getAttribute('data-lucide'));
    }
}

if (employeeGrid && employeeTable) {
    console.log('Grid is hidden:', employeeGrid.classList.contains('hidden'));
    console.log('Table is hidden:', employeeTable.classList.contains('hidden'));
}

// Check if variables exist
console.log('isGridView variable:', typeof isGridView !== 'undefined' ? isGridView : 'undefined');
console.log('currentEmployees variable:', typeof currentEmployees !== 'undefined' ? currentEmployees : 'undefined');

// Check if functions exist
console.log('toggleView function:', typeof toggleView !== 'undefined' ? 'defined' : 'undefined');

// Test the toggle function directly
if (typeof toggleView !== 'undefined') {
    console.log('=== Testing toggleView function ===');
    toggleView();
    
    // Check state after toggle
    if (employeeGrid && employeeTable) {
        console.log('After toggle - Grid is hidden:', employeeGrid.classList.contains('hidden'));
        console.log('After toggle - Table is hidden:', employeeTable.classList.contains('hidden'));
    }
} else {
    console.log('toggleView function not found');
}

console.log('=== Debug Complete ===');