const API_URL = 'http://127.0.0.1:8000';

// --- DOM Elements ---
const listContainer = document.getElementById('contactList');
const searchInput = document.getElementById('searchInput');
const modal = document.getElementById('contactModal');
const form = document.getElementById('contactForm');
const modalTitle = document.getElementById('modalTitle');
const statusPill = document.getElementById('connectionStatus');

// --- State ---
let isEditing = false;
let currentId = null;
let debounceTimer = null; // Stores the timer ID

// --- Initialization ---
document.addEventListener('DOMContentLoaded', fetchContacts);

// --- Helpers ---
function formatPhoneNumber(phoneStr) {
    const cleaned = ('' + phoneStr).replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
        return '(' + match[1] + ') ' + match[2] + '-' + match[3];
    }
    return phoneStr;
}

function updateStatus(isOnline) {
    if(isOnline) {
        statusPill.innerHTML = '<span class="dot" style="background:#81B29A"></span> Online';
    } else {
        statusPill.innerHTML = '<span class="dot" style="background:#E07A5F"></span> Offline';
    }
}

// --- API Functions ---

// 1. Fetch All (Initial Load)
async function fetchContacts() {
    try {
        const res = await fetch(`${API_URL}/contacts`);
        if (!res.ok) throw new Error("Failed");
        const contacts = await res.json();
        renderList(contacts);
        updateStatus(true);
    } catch (err) {
        updateStatus(false);
        renderError("Unable to reach your journal.");
    }
}

// 2. Server-Side Search (Executed after delay)
async function performSearch(query) {
    // If input is empty, just load all contacts
    if (!query) return fetchContacts();

    try {
        // Smart Logic: If query has numbers, search phone. Else search name.
        const isPhone = /\d/.test(query);
        const param = isPhone ? 'phone' : 'name';

        const res = await fetch(`${API_URL}/contacts/search?${param}=${encodeURIComponent(query)}`);

        if (!res.ok) throw new Error("Search failed");

        const contacts = await res.json();
        renderList(contacts);

    } catch (err) {
        console.error(err);
        // Optional: show user an error state
        // renderError("Search failed.");
    }
}

// 3. Save (Create/Update)
async function saveContact(e) {
    e.preventDefault();

    const nameVal = document.getElementById('nameInput').value;
    const phoneVal = document.getElementById('phoneInput').value;
    const emailVal = document.getElementById('emailInput').value || "";

    const payload = {
        name: nameVal,
        phone: phoneVal,
        email: emailVal
    };

    try {
        const url = isEditing ? `${API_URL}/contacts/${currentId}` : `${API_URL}/contacts`;
        const method = isEditing ? 'PUT' : 'POST';

        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            alert(err.detail || "Could not save entry.");
            return;
        }

        closeModal();
        fetchContacts();
    } catch (err) {
        alert("Network Error");
    }
}

// 4. Delete
async function deleteContact(id) {
    if(!confirm("Remove this entry permanently?")) return;
    try {
        await fetch(`${API_URL}/contacts/${id}`, { method: 'DELETE' });
        fetchContacts();
    } catch (err) { alert("Error deleting"); }
}

// --- UI Logic ---

function renderList(contacts) {
    listContainer.innerHTML = '';

    if (contacts.length === 0) {
        listContainer.innerHTML = `
            <div style="text-align:center; color:#9C8E85; margin-top:50px;">
                <p>No matches found.</p>
            </div>`;
        return;
    }

    contacts.forEach(contact => {
        const displayPhone = formatPhoneNumber(contact.phone);

        const card = document.createElement('div');
        card.className = 'contact-card';
        card.innerHTML = `
            <div class="info">
                <h3>${contact.name}</h3>
                <p>${displayPhone}</p>
                ${contact.email ? `<p style="font-size:0.8rem; opacity:0.7;">${contact.email}</p>` : ''}
            </div>
            <div class="actions">
                <button class="icon-btn" onclick="openEdit(${contact.id}, '${contact.name}', '${contact.phone}', '${contact.email || ''}')">✎</button>
                <button class="icon-btn delete-btn" onclick="deleteContact(${contact.id})">✕</button>
            </div>
        `;
        listContainer.appendChild(card);
    });
}

function renderError(msg) {
    listContainer.innerHTML = `
        <div style="text-align:center; color:#9C8E85; margin-top:50px;">
            <p>${msg}</p>
        </div>
    `;
}

// --- THE DEBOUNCE LOGIC (UPDATED) ---
searchInput.addEventListener('input', (e) => {
    const query = e.target.value;

    // 1. Clear the old timer if user types again quickly
    clearTimeout(debounceTimer);

    // 2. Start a new timer for 1200ms (1.2 second)
    debounceTimer = setTimeout(() => {
        performSearch(query);
    }, 1200);
});

// Modal Handling
window.openModal = () => {
    isEditing = false;
    currentId = null;
    form.reset();
    modalTitle.innerText = "New Entry";
    modal.classList.add('active');
};

window.openEdit = (id, name, phone, email) => {
    isEditing = true;
    currentId = id;
    document.getElementById('nameInput').value = name;
    document.getElementById('phoneInput').value = phone;
    document.getElementById('emailInput').value = email;
    modalTitle.innerText = "Edit Entry";
    modal.classList.add('active');
};

window.closeModal = () => {
    modal.classList.remove('active');
};

form.addEventListener('submit', saveContact);
modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
});