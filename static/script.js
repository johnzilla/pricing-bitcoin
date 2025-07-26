// Global state
let currentDirection = 'btc_to_item'; // 'btc_to_item' or 'item_to_btc'
let currentUnit = 'btc'; // 'btc' or 'sats'
let debounceTimer = null;
let currentItem = '';
let itemsData = {};

// DOM elements
let btcInput = document.getElementById('btc-input');
let itemSelect = document.getElementById('item-select');
let btcToggle = document.getElementById('btc-toggle');
let satsToggle = document.getElementById('sats-toggle');
const swapBtn = document.getElementById('swap-direction');
const refreshBtn = document.getElementById('refresh-btn');
const quantityValue = document.getElementById('quantity-value');
const quantityUnit = document.getElementById('quantity-unit');
const itemPrice = document.getElementById('item-price');
const totalValue = document.getElementById('total-value');
const btcPrice = document.getElementById('btc-price');
const loadingSpinner = document.getElementById('loading-spinner');
const historicalSection = document.getElementById('historical-section');
const fromDate = document.getElementById('from-date');
const toDate = document.getElementById('to-date');
const loadHistoricalBtn = document.getElementById('load-historical');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    setDefaultDates();
    updateUIForDirection();
    // Ensure items are loaded after a brief delay to let the DOM settle
    setTimeout(() => {
        console.log('Loading items after DOM setup...');
        loadItems();
    }, 200);
});

function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Input change with debouncing
    if (btcInput) {
        btcInput.addEventListener('input', debounceConvert);
    }
    if (itemSelect) {
        itemSelect.addEventListener('change', handleItemChange);
    }
    
    // Unit toggles
    if (btcToggle) {
        btcToggle.addEventListener('click', () => setUnit('btc'));
    }
    if (satsToggle) {
        satsToggle.addEventListener('click', () => setUnit('sats'));
    }
    
    // Direction swap
    if (swapBtn) {
        swapBtn.addEventListener('click', swapDirection);
    }
    
    // Refresh button
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            if (currentItem) {
                performConversion();
            }
        });
    }
    
    // Historical data
    if (loadHistoricalBtn) {
        loadHistoricalBtn.addEventListener('click', loadHistoricalData);
    }
}

function debounceConvert() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        if (currentItem && btcInput.value) {
            performConversion();
        }
    }, 300);
}

function setUnit(unit) {
    currentUnit = unit;
    btcToggle.classList.toggle('active', unit === 'btc');
    satsToggle.classList.toggle('active', unit === 'sats');
    
    // Update placeholder and convert existing value
    if (unit === 'btc') {
        btcInput.placeholder = '0.1';
        btcInput.step = 'any';
        if (btcInput.value && currentUnit !== 'btc') {
            btcInput.value = (parseFloat(btcInput.value) / 100000000).toString();
        }
    } else {
        btcInput.placeholder = '10000000';
        btcInput.step = '1';
        if (btcInput.value && currentUnit !== 'sats') {
            btcInput.value = Math.round(parseFloat(btcInput.value) * 100000000).toString();
        }
    }
    
    debounceConvert();
}

function swapDirection() {
    currentDirection = currentDirection === 'btc_to_item' ? 'item_to_btc' : 'btc_to_item';
    updateUIForDirection();
    debounceConvert();
}

