// -------------------- REGISTER --------------------
document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = {
        username: form.username.value,
        email: form.email.value,
        password: form.password.value
    };
    const res = await fetch('http://127.0.0.1:5000/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    const result = await res.json();
    alert(result.message || 'Registered!');
    if(res.ok) window.location.href = 'login.html';
});

// -------------------- LOGIN --------------------
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = {
        email: form.email.value,
        password: form.password.value
    };
    const res = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    const result = await res.json();
    if (result.access_token) {
        localStorage.setItem('token', result.access_token);
        window.location.href = 'tasks.html';
    } else {
        alert(result.message || 'Login failed');
    }
});

// -------------------- TASKS --------------------
const token = localStorage.getItem('token');
if(token){
    async function loadTasks(){
        const res = await fetch('http://127.0.0.1:5000/tasks', {
            headers: { 'Authorization': 'Bearer ' + token }
        });
        const tasks = await res.json();
        const list = document.getElementById('taskList');
        if(!list) return;
        list.innerHTML = '';
        tasks.forEach(t => {
            const li = document.createElement('li');
            li.textContent = `${t.title} [${t.status}]`;
            list.appendChild(li);
        });
    }
    loadTasks();

    document.getElementById('taskForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = e.target.title.value;
        await fetch('http://127.0.0.1:5000/tasks', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({title})
        });
        e.target.title.value = '';
        loadTasks();
    });

    document.getElementById('logoutBtn')?.addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    });
}
