/**
 * truth_table.js
 * EC2201 Digital Logic Design - 32-Row Interactive Truth Table Manager
 * Supports category filtering, search, minterm navigation, and active row highlighting.
 */

let truthTableData = [];
let currentHighlightedIndex = -1;

document.addEventListener('DOMContentLoaded', () => {
    initTruthTable();
});

async function initTruthTable() {
    const tableBody = document.getElementById('truthTableBody');
    if (!tableBody) return;

    try {
        const response = await fetch('/api/truth-table');
        if (!response.ok) throw new Error('Failed to fetch truth table');
        
        truthTableData = await response.json();
        renderTruthTable(truthTableData);
        setupTruthTableControls();
    } catch (err) {
        console.error('Error loading truth table:', err);
    }
}

function renderTruthTable(rows) {
    const tableBody = document.getElementById('truthTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = '';
    
    rows.forEach(r => {
        const tr = document.createElement('tr');
        tr.id = `tt-row-${r.index}`;
        if (r.index === currentHighlightedIndex) {
            tr.classList.add('active-minterm-row');
        }

        let badgeClass = 'badge-strength-weak';
        if (r.category === 'Medium') badgeClass = 'badge-strength-medium';
        else if (r.category === 'Strong') badgeClass = 'badge-strength-strong';
        else if (r.category === 'Very Strong') badgeClass = 'badge-strength-very-strong';

        tr.innerHTML = `
            <td><span class="badge bg-dark border border-secondary">${r.minterm}</span></td>
            <td><code>${r.index}</code></td>
            <td class="${r.A ? 'text-info fw-bold' : 'text-muted'}">${r.A}</td>
            <td class="${r.B ? 'text-info fw-bold' : 'text-muted'}">${r.B}</td>
            <td class="${r.C ? 'text-info fw-bold' : 'text-muted'}">${r.C}</td>
            <td class="${r.D ? 'text-info fw-bold' : 'text-muted'}">${r.D}</td>
            <td class="${r.E ? 'text-info fw-bold' : 'text-muted'}">${r.E}</td>
            <td><span class="badge bg-dark border border-cyan text-info">${r.S2} ${r.S1} ${r.S0}</span></td>
            <td class="fw-bold">${r.score}</td>
            <td><span class="${badgeClass}">${r.category}</span></td>
        `;

        tableBody.appendChild(tr);
    });

    const countElem = document.getElementById('truthTableRowCount');
    if (countElem) countElem.textContent = `${rows.length} States`;
}

function setupTruthTableControls() {
    const filterSelect = document.getElementById('ttCategoryFilter');
    const searchInput = document.getElementById('ttSearchInput');

    if (filterSelect) {
        filterSelect.addEventListener('change', applyFilters);
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyFilters);
    }
}

function applyFilters() {
    const category = document.getElementById('ttCategoryFilter')?.value || 'ALL';
    const query = document.getElementById('ttSearchInput')?.value.toLowerCase().trim() || '';

    let filtered = truthTableData.filter(r => {
        const matchesCategory = (category === 'ALL') || (r.category === category);
        const binaryStr = `${r.A}${r.B}${r.C}${r.D}${r.E}`;
        const matchesQuery = !query || 
            r.minterm.toLowerCase().includes(query) || 
            String(r.index).includes(query) ||
            binaryStr.includes(query) ||
            r.category.toLowerCase().includes(query);
        return matchesCategory && matchesQuery;
    });

    renderTruthTable(filtered);
}

/**
 * Highlights the row corresponding to the active evaluated password's minterm
 */
function highlightTruthTableRow(mintermIndex) {
    currentHighlightedIndex = mintermIndex;
    
    // Remove previous highlights
    document.querySelectorAll('.table-cyber tr.active-minterm-row').forEach(tr => {
        tr.classList.remove('active-minterm-row');
    });

    const targetRow = document.getElementById(`tt-row-${mintermIndex}`);
    if (targetRow) {
        targetRow.classList.add('active-minterm-row');
        // Scroll into view if table container exists
        targetRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}