function updateUIForDirection() {
    const inputSide = document.querySelector('.input-side');
    const outputSide = document.querySelector('.output-side');
    
    if (currentDirection === 'btc_to_item') {
        // BTC input, item output
        inputSide.innerHTML = `
            <div class="input-group">
                <label for="btc-input">Bitcoin Amount</label>
                <div class="input-wrapper">
                    <input type="number" id="btc-input" placeholder="${currentUnit === 'btc' ? '0.1' : '10000000'}" step="${currentUnit === 'btc' ? 'any' : '1'}" min="0">
                    <div class="unit-toggle">
                        <button id="btc-toggle" class="unit-btn ${currentUnit === 'btc' ? 'active' : ''}" data-unit="btc">BTC</button>
                        <button id="sats-toggle" class="unit-btn ${currentUnit === 'sats' ? 'active' : ''}" data-unit="sats">sats</button>
                    </div>
                </div>
            </div>
        `;
        
        outputSide.innerHTML = `
            <div class="input-group">
                <label for="item-select">Item</label>
                <select id="item-select">
                    <option value="">Select an item...</option>
                </select>
            </div>
            <div class="result-container">
                <div id="result-display" class="result-display">
                    <div class="quantity-result">
                        <span id="quantity-value">--</span>
                        <span id="quantity-unit"></span>
                    </div>
                    <div class="price-breakdown">
                        <div class="price-row">
                            <span>Item Price:</span>
                            <span id="item-price">$--</span>
                        </div>
                        <div class="price-row">
                            <span>Total Value:</span>
                            <span id="total-value">$--</span>
                        </div>
                        <div class="price-row">
                            <span>BTC Price:</span>
                            <span id="btc-price">$--</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Item input, BTC output
        inputSide.innerHTML = `
            <div class="input-group">
                <label for="item-select">Item</label>
                <select id="item-select">
                    <option value="">Select an item...</option>
                </select>
            </div>
            <div class="input-group">
                <label for="quantity-input">Quantity</label>
                <input type="number" id="quantity-input" placeholder="1" step="any" min="0">
            </div>
        `;
        
        outputSide.innerHTML = `
            <div class="input-group">
                <label>Bitcoin Needed</label>
                <div class="unit-toggle">
                    <button id="btc-toggle" class="unit-btn ${currentUnit === 'btc' ? 'active' : ''}" data-unit="btc">BTC</button>
                    <button id="sats-toggle" class="unit-btn ${currentUnit === 'sats' ? 'active' : ''}" data-unit="sats">sats</button>
                </div>
            </div>
            <div class="result-container">
                <div id="result-display" class="result-display">
                    <div class="quantity-result">
                        <span id="quantity-value">--</span>
                        <span id="quantity-unit">${currentUnit}</span>
                    </div>
                    <div class="price-breakdown">
                        <div class="price-row">
                            <span>Item Price:</span>
                            <span id="item-price">$--</span>
                        </div>
                        <div class="price-row">
                            <span>Total Value:</span>
                            <span id="total-value">$--</span>
                        </div>
                        <div class="price-row">
                            <span>BTC Price:</span>
                            <span id="btc-price">$--</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Re-setup event listeners for new elements
    setupEventListenersAfterDirectionChange();
}

function setupEventListenersAfterDirectionChange() {
    // Re-get DOM elements
    const newBtcInput = document.getElementById('btc-input');
    const newQuantityInput = document.getElementById('quantity-input');
    const newItemSelect = document.getElementById('item-select');
    const newBtcToggle = document.getElementById('btc-toggle');
    const newSatsToggle = document.getElementById('sats-toggle');
    
    // Setup listeners based on direction
    if (currentDirection === 'btc_to_item' && newBtcInput) {
        newBtcInput.addEventListener('input', debounceConvert);
    } else if (currentDirection === 'item_to_btc' && newQuantityInput) {
        newQuantityInput.addEventListener('input', debounceConvert);
    }
    
    if (newItemSelect) {
        newItemSelect.addEventListener('change', handleItemChange);
    }
    
    if (newBtcToggle) {
        newBtcToggle.addEventListener('click', () => setUnit('btc'));
    }
    
    if (newSatsToggle) {
        newSatsToggle.addEventListener('click', () => setUnit('sats'));
    }
    
    // Update global references
    btcInput = newBtcInput;
    itemSelect = newItemSelect;
    btcToggle = newBtcToggle;
    satsToggle = newSatsToggle;
}

async function loadItems() {
    try {
        // Fetch items from the API
        const response = await fetch('/api/items');
        if (!response.ok) {
            throw new Error('Failed to fetch items');
        }
        const categories = await response.json();
        
        const select = document.getElementById('item-select');
        if (!select) {
            console.error('Could not find item-select element');
            return;
        }
        select.innerHTML = '<option value="">Select an item...</option>';
        
        Object.entries(categories).forEach(([category, items]) => {
            const optgroup = document.createElement('optgroup');
            optgroup.label = category;
            
            items.forEach(item => {
                const option = document.createElement('option');
                option.value = item.key;
                option.textContent = item.name;
                option.dataset.historicalSupport = item.historical_support;
                option.dataset.unit = item.unit;
                optgroup.appendChild(option);
            });
            
            select.appendChild(optgroup);
        });
        
        itemsData = categories;
        console.log('Items loaded successfully:', Object.keys(categories).length, 'categories');
        
    } catch (error) {
        console.error('Error loading items:', error);
        showToast('Failed to load items: ' + error.message, 'error');
    }
}

function handleItemChange() {
    const select = document.getElementById('item-select');
    currentItem = select.value;
    
    if (currentItem) {
        const option = select.querySelector(`option[value="${currentItem}"]`);
        const hasHistoricalSupport = option?.dataset.historicalSupport === 'true';
        
        // Show/hide historical section
        if (hasHistoricalSupport) {
            historicalSection.style.display = 'block';
        } else {
            historicalSection.style.display = 'none';
        }
        
        // Update quantity unit
        const unitSpan = document.getElementById('quantity-unit');
        if (unitSpan && currentDirection === 'btc_to_item') {
            const unit = option?.dataset.unit;
            if (unit) {
                unitSpan.textContent = unit;
            }
        }
        
        debounceConvert();
    } else {
        historicalSection.style.display = 'none';
        clearResults();
    }
}

async function performConversion() {
    const inputElement = currentDirection === 'btc_to_item' 
        ? document.getElementById('btc-input')
        : document.getElementById('quantity-input');
    
    if (!inputElement || !inputElement.value || !currentItem) {
        return;
    }
    
    const inputValue = parseFloat(inputElement.value);
    if (inputValue <= 0) {
        showToast('Please enter a positive value', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const params = new URLSearchParams({
            item: currentItem,
            direction: currentDirection,
            sats: currentUnit === 'sats' ? 'true' : 'false'
        });
        
        if (currentDirection === 'btc_to_item') {
            params.append('btc_amount', inputValue);
        } else {
            params.append('quantity', inputValue);
        }
        
        const response = await fetch(`/api/convert?${params}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Conversion failed');
        }
        
        const data = await response.json();
        updateResults(data);
        
    } catch (error) {
        showToast(error.message, 'error');
        clearResults();
    } finally {
        showLoading(false);
    }
}

function updateResults(data) {
    document.getElementById('quantity-value').textContent = data.quantity.toLocaleString();
    document.getElementById('item-price').textContent = `$${data.usd_item.toLocaleString()}`;
    document.getElementById('total-value').textContent = `$${data.usd_total.toLocaleString()}`;
    document.getElementById('btc-price').textContent = `$${data.btc_price.toLocaleString()}`;
}

function clearResults() {
    document.getElementById('quantity-value').textContent = '--';
    document.getElementById('item-price').textContent = '$--';
    document.getElementById('total-value').textContent = '$--';
    document.getElementById('btc-price').textContent = '$--';
}

async function loadHistoricalData() {
    if (!currentItem) {
        showToast('Please select an item first', 'error');
        return;
    }
    
    const fromDateValue = fromDate.value;
    const toDateValue = toDate.value;
    
    if (!fromDateValue || !toDateValue) {
        showToast('Please select both from and to dates', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const params = new URLSearchParams({
            item: currentItem,
            from_date: fromDateValue,
            to_date: toDateValue
        });
        
        const response = await fetch(`/api/historical?${params}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to load historical data');
        }
        
        const data = await response.json();
        renderChart(data);
        
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function renderChart(data) {
    const dataPoints = data.dates.map((date, index) => ({
        x: new Date(date),
        y: data.btc_prices[index]
    }));
    
    const chart = new CanvasJS.Chart("chartContainer", {
        animationEnabled: true,
        theme: "light2",
        title: {
            text: `${currentItem.replace('_', ' ').toUpperCase()} Price in BTC`
        },
        axisX: {
            valueFormatString: "MMM YYYY",
            crosshair: {
                enabled: true,
                snapToDataPoint: true
            }
        },
        axisY: {
            title: "BTC",
            includeZero: false,
            prefix: "₿",
            crosshair: {
                enabled: true
            }
        },
        toolTip: {
            shared: true
        },
        data: [{
            type: "spline",
            name: "Price in BTC",
            showInLegend: true,
            dataPoints: dataPoints
        }]
    });
    
    chart.render();
}

function setDefaultDates() {
    const today = new Date();
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(today.getFullYear() - 1);
    
    toDate.value = today.toISOString().split('T')[0];
    fromDate.value = oneYearAgo.toISOString().split('T')[0];
}

function showLoading(show) {
    loadingSpinner.style.display = show ? 'flex' : 'none';
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    document.getElementById('toast-container').appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 4000);
}

// Error handling for unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    showToast('An unexpected error occurred', 'error');
    console.error('Unhandled promise rejection:', event.reason);
}); 