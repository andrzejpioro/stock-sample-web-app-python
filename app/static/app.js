let allQuotes = [];

async function loadIndices() {
    try {
        const response = await fetch('/api/indices');
        const indices = await response.json();
        const select = document.getElementById('indexFilter');

        indices.forEach(index => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = index;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading indices:', error);
    }
}

async function loadDates() {
    try {
        const response = await fetch('/api/dates');
        const dates = await response.json();
        const input = document.getElementById('dateFilter');

        // Set max date to today and min to first available date
        if (dates.length > 0) {
            input.min = dates[0];
            input.max = dates[dates.length - 1];
        }
    } catch (error) {
        console.error('Error loading dates:', error);
    }
}

async function loadQuotes(indexName = '', date = '') {
    try {
        let url = '/api/quotes';
        const params = [];

        if (indexName) params.push('index_name=' + encodeURIComponent(indexName));
        if (date) params.push('date=' + encodeURIComponent(date));

        if (params.length > 0) {
            url += '?' + params.join('&');
        }

        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to load quotes');

        allQuotes = await response.json();
        displayQuotes(allQuotes);
        updateStats();
    } catch (error) {
        console.error('Error loading quotes:', error);
        document.getElementById('error').textContent = 'Error loading data: ' + error.message;
        document.getElementById('error').style.display = 'block';
    }
}

function displayQuotes(quotes) {
    const tbody = document.getElementById('quotesBody');

    if (quotes.length === 0) {
        tbody.innerHTML = '<tr class="no-data"><td colspan="5">No quotations found</td></tr>';
        return;
    }

    tbody.innerHTML = quotes.map(quote => `
        <tr>
            <td>${quote.date}</td>
            <td>${quote.time}</td>
            <td class="isin">${quote.isin}</td>
            <td class="price">${quote.price.toFixed(2)}</td>
            <td>${quote.index_name}</td>
        </tr>
    `).join('');
}

function updateStats() {
    const indexFilter = document.getElementById('indexFilter').value;
    const dateFilter = document.getElementById('dateFilter').value;

    let filtered = allQuotes;
    if (indexFilter) {
        filtered = filtered.filter(q => q.index_name === indexFilter);
    }
    if (dateFilter) {
        filtered = filtered.filter(q => q.date === dateFilter);
    }

    const uniqueIsins = new Set(filtered.map(q => q.isin)).size;
    const uniqueDates = new Set(filtered.map(q => q.date)).size;

    document.getElementById('quoteCount').textContent = filtered.length;
    document.getElementById('isinCount').textContent = uniqueIsins;
    document.getElementById('dateCount').textContent = uniqueDates;
}

// Event listeners
document.getElementById('indexFilter').addEventListener('change', () => {
    const indexName = document.getElementById('indexFilter').value;
    const date = document.getElementById('dateFilter').value;
    loadQuotes(indexName, date);
});

document.getElementById('dateFilter').addEventListener('change', () => {
    const indexName = document.getElementById('indexFilter').value;
    const date = document.getElementById('dateFilter').value;
    loadQuotes(indexName, date);
});

// Initial load
async function init() {
    await loadIndices();
    await loadDates();
    await loadQuotes();
}

init();
