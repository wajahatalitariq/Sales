// Main App Component
function App() {
    const [items, setItems] = React.useState([]);
    const [sales, setSales] = React.useState([]);
    const [summary, setSummary] = React.useState({
        initial_investment: 0,
        total_sales: 0,
        remaining_investment: 0,
        percent_recouped: 0,
        sales_by_item: []
    });
    const [salesData, setSalesData] = React.useState({});
    const [activeCategory, setActiveCategory] = React.useState('all');
    const [isLoading, setIsLoading] = React.useState(true);
    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const [showSuccess, setShowSuccess] = React.useState(false);
    const [currentUser, setCurrentUser] = React.useState(null);
    const [pendingOrders, setPendingOrders] = React.useState([]);
    const [isPendingOrdersLoading, setIsPendingOrdersLoading] = React.useState(false);
    const [showPendingOrders, setShowPendingOrders] = React.useState(false);
    const [pendingOrdersCount, setPendingOrdersCount] = React.useState(0);

    // Fetch items, sales history and summary on component mount
    React.useEffect(() => {
        Promise.all([
            fetchItems(),
            fetchSales(),
            fetchSummary(),
            fetchCurrentUser(),
            fetchPendingOrders()
        ]).then(() => {
            setIsLoading(false);
        });

        // Set up interval to refresh pending orders
        const intervalId = setInterval(() => {
            fetchPendingOrders();
        }, 30000); // every 30 seconds

        // Clean up interval on unmount
        return () => clearInterval(intervalId);
    }, []);

    // Fetch current user information
    const fetchCurrentUser = async () => {
        try {
            const response = await fetch('/api/user');
            const data = await response.json();
            setCurrentUser(data);
            
            // Update the user profile in the navbar
            if (data && data.username) {
                renderUserProfile(data);
            }
            
            return data;
        } catch (error) {
            console.error('Error fetching user info:', error);
            return null;
        }
    };
    
    // Render user profile in the navbar
    const renderUserProfile = (user) => {
        const navbarElement = document.querySelector('.navbar');
        if (!navbarElement) return;
        
        // Check if profile already exists
        const existingProfile = document.querySelector('.user-profile');
        if (existingProfile) {
            existingProfile.remove();
        }
        
        // Create profile element
        const profileElement = document.createElement('div');
        profileElement.className = 'user-profile';
        
        // Create HTML content
        profileElement.innerHTML = `
            <div class="user-avatar">
                ${user.username ? user.username[0].toUpperCase() : "U"}
            </div>
            <div class="user-info">
                <span class="user-name">${user.username || "User"}</span>
                <a href="/logout" class="logout-link">Logout</a>
            </div>
        `;
        
        // Append to navbar
        navbarElement.appendChild(profileElement);
    };

    // Fetch items from API
    const fetchItems = async () => {
        try {
            const response = await fetch('/api/items');
            const data = await response.json();
            
            // Add deal items to the regular items
            const dealItems = [
                {
                    id: 'deal1',
                    name: 'Deal: Golgappay 8 + Margarita',
                    price: 299,
                    description: 'Special Deal: Golgappay (8 pieces) with Mint Margarita',
                    isDeal: true
                },
                {
                    id: 'deal2',
                    name: 'Deal: Chat in Bag + Margarita',
                    price: 399,
                    description: 'Special Deal: Chat in Bag with Mint Margarita',
                    isDeal: true
                },
                {
                    id: 'deal3',
                    name: 'Deal: Chat + Corn + Margarita',
                    price: 499,
                    description: 'Special Deal: Chat in Bag with Masala Masti Corn and Mint Margarita',
                    isDeal: true
                },
                {
                    id: 'deal4',
                    name: 'Deal: Golgappay 12 + Corn + Margarita',
                    price: 499,
                    description: 'Special Deal: Golgappay (12 pieces) with Masala Masti Corn and Mint Margarita',
                    isDeal: true,
                    recommended: true
                }
            ];
            
            const allItems = [...data, ...dealItems];
            setItems(allItems);
            
            // Initialize sales data state
            const initialSalesData = {};
            allItems.forEach(item => {
                initialSalesData[item.name] = {
                    quantity: 0,
                    amount: 0,
                    price: item.price,
                    options: []
                };
            });
            setSalesData(initialSalesData);
            return allItems;
        } catch (error) {
            console.error('Error fetching items:', error);
            return [];
        }
    };

    // Fetch sales history from API
    const fetchSales = async () => {
        try {
            const response = await fetch('/api/sales');
            const data = await response.json();
            setSales(data);
            return data;
        } catch (error) {
            console.error('Error fetching sales:', error);
            return [];
        }
    };

    // Fetch summary data from API
    const fetchSummary = async () => {
        try {
            const response = await fetch('/api/summary');
            const data = await response.json();
            setSummary(data);
            return data;
        } catch (error) {
            console.error('Error fetching summary:', error);
            return {};
        }
    };

    // Fetch pending orders
    const fetchPendingOrders = async () => {
        try {
            setIsPendingOrdersLoading(true);
            const response = await fetch('/api/pending-orders');
            if (response.ok) {
                const data = await response.json();
                setPendingOrders(data);
                setPendingOrdersCount(data.length);
            }
        } catch (error) {
            console.error('Error fetching pending orders:', error);
        } finally {
            setIsPendingOrdersLoading(false);
        }
    };

    // Handle order approval
    const handleApproveOrder = async (orderId) => {
        try {
            const response = await fetch(`/api/approve-order/${orderId}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                // Refresh data
                await Promise.all([
                    fetchPendingOrders(),
                    fetchSales(),
                    fetchSummary()
                ]);
                
                // Show success message
                setShowSuccess(true);
                setTimeout(() => {
                    setShowSuccess(false);
                }, 3000);
            } else {
                alert('Failed to approve order. Please try again.');
            }
        } catch (error) {
            console.error('Error approving order:', error);
            alert('Failed to approve order. Please try again.');
        }
    };

    // Handle order rejection
    const handleRejectOrder = async (orderId) => {
        try {
            const response = await fetch(`/api/reject-order/${orderId}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                // Refresh pending orders
                await fetchPendingOrders();
            } else {
                alert('Failed to reject order. Please try again.');
            }
        } catch (error) {
            console.error('Error rejecting order:', error);
            alert('Failed to reject order. Please try again.');
        }
    };

    // Handle quantity change
    const handleQuantityChange = (itemName, value) => {
        if (value < 0) return;
        
        setSalesData(prevData => {
            const itemPrice = prevData[itemName].price;
            const newAmount = value * itemPrice;
            
            return {
                ...prevData,
                [itemName]: {
                    ...prevData[itemName],
                    quantity: value,
                    amount: newAmount
                }
            };
        });
    };

    // Handle option toggle
    const handleOptionToggle = (itemName, option) => {
        setSalesData(prevData => {
            const currentOptions = prevData[itemName].options || [];
            const newOptions = currentOptions.includes(option) 
                ? currentOptions.filter(opt => opt !== option)
                : [...currentOptions, option];
            
            return {
                ...prevData,
                [itemName]: {
                    ...prevData[itemName],
                    options: newOptions
                }
            };
        });
    };

    // Submit sales data
    const handleSubmit = async () => {
        const salesToSubmit = [];
        
        // Prepare sales data for submission
        for (const [itemName, data] of Object.entries(salesData)) {
            if (data.quantity > 0) {
                salesToSubmit.push({
                    item: itemName,
                    quantity: data.quantity,
                    amount: data.amount,
                    options: data.options.join(', ')
                });
            }
        }
        
        if (salesToSubmit.length === 0) {
            alert('Please add at least one item to submit');
            return;
        }
        
        try {
            setIsSubmitting(true);
            
            const response = await fetch('/api/sales', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(salesToSubmit)
            });
            
            if (response.ok) {
                // Reset sales data
                const resetSalesData = {};
                items.forEach(item => {
                    resetSalesData[item.name] = {
                        quantity: 0,
                        amount: 0,
                        price: item.price,
                        options: []
                    };
                });
                setSalesData(resetSalesData);
                
                // Refresh sales history and summary
                await Promise.all([fetchSales(), fetchSummary()]);
                
                // Show success message
                setShowSuccess(true);
                setTimeout(() => {
                    setShowSuccess(false);
                }, 3000);
            } else {
                throw new Error('Failed to add sales');
            }
        } catch (error) {
            console.error('Error adding sales:', error);
            alert('Failed to add sales. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    // Get icon for each item
    const getItemIcon = (itemName) => {
        if (typeof itemName !== 'string') {
            return <span className="item-icon">🍽️</span>;
        }
        
        const name = itemName.toLowerCase();
        
        if (name.includes("golgappay")) return <span className="item-icon">🍵</span>;
        if (name.includes("chat")) return <span className="item-icon">🥡</span>;
        if (name.includes("corn")) return <span className="item-icon">🌽</span>;
        if (name.includes("margarita")) return <span className="item-icon">🥤</span>;
        if (name.includes("dahi")) return <span className="item-icon">🥛</span>;
        if (name.includes("samosa")) return <span className="item-icon">🥟</span>;
        
        return <span className="item-icon">🍽️</span>;
    };

    // Format date
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    // Format full date
    const formatFullDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString([], {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    // Get item category
    const getItemCategory = (itemName) => {
        if (itemName.includes('Golgappay')) return 'golgappay';
        if (itemName.includes('Margarita')) return 'drinks';
        if (itemName.includes('Chat in Bag')) return 'chat';
        if (itemName.includes('Corn') || itemName.includes('Topping')) return 'corn';
        
        // New condition for deal items
        if (itemName.startsWith('Deal:')) return 'deals';
        
        return 'other';
    };

    // Filter items by category
    const filterItems = (items) => {
        if (activeCategory === 'all') return items.filter(item => !item.isDeal);
        if (activeCategory === 'deals') return items.filter(item => item.isDeal);
        return items.filter(item => getItemCategory(item.name) === activeCategory && !item.isDeal);
    };

    // Check if Chat in Bag item
    const isChatInBag = (itemName) => {
        return itemName === 'Chat in Bag';
    };

    // Get Chat in Bag options
    const getChatOptions = () => {
        return ['Noodles', 'Onion', 'Tomato', 'Boiled Corn', 'Lemon', 'Chilli Garlic Sauce', 'Mayo Sauce', 'Corrian'];
    };

    // Calculate total items in cart
    const getTotalItemsInCart = () => {
        return Object.values(salesData).reduce((total, item) => total + item.quantity, 0);
    };

    // Calculate total amount in cart
    const getTotalAmountInCart = () => {
        return Object.values(salesData).reduce((total, item) => total + item.amount, 0);
    };

    // Toggle pending orders view
    const togglePendingOrders = () => {
        setShowPendingOrders(!showPendingOrders);
    };

    // Download QR code
    const downloadQRCode = () => {
        window.open('/qrcode', '_blank');
    };

    // Add a clearHistory function to clear sales history and reset summary data
    const clearHistory = async () => {
        if (!confirm('Are you sure you want to clear all sales history and reset the summary data? This action cannot be undone.')) {
            return;
        }
        
        try {
            setIsLoading(true);
            
            const response = await fetch('/api/clear-sales', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                // Refresh sales and summary data
                await Promise.all([fetchSales(), fetchSummary()]);
                
                // Show success message
                setShowSuccess(true);
                setTimeout(() => {
                    setShowSuccess(false);
                }, 3000);
            } else {
                throw new Error('Failed to clear sales history');
            }
        } catch (error) {
            console.error('Error clearing sales history:', error);
            alert('Failed to clear sales history. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Loading menu data...</p>
            </div>
        );
    }

    // Render the app
    return (
        <div className="dashboard-container">
            {showSuccess && (
                <div className="success-notification">
                    <span className="success-icon">✓</span>
                    Sales added successfully!
                </div>
            )}
            
            <div className="card sales-form">
                <div className="header-actions">
                    <h2>Record New Sales</h2>
                    <div>
                        <button 
                            className="action-btn qr-btn" 
                            onClick={downloadQRCode}
                            title="Download QR Code for customer orders"
                        >
                            📱 QR Code
                        </button>
                        <button 
                            className="action-btn pending-btn" 
                            onClick={togglePendingOrders}
                            title="View pending customer orders"
                        >
                            🔔 Pending Orders {pendingOrdersCount > 0 && <span className="badge">{pendingOrdersCount}</span>}
                        </button>
                    </div>
                </div>
                <p>Enter quantity for items sold in this transaction. Amount will be calculated automatically.</p>
                
                {showPendingOrders && (
                    <div className="pending-orders-container">
                        <h3>Pending Customer Orders</h3>
                        
                        {isPendingOrdersLoading ? (
                            <div className="loading-spinner-small"></div>
                        ) : pendingOrders.length === 0 ? (
                            <div className="empty-state">No pending orders available</div>
                        ) : (
                            <div className="pending-orders-list">
                                {pendingOrders.map(order => (
                                    <div className="pending-order-card" key={order.id}>
                                        <div className="pending-order-header">
                                            <div>
                                                <h4>Order from: {order.customerName}</h4>
                                                <p className="order-time">Placed: {formatFullDate(order.timestamp)}</p>
                                            </div>
                                            <div className="pending-order-total">Rs{order.totalAmount}</div>
                                        </div>
                                        
                                        <div className="pending-order-items">
                                            {order.items.map((item, idx) => (
                                                <div className="pending-order-item" key={idx}>
                                                    <span>{item.item} x{item.quantity}</span>
                                                    <span>Rs{item.amount}</span>
                                                </div>
                                            ))}
                                        </div>
                                        
                                        <div className="pending-order-actions">
                                            <button 
                                                className="approve-btn"
                                                onClick={() => handleApproveOrder(order.id)}
                                            >
                                                Approve
                                            </button>
                                            <button 
                                                className="reject-btn"
                                                onClick={() => handleRejectOrder(order.id)}
                                            >
                                                Reject
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
                
                <div className="category-tabs">
                    <button 
                        className={`tab-btn ${activeCategory === 'all' ? 'active' : ''}`}
                        onClick={() => setActiveCategory('all')}
                    >
                        All Items
                    </button>
                    <button 
                        className={`tab-btn ${activeCategory === 'golgappay' ? 'active' : ''}`}
                        onClick={() => setActiveCategory('golgappay')}
                    >
                        Golgappay
                    </button>
                    <button 
                        className={`tab-btn ${activeCategory === 'drinks' ? 'active' : ''}`}
                        onClick={() => setActiveCategory('drinks')}
                    >
                        Drinks
                    </button>
                    <button 
                        className={`tab-btn ${activeCategory === 'chat' ? 'active' : ''}`}
                        onClick={() => setActiveCategory('chat')}
                    >
                        Chat
                    </button>
                    <button 
                        className={`tab-btn ${activeCategory === 'corn' ? 'active' : ''}`}
                        onClick={() => setActiveCategory('corn')}
                    >
                        Corn
                    </button>
                    <button 
                        className={`tab-btn ${activeCategory === 'deals' ? 'active' : ''}`}
                        onClick={() => setActiveCategory('deals')}
                    >
                        Deal Menu
                    </button>
                </div>
                
                <div className="sales-items">
                    {filterItems(items).map(item => (
                        <div className={`item-card ${item.isDeal ? 'deal-item' : ''} ${item.recommended ? 'recommended-item' : ''}`} key={item.id}>
                            {item.isDeal && <div className="deal-badge">DEAL</div>}
                            {item.recommended && <div className="recommended-badge">RECOMMENDED</div>}
                            
                            <div className="card-header">
                                {getItemIcon(item.name)}
                                <h3>{item.name}</h3>
                            </div>
                            
                            <p>{item.description}</p>
                            
                            {item.isDeal && (
                                <div className="deal-items-icon">
                                    {item.name.includes('Golgappay 8') && <span className="deal-item-icon">🍵</span>}
                                    {item.name.includes('Golgappay 12') && <span className="deal-item-icon">🍵</span>}
                                    {item.name.includes('Chat') && <span className="deal-item-icon">🥡</span>}
                                    {item.name.includes('Corn') && <span className="deal-item-icon">🌽</span>}
                                    {item.name.includes('Margarita') && <span className="deal-item-icon">🥤</span>}
                                </div>
                            )}
                            
                            <div className="card-footer">
                                <div className="price-container">
                                    <span>Rs</span>
                                    <span className="item-price">{item.price}</span>
                                </div>
                                <div className="quantity-control">
                                    <label>Quantity</label>
                                    <div className="quantity-buttons">
                                        <button 
                                            onClick={() => handleQuantityChange(item.name, Math.max(0, salesData[item.name]?.quantity - 1 || 0))}
                                            disabled={!salesData[item.name]?.quantity || salesData[item.name]?.quantity <= 0}
                                        >
                                            -
                                        </button>
                                        <span>{salesData[item.name]?.quantity || 0}</span>
                                        <button 
                                            onClick={() => handleQuantityChange(item.name, (salesData[item.name]?.quantity || 0) + 1)}
                                        >
                                            +
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
                
                <div className="cart-summary">
                    <div className="cart-total">
                        <span>Total Items: <strong>{getTotalItemsInCart()}</strong></span>
                        <span>Total Amount: <strong>Rs{getTotalAmountInCart()}</strong></span>
                    </div>
                    <button 
                        className="submit-btn" 
                        onClick={handleSubmit}
                        disabled={isSubmitting || getTotalItemsInCart() === 0}
                    >
                        {isSubmitting ? 'Processing...' : 'Add All Sales'}
                    </button>
                </div>
            </div>
            
            <div className="card sales-summary">
                <div className="header-actions">
                    <h2>Sales Summary</h2>
                    <button 
                        className="action-btn clear-btn" 
                        onClick={clearHistory}
                        title="Clear all sales history and reset summary"
                    >
                        🗑️ Clear History
                    </button>
                </div>
                <p>Overview of your sales performance.</p>
                
                <div className="summary-card">
                    <div className="summary-item">
                        <span>Initial Investment:</span>
                        <strong>Rs{summary.initial_investment.toFixed(0)}</strong>
                    </div>
                    
                    <div className="summary-item">
                        <span>Total Sales:</span>
                        <strong style={{ color: '#e74c3c' }}>Rs{summary.total_sales.toFixed(0)}</strong>
                    </div>
                    
                    <div className="summary-item">
                        <span>Remaining Investment:</span>
                        <strong>Rs{summary.remaining_investment.toFixed(0)}</strong>
                    </div>
                </div>
                
                <div className="progress-container">
                    <p>Investment Recouped</p>
                    <div className="progress-bar">
                        <div 
                            className="progress-fill"
                            style={{ width: `${Math.min(100, summary.percent_recouped)}%` }}
                        ></div>
                    </div>
                    <div className="progress-value">{summary.percent_recouped.toFixed(1)}%</div>
                </div>
                
                <div className="summary-card">
                    <h3>Sales by Item:</h3>
                    {summary.sales_by_item.length > 0 ? (
                        summary.sales_by_item.map((item, index) => (
                            <div className="summary-item" key={index}>
                                <span>{item.name} ({item.qty})</span>
                                <strong>Rs{item.amount.toFixed(0)}</strong>
                            </div>
                        ))
                    ) : (
                        <div className="empty-state">No sales recorded yet</div>
                    )}
                </div>
            </div>
            
            <div className="card sales-history">
                <div className="header-actions">
                    <h2>Recent Sales History</h2>
                    <button 
                        className="action-btn clear-btn" 
                        onClick={clearHistory}
                        title="Clear all sales history and reset summary"
                    >
                        🗑️ Clear History
                    </button>
                </div>
                
                {sales.length > 0 ? (
                    <table className="sales-table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Customer</th>
                                <th>Item</th>
                                <th>Qty</th>
                                <th>Amount</th>
                                <th>Options</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sales.map(sale => (
                                <tr key={sale.id}>
                                    <td>{formatDate(sale.timestamp)}</td>
                                    <td>{sale.customerName || 'Walk-in'}</td>
                                    <td>{sale.name}</td>
                                    <td>{sale.quantity}</td>
                                    <td>Rs{sale.amount.toFixed(0)}</td>
                                    <td>{sale.options || '-'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <div className="empty-state">No sales history available yet</div>
                )}
            </div>
        </div>
    );
}

// Render the app
ReactDOM.render(<App />, document.getElementById('root')); 