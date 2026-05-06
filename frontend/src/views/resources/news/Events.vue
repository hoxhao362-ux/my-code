<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'resources-news-events'"
      :logout="userStore.logout"
    />
    <h1>{{ $t('news.events.title') }}</h1>
    
    <div class="timeline">
      <div v-for="event in events" :key="event.id" class="event-item">
        <div class="event-date">
          <span class="day">{{ event.day }}</span>
          <span class="month">{{ event.month }}</span>
        </div>
        <div class="event-card">
          <h2 class="event-title">{{ event.title }}</h2>
          <div class="event-meta">
            <span class="location">📍 {{ event.location }}</span>
            <span class="time">🕒 {{ event.time }}</span>
          </div>
          <div class="event-actions">
            <button class="btn-primary" @click="handleAction(event)">{{ event.type === 'upcoming' ? $t('news.events.register') : $t('news.events.watchReplay') }}</button>
            <a href="#" class="add-calendar" @click.prevent="addToCalendar(event)">{{ $t('news.events.addToCalendar') }}</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '../../../stores/user'
import { useToastStore } from '../../../stores/toast'
import Navigation from '../../../components/Navigation.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const userStore = useUserStore()
const toastStore = useToastStore()
const user = computed(() => userStore.user)

// TODO: In a real app, fetch these from an API (/api/events)
const events = computed(() => [
  {
    id: 1,
    title: "The Future of Global Health: Annual Conference",
    day: "15",
    month: "MAR",
    year: "2026",
    time: "09:00 - 17:00 GMT",
    location: "London, UK (Hybrid)",
    type: "upcoming",
    description: "Join us for the annual gathering of global health leaders."
  },
  {
    id: 2,
    title: "Webinar: Writing Effective Abstracts",
    day: "02",
    month: "APR",
    year: "2026",
    time: "14:00 - 15:30 GMT",
    location: "Online Zoom",
    type: "upcoming",
    description: "Learn how to summarize your research effectively."
  },
  {
    id: 3,
    title: "2025 Retrospective Symposium",
    day: "10",
    month: "JAN",
    year: "2026",
    time: "10:00 - 12:00 GMT",
    location: "Online",
    type: "past",
    description: "Looking back at the major medical breakthroughs of 2025."
  }
])

const handleAction = (event) => {
  if (event.type === 'upcoming') {
<<<<<<< HEAD
    toastStore.add({ message: `Registration for "${event.title}" opened.`, type: 'success' })
  } else {
    toastStore.add({ message: `Opening replay for "${event.title}"...`, type: 'info' })
=======
    toastStore.add({ message: t('news.events.toastRegister', { title: event.title }), type: 'success' })
  } else {
    toastStore.add({ message: t('news.events.toastReplay', { title: event.title }), type: 'info' })
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
  }
}

const addToCalendar = (event) => {
  // Simple ICS generation
  const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
<<<<<<< HEAD
PRODID:-//Journal Platform//Events//EN
BEGIN:VEVENT
UID:${event.id}@journalplatform.com
=======
PRODID:-//Peerex Peer//Events//EN
BEGIN:VEVENT
UID:${event.id}@peerexpeer.com
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
DTSTAMP:${new Date().toISOString().replace(/[-:]/g, '').split('.')[0]}Z
DTSTART:${event.year}03${event.day}T090000Z
SUMMARY:${event.title}
DESCRIPTION:${event.description}
LOCATION:${event.location}
END:VEVENT
END:VCALENDAR`

  const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' })
  const link = document.createElement('a')
  link.href = window.URL.createObjectURL(blob)
  link.setAttribute('download', 'event.ics')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
.page-container {
  max-width: 800px;
  margin: 80px auto 0;
  padding: 40px 24px;
}

h1 {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 40px;
}

.timeline {
  position: relative;
  padding-left: 20px;
  border-left: 2px solid #0056B3;
}

.event-item {
  position: relative;
  margin-bottom: 40px;
  padding-left: 30px;
  display: flex;
  gap: 24px;
}

.event-item::before {
  content: '';
  position: absolute;
  left: -9px;
  top: 0;
  width: 16px;
  height: 16px;
  background: #0056B3;
  border-radius: 50%;
  border: 4px solid white;
}

.event-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
  padding-top: 4px;
}

.day {
  font-size: 24px;
  font-weight: bold;
  color: #0056B3;
}

.month {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.event-card {
  flex-grow: 1;
  background: white;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.event-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 12px;
}

.event-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}

.event-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-primary {
  background-color: #333;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary:hover {
  background-color: #000;
}

.add-calendar {
  font-size: 12px;
  color: #999;
  text-decoration: none;
}

.add-calendar:hover {
  color: #0056B3;
  text-decoration: underline;
}

@media (max-width: 600px) {
  .event-item {
    flex-direction: column;
    gap: 10px;
  }
  .event-date {
    align-items: flex-start;
    flex-direction: row;
    gap: 8px;
  }
}
</style>
