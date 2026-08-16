"""Streamlit web dashboard for DukaanIQ."""

import html as html_lib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from src.web_backend import InventoryWebBackend

st.set_page_config(
    page_title="DukaanIQ - AI Inventory Agent",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional dark SaaS CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-base: #0b0f19;
        --bg-surface: #111827;
        --bg-surface-raised: #1f2937;
        --border-subtle: rgba(255, 255, 255, 0.06);
        --border-default: rgba(255, 255, 255, 0.1);
        --text-primary: #f9fafb;
        --text-secondary: #9ca3af;
        --text-tertiary: #6b7280;
        --accent: #6366f1;
        --accent-hover: #818cf8;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --info: #3b82f6;
    }

    * {font-family: 'Inter', sans-serif;}

    .stApp {
        background: var(--bg-base);
        color: var(--text-primary);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-surface) !important;
        border-right: 1px solid var(--border-subtle);
    }

    .sidebar-brand {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }

    .sidebar-subtitle {
        color: var(--text-tertiary);
        font-size: 0.8rem;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }

    .nav-section {
        color: var(--text-tertiary);
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 1.25rem 0 0.5rem 0;
    }

    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.6rem 0.75rem;
        border-radius: 0.5rem;
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.15rem;
        transition: all 0.15s ease;
        cursor: pointer;
        text-decoration: none;
    }

    .nav-item:hover {
        background: rgba(255, 255, 255, 0.04);
        color: var(--text-primary);
    }

    .nav-item.active {
        background: rgba(99, 102, 241, 0.12);
        color: var(--accent-hover);
        border: 1px solid rgba(99, 102, 241, 0.25);
    }

    .nav-icon {
        width: 1.25rem;
        height: 1.25rem;
        opacity: 0.8;
        flex-shrink: 0;
    }

    .sidebar-footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-subtle);
        color: var(--text-tertiary);
        font-size: 0.75rem;
        line-height: 1.6;
    }

    /* Main content */
    .page-header {
        margin-bottom: 2rem;
    }

    .page-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.02em;
    }

    .page-description {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-top: 0.35rem;
    }

    /* Stats */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .stat-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 0.75rem;
        padding: 1.25rem;
        transition: all 0.2s ease;
        animation: fadeInUp 0.5s ease-out;
    }

    .stat-card:hover {
        border-color: var(--border-default);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
    }

    .stat-label {
        color: var(--text-tertiary);
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .stat-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
    }

    /* Cards */
    .card {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .card-header {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }

    /* Notifications */
    .notification {
        padding: 0.875rem 1rem;
        border-radius: 0.5rem;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 1rem;
        animation: slideInRight 0.3s ease-out;
        border: 1px solid;
    }

    .notification-success {
        background: rgba(16, 185, 129, 0.08);
        border-color: rgba(16, 185, 129, 0.25);
        color: #6ee7b7;
    }

    .notification-error {
        background: rgba(239, 68, 68, 0.08);
        border-color: rgba(239, 68, 68, 0.25);
        color: #fca5a5;
    }

    .notification-info {
        background: rgba(59, 130, 246, 0.08);
        border-color: rgba(59, 130, 246, 0.25);
        color: #93c5fd;
    }

    .notification-warning {
        background: rgba(245, 158, 11, 0.08);
        border-color: rgba(245, 158, 11, 0.25);
        color: #fcd34d;
    }

    /* Confirmation */
    .confirm-panel {
        background: var(--bg-surface-raised);
        border: 1px solid var(--border-default);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: zoomIn 0.25s ease-out;
    }

    .confirm-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 0;
        border-bottom: 1px solid var(--border-subtle);
    }

    .confirm-row:last-child {
        border-bottom: none;
    }

    .confirm-label {
        color: var(--text-tertiary);
        font-size: 0.85rem;
        font-weight: 500;
    }

    .confirm-value {
        color: var(--text-primary);
        font-size: 0.95rem;
        font-weight: 600;
    }

    /* Tables */
    .data-table-wrapper {
        overflow-x: auto;
        border-radius: 0.75rem;
        border: 1px solid var(--border-subtle);
    }

    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }

    .data-table thead {
        background: var(--bg-surface-raised);
    }

    .data-table th {
        color: var(--text-tertiary);
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.875rem 1rem;
        text-align: left;
        border-bottom: 1px solid var(--border-default);
        white-space: nowrap;
    }

    .data-table td {
        padding: 0.875rem 1rem;
        border-bottom: 1px solid var(--border-subtle);
        color: var(--text-secondary);
        vertical-align: middle;
    }

    .data-table tbody tr {
        transition: background 0.15s ease;
    }

    .data-table tbody tr:hover {
        background: rgba(255, 255, 255, 0.02);
    }

    .data-table tbody tr:last-child td {
        border-bottom: none;
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        white-space: nowrap;
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.12);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }

    .badge-warning {
        background: rgba(245, 158, 11, 0.12);
        color: #fcd34d;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }

    .badge-error {
        background: rgba(239, 68, 68, 0.12);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.25);
    }

    .badge-neutral {
        background: rgba(107, 114, 128, 0.12);
        color: #d1d5db;
        border: 1px solid rgba(107, 114, 128, 0.25);
    }

    .badge-info {
        background: rgba(59, 130, 246, 0.12);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.25);
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: var(--text-tertiary);
    }

    .empty-state-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
    }

    .empty-state-desc {
        font-size: 0.9rem;
    }

    /* Activity */
    .activity-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        margin-bottom: 0.5rem;
        transition: all 0.15s ease;
        animation: fadeInUp 0.35s ease-out;
    }

    .activity-item:hover {
        border-color: var(--border-default);
        background: var(--bg-surface-raised);
    }

    .activity-dot {
        width: 0.5rem;
        height: 0.5rem;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .activity-dot-add { background: var(--success); }
    .activity-dot-remove { background: var(--error); }

    .activity-text {
        flex: 1;
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    .activity-time {
        color: var(--text-tertiary);
        font-size: 0.8rem;
        white-space: nowrap;
    }

    /* Inputs */
    .stTextInput>div>div>input {
        background: var(--bg-surface-raised) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: 0.5rem !important;
        color: var(--text-primary) !important;
        padding: 0.625rem 0.875rem !important;
        font-size: 0.95rem !important;
    }

    .stTextInput>div>div>input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }

    .stTextInput>div>div>input::placeholder {
        color: var(--text-tertiary) !important;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 0.5rem !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
        border: 1px solid var(--border-default) !important;
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* Animations */
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }

    @keyframes fadeInUp {
        from {opacity: 0; transform: translateY(12px);}
        to {opacity: 1; transform: translateY(0);}
    }

    @keyframes slideInRight {
        from {opacity: 0; transform: translateX(16px);}
        to {opacity: 1; transform: translateX(0);}
    }

    @keyframes zoomIn {
        from {opacity: 0; transform: scale(0.96);}
        to {opacity: 1; transform: scale(1);}
    }

    @keyframes gradientShift {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    .gradient-text {
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4, #6366f1);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 5s ease infinite;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: 1fr;
        }
        .page-title {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# NAVIGATION CONFIG
# Add new modules here. Each entry maps a page name to:
#   - id: URL-friendly page identifier
#   - label: display name in sidebar
#   - icon: simple text symbol (no emoji)
# ============================================================
NAVIGATION = [
    {"id": "dashboard", "label": "Dashboard", "icon": "Dashboard"},
    {"id": "inventory", "label": "Inventory", "icon": "Inventory"},
    {"id": "transactions", "label": "Transactions", "icon": "Transactions"},
    {"id": "sales", "label": "Sales", "icon": "Sales"},
    {"id": "khata", "label": "Khata", "icon": "Khata"},
    {"id": "suppliers", "label": "Suppliers", "icon": "Suppliers"},
    {"id": "expenses", "label": "Expenses", "icon": "Expenses"},
    {"id": "reports", "label": "Reports", "icon": "Reports"},
]

# Initialize backend in session state
if "backend" not in st.session_state:
    st.session_state.backend = InventoryWebBackend()

if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# Determine active page from query params or default
query_params = st.query_params
active_page = query_params.get("page", "dashboard")

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-brand">DukaanIQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">AI Inventory Agent</div>', unsafe_allow_html=True)

    st.markdown('<div class="nav-section">Menu</div>', unsafe_allow_html=True)
    for item in NAVIGATION:
        item_id = item["id"]
        label = item["label"]
        icon = item["icon"]
        active_class = "active" if active_page == item_id else ""
        if st.button(f"{icon}  {label}", key=f"nav_{item_id}", use_container_width=True):
            st.query_params["page"] = item_id
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="nav-section">System</div>', unsafe_allow_html=True)
    st.markdown("**Model:** qwen2.5:7b-instruct")
    st.markdown("**Database:** SQLite (local)")
    st.markdown("**Version:** 0.1.0")

# Helper: render notification
def render_notification(result):
    if not result:
        return
    css = "notification-success" if result.get("status") == "success" else "notification-error"
    st.markdown(f'<div class="notification {css}">{html_lib.escape(str(result.get("message", "")))}</div>', unsafe_allow_html=True)

# Helper: render empty state
def render_empty_state(title, description):
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-title">{html_lib.escape(title)}</div>
        <div class="empty-state-desc">{html_lib.escape(description)}</div>
    </div>
    """, unsafe_allow_html=True)

# Helper: escape dict values for safe HTML rendering
def esc(val):
    if val is None:
        return ""
    return html_lib.escape(str(val))

# ======================= DASHBOARD =======================
if active_page == "dashboard":
    st.markdown('<div class="page-header">', unsafe_allow_html=True)
    st.markdown('<div class="page-title gradient-text">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-description">Overview of your inventory and recent activity.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.session_state.backend as backend:
        inventory = backend.get_inventory()
        transactions = backend.get_transactions(limit=5)

        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Products</div>
                <div class="stat-value">{len(inventory)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            total_qty = sum(item["quantity"] for item in inventory)
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Stock Units</div>
                <div class="stat-value">{total_qty}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            low_stock = sum(1 for item in inventory if item["quantity"] <= item["minimum_stock_level"])
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Low Stock Alerts</div>
                <div class="stat-value">{low_stock}</div>
            </div>
            """, unsafe_allow_html=True)

        # AI Command
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">AI Command</div>', unsafe_allow_html=True)
        with st.form("ai_command_form", clear_on_submit=True):
            col_input, col_submit = st.columns([4, 1])
            with col_input:
                user_input = st.text_input(
                    "Enter a natural-language command:",
                    placeholder="e.g., I received 20 Coke, I sold 5 Pepsi, How many biscuits do I have?",
                    label_visibility="collapsed",
                )
            with col_submit:
                submitted = st.form_submit_button("Send", use_container_width=True)

        if submitted and user_input.strip():
            with st.spinner("Interpreting..."):
                result = backend.interpret(user_input.strip())
                st.session_state.last_result = result

                if result["status"] == "success":
                    validated = result["validated"]
                    action = validated["action"]
                    product = validated.get("product")
                    quantity = validated.get("quantity")

                    if action in ("ADD", "REMOVE"):
                        st.session_state.pending_action = validated
                        st.markdown(f'<div class="notification notification-info">Interpreted: {esc(action)} | product={esc(product)} | quantity={esc(quantity)}</div>', unsafe_allow_html=True)
                        st.warning("This action will modify inventory. Please confirm below.")
                    elif action == "UNKNOWN":
                        st.markdown('<div class="notification notification-warning">Request not understood. Please try again.</div>', unsafe_allow_html=True)
                    else:
                        exec_result = backend.confirm_and_execute(validated)
                        st.session_state.last_result = exec_result
                        render_notification(exec_result)
                else:
                    st.markdown(f'<div class="notification notification-error">Error: {esc(result.get("message", ""))}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Confirmation
        if st.session_state.pending_action is not None:
            validated = st.session_state.pending_action
            action = validated["action"]
            product = validated.get("product")
            quantity = validated.get("quantity")

            st.markdown('<div class="confirm-panel">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">Confirm Action</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="confirm-row">
                <div class="confirm-label">Action</div>
                <div class="confirm-value">{esc(action)}</div>
            </div>
            <div class="confirm-row">
                <div class="confirm-label">Product</div>
                <div class="confirm-value">{esc(product)}</div>
            </div>
            <div class="confirm-row">
                <div class="confirm-label">Quantity</div>
                <div class="confirm-value">{esc(quantity)}</div>
            </div>
            """, unsafe_allow_html=True)

            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("Confirm", use_container_width=True, type="primary"):
                    exec_result = backend.confirm_and_execute(validated)
                    st.session_state.last_result = exec_result
                    st.session_state.pending_action = None
                    render_notification(exec_result)
            with col_cancel:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.pending_action = None
                    st.info("Operation cancelled.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Recent Activity
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Recent Activity</div>', unsafe_allow_html=True)
        if transactions:
            for txn in transactions:
                txn_type = txn["type"]
                item_name = esc(txn.get("item_name", "Unknown"))
                qty = txn["quantity"]
                ts = esc(txn["timestamp"])
                dot_class = "activity-dot-add" if txn_type == "ADD" else "activity-dot-remove"
                st.markdown(f"""
                <div class="activity-item">
                    <div class="activity-dot {dot_class}"></div>
                    <div class="activity-text"><strong>{esc(txn_type)}</strong> {qty} x {item_name}</div>
                    <div class="activity-time">{ts}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            render_empty_state("No transactions yet", "Activity will appear here once you start managing inventory.")
        st.markdown('</div>', unsafe_allow_html=True)

# ======================= INVENTORY =======================
elif active_page == "inventory":
    st.markdown('<div class="page-header">', unsafe_allow_html=True)
    st.markdown('<div class="page-title gradient-text">Inventory</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-description">Manage your products and stock levels.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.session_state.backend as backend:
        inventory = backend.get_inventory()

        if not inventory:
            render_empty_state("Inventory is empty", "Add stock using the AI command on the Dashboard.")
        else:
            rows = []
            for item in inventory:
                qty = item["quantity"]
                min_stock = item["minimum_stock_level"]
                if qty == 0:
                    status = '<span class="badge badge-error">Out of Stock</span>'
                elif qty <= min_stock:
                    status = '<span class="badge badge-warning">Low Stock</span>'
                else:
                    status = '<span class="badge badge-success">In Stock</span>'

                rows.append(f"""
                <tr>
                    <td style="font-weight: 500;">{esc(item["name"])}</td>
                    <td>{esc(item["category"])}</td>
                    <td style="text-align: right; font-weight: 600;">{qty}</td>
                    <td>{esc(item["unit"])}</td>
                    <td style="text-align: right;">${item['price']:.2f}</td>
                    <td style="text-align: right;">{min_stock}</td>
                    <td>{status}</td>
                </tr>
                """)

            html = f"""
            <div class="data-table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Category</th>
                            <th style="text-align: right;">Qty</th>
                            <th>Unit</th>
                            <th style="text-align: right;">Price</th>
                            <th style="text-align: right;">Min Stock</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(rows)}
                    </tbody>
                </table>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

# ======================= TRANSACTIONS =======================
elif active_page == "transactions":
    st.markdown('<div class="page-header">', unsafe_allow_html=True)
    st.markdown('<div class="page-title gradient-text">Transactions</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-description">Audit log of all inventory movements.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.session_state.backend as backend:
        transactions = backend.get_transactions(limit=50)

        if not transactions:
            render_empty_state("No transactions recorded yet", "Transactions will appear here once stock changes are made.")
        else:
            rows = []
            for txn in transactions:
                txn_type = txn["type"]
                badge_class = "badge-success" if txn_type == "ADD" else "badge-error"
                rows.append(f"""
                <tr>
                    <td>{esc(txn["timestamp"])}</td>
                    <td><span class="badge {badge_class}">{esc(txn_type)}</span></td>
                    <td style="font-weight: 500;">{esc(txn.get("item_name", "Unknown"))}</td>
                    <td style="text-align: right; font-weight: 600;">{txn["quantity"]}</td>
                    <td>{esc(txn.get("note", ""))}</td>
                </tr>
                """)

            html = f"""
            <div class="data-table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Type</th>
                            <th>Item</th>
                            <th style="text-align: right;">Quantity</th>
                            <th>Note</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(rows)}
                    </tbody>
                </table>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

# ======================= PLACEHOLDER PAGES =======================
else:
    page_label = next((item["label"] for item in NAVIGATION if item["id"] == active_page), active_page)
    st.markdown('<div class="page-header">', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title gradient-text">{esc(page_label)}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    render_empty_state("Coming soon", "This module is planned for a future release.")
