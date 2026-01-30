// Получаем токен
const token = localStorage.getItem('access_token');

if (!token) {
    // Если нет токена, перенаправляем на страницу входа
    alert('Please login first');
    window.location.href = '/auth/login-page';
    throw new Error('No token found');
}

console.log('Token found, initializing board...');

async function loadTasks() {
    try {
        const res = await fetch("/tasks/board", {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        });

        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const tasks = await res.json();
        console.log(`Loaded ${tasks.length} tasks`);

        const map = {
            A: "q1",
            B: "q2",
            C: "q3",
            D: "q4"
        };

        // Очищаем колонки перед добавлением
        Object.values(map).forEach(id => {
            const ul = document.getElementById(id);
            if (ul) ul.innerHTML = '';
        });

        // Добавляем задачи
        tasks.forEach(t => {
            const ul = document.getElementById(map[t.importance_level]);
            if (!ul) return;

            // СОЗДАЕМ ЭЛЕМЕНТ С КЛАССОМ task-item
            const li = document.createElement("li");
            li.className = "task-item";
            li.onclick = (event) => openTask(t.id, event); // Передаем event

            li.innerHTML = `
                <div class="task-title">${t.title || 'No title'}</div>
                <div class="task-meta-small">
                    <span>👤 ${t.user?.name || t.name || 'Unknown'}</span>
                    <span>🗓️ ${formatDate(t.created_at)}</span>
                </div>
            `;

            ul.appendChild(li);
        });

    } catch (error) {
        console.error("Error loading tasks:", error);
    }
}

function refreshBoardData() {
    console.log("Refreshing board...");
    loadTasks();
}

function showNotification(message) {
    console.log("Notification:", message);
}

/* ---------- WebSocket ---------- */
let socket;
try {
    socket = new WebSocket(`ws://${location.host}/ws?token=${token}`);

    socket.onopen = () => {
        console.log('WebSocket connected');
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('WebSocket event:', data);

        if (data.event === 'task_created') {
            console.log('Detected task change, refreshing...');
            refreshBoardData();
            showNotification(`The task "${data.title}" has been created`);
        }

        if (data.event === 'task_updated') {
            console.log('Update detected!');
            refreshBoardData();
            showNotification(`The task "${data.title}" has been updated`);
        }

        if (data.event == 'task_completed') {
            console.log('Update detected!');
            showNotification(`The task "${data.title}" has been completed`);
            refreshBoardData();
        }

        if (data.event === 'task_deleted') {
            console.log('Update detected!');
            showNotification(`The task "${data.title}" has been deleted`);
            refreshBoardData();
        }




        if (data.event === 'user_joined' || data.event === 'user_left') {
            const actionText = data.event === 'user_joined' ? 'joined' : 'left';
            showNotification(`User ${data.email} ${actionText}`);
            // При желании можно тоже обновлять доску, чтобы видеть актуальных авторов
        }
    };

    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (error.message.includes('401') || error.message.includes('403')) {
            alert('Authentication failed. Please login again.');
            logout();
        }
    };

    socket.onclose = (event) => {
        console.log(`Code: ${event.code}, Reason: ${event.reason}`);
    };
} catch (error) {
    console.error('Failed to create WebSocket:', error);
}

/* ---------- Открытие задачи ---------- */
async function openTask(id) {
    try {
        const res = await fetch(`/tasks/board/${id}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        });

        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const task = await res.json();
        console.log('Task details:', task);

        // Заполняем модальное окно
        document.getElementById("modal-title").textContent = task.title;
        document.getElementById("modal-content").textContent = task.content;
        document.getElementById("modal-author").textContent = task.user ?.name || task.name || 'Unknown';
        document.getElementById("modal-position").textContent = task.user ?.position || task.position || 'Unknown';
        document.getElementById("modal-date").textContent = formatDate(task.created_at);
        document.getElementById("modal-deadline").textContent = formatDate(task.deadline_date);

        // Обработка ремарки
        const remarkSection = document.getElementById("remark-section");
        if (task.remark && task.remark.trim() !== '') {
            document.getElementById("modal-remark").textContent = task.remark;
            remarkSection.style.display = 'block';
        } else {
            remarkSection.style.display = 'none';
        }

        // Отображаем важность
        const importanceBadge = document.getElementById("modal-importance");
        const importanceMap = {
            'A': {
                text: 'Наивысший приоритет',
                color: '#e0564a'
            },
            'B': {
                text: 'Высокий приоритет',
                color: '#7ddc8a'
            },
            'C': {
                text: 'Умеренный приоритет',
                color: '#f3e26d'
            },
            'D': {
                text: 'Низкий приоритет',
                color: '#19b5f1'
            }
        };

        const importance = importanceMap[task.importance_level] || {
            text: 'Unknown',
            color: '#6c757d'
        };
        importanceBadge.textContent = importance.text;
        importanceBadge.style.background = importance.color;
        importanceBadge.style.color = task.importance_level === 'C' ? '#4a3f00' : '#fff';
        importanceBadge.style.padding = '4px 12px';
        importanceBadge.style.borderRadius = '12px';
        importanceBadge.style.fontSize = '12px';
        importanceBadge.style.fontWeight = '600';

        // Показываем модальное окно
        document.getElementById("modal").style.display = "block";
        document.getElementById("modalOverlay").style.display = "block";
        document.body.style.overflow = "hidden"; // Блокируем скролл

    } catch (error) {
        console.error("Error loading task details:", error);
        alert("Failed to load task details");
    }
}

/* ---------- Закрытие модального окна ---------- */
function closeModal() {
    document.getElementById("modal").style.display = "none";
    document.getElementById("modalOverlay").style.display = "none";
    document.body.style.overflow = "auto"; // Возвращаем скролл
}

/* ---------- Вспомогательные функции ---------- */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function logout() {
    // Удаляем токен и перенаправляем
    localStorage.removeItem('access_token');
    window.location.href = '/auth/login-page';
}

// Закрытие модального окна при клике вне его/Escape button
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' &&
        document.getElementById("modal").style.display === "block") {
        closeModal();
    }
});

// Загружаем задачи при загрузке страницы
document.addEventListener('DOMContentLoaded', loadTasks);
