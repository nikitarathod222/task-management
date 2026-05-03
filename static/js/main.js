// Auto-hide alerts after 3 seconds
setTimeout(() => {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => alert.style.display = 'none');
}, 3000);


// Confirm before deleting (future use)
function confirmAction(msg) {
    return confirm(msg);
}
const tasks = document.querySelectorAll('.task-card');
const columns = document.querySelectorAll('.kanban-column');

tasks.forEach(task => {
    task.addEventListener('dragstart', () => {
        task.classList.add('dragging');
    });

    task.addEventListener('dragend', () => {
        task.classList.remove('dragging');
    });
});

columns.forEach(column => {
    column.addEventListener('dragover', e => {
        e.preventDefault();
        const dragging = document.querySelector('.dragging');
        column.appendChild(dragging);
    });

    column.addEventListener('drop', () => {
        const task = column.querySelector('.dragging');
        const taskId = task.dataset.id;
        const newStatus = column.dataset.status;

        // SEND TO SERVER
        fetch('/update_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `task_id=${taskId}&status=${newStatus}`
        });
    });
});
