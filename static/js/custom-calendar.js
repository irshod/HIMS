// Extend dayjs with isBetween plugin
dayjs.extend(window.dayjs_plugin_isBetween);

document.addEventListener("DOMContentLoaded", function () {
    const dayLabel = document.getElementById('dayLabel');
    const hoursContainer = document.getElementById('hoursContainer');
    const departmentFilter = document.getElementById('departmentFilter');
    const doctorFilter = document.getElementById('doctorFilter');
    let currentDate = dayjs();  // Default to today's date

    function fetchAppointments(date) {
        const formattedDate = date.format('YYYY-MM-DD');
        const departmentId = departmentFilter.value;
        const doctorId = doctorFilter.value;
        let url = `/appointments/events/?date=${formattedDate}`;
        if (departmentId) url += `&department=${departmentId}`;
        if (doctorId) url += `&doctor=${doctorId}`;
        
        fetch(url)
            .then(response => response.json())
            .then(events => {
                renderDailySchedule(date, events);
            })
            .catch(error => console.error("Error fetching appointments:", error));
    }

    function renderDailySchedule(date, events) {
        hoursContainer.innerHTML = '';
        dayLabel.textContent = date.format('MMMM D, YYYY');
        for (let hour = 8; hour <= 17; hour++) {
            const hourStart = date.hour(hour).minute(0).second(0);
            const hourLabel = hourStart.format('HH:mm') + ' - ' + hourStart.add(59, 'minutes').format('HH:mm');
            const hourCell = document.createElement('div');
            hourCell.classList.add('col-12', 'calendar-hour');
            hourCell.innerHTML = `<strong>${hourLabel}</strong>`;
            const filteredEvents = events.filter(event => dayjs(event.start).isBetween(hourStart, hourStart.add(59, 'minutes'), 'minute', '[)'));
            if (filteredEvents.length > 0) {
                filteredEvents.forEach(event => {
                    const eventEl = document.createElement('div');
                    eventEl.classList.add('event');
                    eventEl.textContent = `${event.title} - ${event.extendedProps.department} - ${event.extendedProps.type}`;
                    hourCell.appendChild(eventEl);
                });
            } else {
                const emptySlot = document.createElement('div');
                emptySlot.classList.add('text-muted');
                emptySlot.textContent = "No appointments";
                hourCell.appendChild(emptySlot);
            }
            hoursContainer.appendChild(hourCell);
        }
    }

    departmentFilter.addEventListener("change", () => fetchAppointments(currentDate));
    doctorFilter.addEventListener("change", () => fetchAppointments(currentDate));

    document.getElementById('prevDay').addEventListener('click', () => {
        currentDate = currentDate.subtract(1, 'day');
        fetchAppointments(currentDate);
    });
    
    document.getElementById('nextDay').addEventListener('click', () => {
        currentDate = currentDate.add(1, 'day');
        fetchAppointments(currentDate);
    });

    fetchAppointments(currentDate);  // Initial fetch
});
